"""
NL2SQL Service
Converts natural language questions to SQL queries using Google Gemini via LangChain
"""

import os
import logging
from typing import Dict, Any, List, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from sqlalchemy import create_engine, inspect, MetaData, Table, text
from sqlalchemy.exc import SQLAlchemyError
from app.config import get_settings
from app.services.sql_validator import SQLValidator

logger = logging.getLogger(__name__)
settings = get_settings()


class NL2SQLService:
    """Service for converting natural language to SQL queries"""
    
    def __init__(self):
        """Initialize NL2SQL service with Gemini and database connection"""
        self.llm = ChatGoogleGenerativeAI(
            model=settings.GEMINI_MODEL,
            google_api_key=settings.GOOGLE_GEMINI_API_KEY,
            temperature=0.0  # Use 0 for deterministic SQL generation
        )
        self.validator = SQLValidator()
        
        # Create separate read-only engine for NL2SQL queries
        # Use Supabase PostgreSQL if configured
        nl2sql_db_url = os.getenv('NL2SQL_DATABASE_URL', settings.DATABASE_URL)
        self.engine = create_engine(nl2sql_db_url, pool_pre_ping=True)
        
        logger.info(f"NL2SQL Service initialized with database")
    
    def get_database_schema(self) -> str:
        """
        Introspect database and return schema information
        
        Returns:
            String representation of database schema
        """
        try:
            inspector = inspect(self.engine)
            schema_info = []
            
            # Get all table names
            table_names = inspector.get_table_names()
            
            schema_info.append(f"Database has {len(table_names)} tables:\n")
            
            for table_name in table_names:
                schema_info.append(f"\nTable: {table_name}")
                
                # Get columns for each table
                columns = inspector.get_columns(table_name)
                schema_info.append("Columns:")
                for col in columns:
                    col_type = str(col['type'])
                    nullable = "NULL" if col['nullable'] else "NOT NULL"
                    schema_info.append(f"  - {col['name']}: {col_type} {nullable}")
                
                # Get primary keys
                pk = inspector.get_pk_constraint(table_name)
                if pk and pk['constrained_columns']:
                    schema_info.append(f"Primary Key: {', '.join(pk['constrained_columns'])}")
                
                # Get foreign keys
                fks = inspector.get_foreign_keys(table_name)
                if fks:
                    schema_info.append("Foreign Keys:")
                    for fk in fks:
                        schema_info.append(
                            f"  - {', '.join(fk['constrained_columns'])} -> "
                            f"{fk['referred_table']}.{', '.join(fk['referred_columns'])}"
                        )
            
            return "\n".join(schema_info)
        
        except Exception as e:
            logger.error(f"Error getting database schema: {str(e)}")
            return "Error retrieving database schema"
    
    def generate_sql(self, question: str, schema: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate SQL query from natural language question
        
        Args:
            question: Natural language question
            schema: Optional database schema (will be fetched if not provided)
            
        Returns:
            Dictionary with sql query and metadata
        """
        try:
            # Get schema if not provided
            if schema is None:
                schema = self.get_database_schema()
            
            # Create prompt for SQL generation
            prompt_template = PromptTemplate(
                input_variables=["question", "schema"],
                template="""You are a SQL expert. Convert the following natural language question into a SQL query.

Database Schema:
{schema}

IMPORTANT RULES:
1. Generate SELECT, INSERT, UPDATE, or DELETE queries as appropriate for the question
2. Return ONLY the SQL query, no explanations or markdown
3. Do not include semicolons
4. Use proper SQL syntax for PostgreSQL
5. Use table and column names exactly as shown in the schema
6. Do NOT generate DROP, ALTER, CREATE, TRUNCATE, or other DDL statements
7. For write operations (INSERT/UPDATE/DELETE), be precise and use WHERE clauses when appropriate
8. If the question cannot be answered with the given schema, return: "ERROR: Cannot generate query from this question"

Question: {question}

SQL Query:"""
            )
            
            # Format prompt
            formatted_prompt = prompt_template.format(question=question, schema=schema)
            
            # Generate SQL using Gemini
            logger.info(f"Generating SQL for question: {question}")
            response = self.llm.invoke(formatted_prompt)
            
            # Extract SQL from response
            sql = response.content.strip()
            
            # Remove markdown code blocks if present
            if sql.startswith('```sql'):
                sql = sql[6:]
            elif sql.startswith('```'):
                sql = sql[3:]
            if sql.endswith('```'):
                sql = sql[:-3]
            
            sql = sql.strip()
            
            # Check for error response
            if sql.startswith('ERROR:'):
                logger.warning(f"Could not generate SQL: {sql}")
                return {
                    'success': False,
                    'error': sql,
                    'sql': None
                }
            
            # Validate the generated SQL
            is_safe, sanitized_sql, error = self.validator.validate_and_sanitize(sql)
            
            if not is_safe:
                logger.warning(f"Generated unsafe SQL: {sql}")
                return {
                    'success': False,
                    'error': f"Generated query failed safety validation: {error}",
                    'sql': sql
                }
            
            logger.info(f"Successfully generated SQL: {sanitized_sql}")
            return {
                'success': True,
                'sql': sanitized_sql,
                'original_question': question
            }
        
        except Exception as e:
            logger.error(f"Error generating SQL: {str(e)}")
            return {
                'success': False,
                'error': f"Failed to generate SQL: {str(e)}",
                'sql': None
            }
    
    def execute_sql(self, sql: str) -> Dict[str, Any]:
        """
        Execute a SQL query and return results
        
        Args:
            sql: SQL query to execute
            
        Returns:
            Dictionary with query results or error
        """
        try:
            # Final validation before execution
            is_safe, sanitized_sql, error = self.validator.validate_and_sanitize(sql)
            
            if not is_safe:
                logger.warning(f"Attempted to execute unsafe SQL: {sql}")
                return {
                    'success': False,
                    'error': f"Query failed safety validation: {error}",
                    'data': None
                }
            
            # Execute query
            logger.info(f"Executing SQL: {sanitized_sql}")
            with self.engine.connect() as connection:
                # Check if it's a write operation
                query_type = self.validator.get_query_type(sanitized_sql)
                
                result = connection.execute(text(sanitized_sql))
                
                # For write operations, commit and return affected rows
                if query_type in ['INSERT', 'UPDATE', 'DELETE']:
                    connection.commit()
                    rows_affected = result.rowcount
                    logger.info(f"{query_type} query executed successfully, {rows_affected} rows affected")
                    return {
                        'success': True,
                        'data': [],
                        'row_count': 0,
                        'columns': [],
                        'rows_affected': rows_affected,
                        'query_type': query_type,
                        'message': f"{query_type} successful: {rows_affected} row(s) affected"
                    }
                
                # For SELECT, fetch and return results
                rows = result.fetchall()
                columns = result.keys()
                
                # Convert to list of dictionaries
                data = []
                for row in rows:
                    data.append(dict(zip(columns, row)))
                
                logger.info(f"Query executed successfully, returned {len(data)} rows")
                return {
                    'success': True,
                    'data': data,
                    'row_count': len(data),
                    'columns': list(columns),
                    'rows_affected': 0,
                    'query_type': 'SELECT'
                }
        
        except SQLAlchemyError as e:
            logger.error(f"Database error executing SQL: {str(e)}")
            return {
                'success': False,
                'error': f"Database error: {str(e)}",
                'data': None
            }
        
        except Exception as e:
            logger.error(f"Error executing SQL: {str(e)}")
            return {
                'success': False,
                'error': f"Execution error: {str(e)}",
                'data': None
            }
    
    def process_nl_query(self, question: str) -> Dict[str, Any]:
        """
        Process a natural language query end-to-end
        
        Args:
            question: Natural language question
            
        Returns:
            Dictionary with SQL, results, and metadata
        """
        # Step 1: Generate SQL
        sql_result = self.generate_sql(question)
        
        if not sql_result['success']:
            return {
                'success': False,
                'question': question,
                'sql': sql_result.get('sql'),
                'error': sql_result['error'],
                'data': None
            }
        
        sql = sql_result['sql']
        
        # Step 2: Execute SQL
        execution_result = self.execute_sql(sql)
        
        return {
            'success': execution_result['success'],
            'question': question,
            'sql': sql,
            'data': execution_result.get('data'),
            'row_count': execution_result.get('row_count'),
            'columns': execution_result.get('columns'),
            'error': execution_result.get('error')
        }


# Singleton instance
_nl2sql_service = None


def get_nl2sql_service() -> NL2SQLService:
    """Get or create NL2SQL service instance"""
    global _nl2sql_service
    if _nl2sql_service is None:
        _nl2sql_service = NL2SQLService()
    return _nl2sql_service
