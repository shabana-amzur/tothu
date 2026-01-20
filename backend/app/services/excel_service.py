"""
Excel and Google Sheets Service
Handles Excel file processing, data extraction, and Q&A
"""

import os
import pandas as pd
from typing import Dict, List, Any, Optional
import logging
from pathlib import Path
import json

from langchain_google_genai import ChatGoogleGenerativeAI
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.database import Document

logger = logging.getLogger(__name__)
settings = get_settings()


class ExcelService:
    """Service for processing Excel files and answering questions"""
    
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model=settings.GEMINI_MODEL,
            google_api_key=settings.GOOGLE_GEMINI_API_KEY,
            temperature=settings.GEMINI_TEMPERATURE
        )
    
    def load_excel_file(self, file_path: str, sheet_name: Optional[str] = None) -> pd.DataFrame:
        """Load Excel file into pandas DataFrame"""
        try:
            file_ext = Path(file_path).suffix.lower()
            
            if file_ext == '.xlsx' or file_ext == '.xlsm':
                # Modern Excel format
                if sheet_name:
                    df = pd.read_excel(file_path, sheet_name=sheet_name, engine='openpyxl')
                else:
                    df = pd.read_excel(file_path, engine='openpyxl')
            elif file_ext == '.xls':
                # Legacy Excel format
                if sheet_name:
                    df = pd.read_excel(file_path, sheet_name=sheet_name, engine='xlrd')
                else:
                    df = pd.read_excel(file_path, engine='xlrd')
            elif file_ext == '.csv':
                df = pd.read_csv(file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_ext}")
            
            logger.info(f"Loaded Excel file: {file_path} with shape {df.shape}")
            return df
        
        except Exception as e:
            logger.error(f"Error loading Excel file {file_path}: {str(e)}")
            raise
    
    def get_sheet_names(self, file_path: str) -> List[str]:
        """Get list of sheet names in Excel file"""
        try:
            file_ext = Path(file_path).suffix.lower()
            
            if file_ext in ['.xlsx', '.xlsm']:
                excel_file = pd.ExcelFile(file_path, engine='openpyxl')
            elif file_ext == '.xls':
                excel_file = pd.ExcelFile(file_path, engine='xlrd')
            else:
                return []
            
            return excel_file.sheet_names
        
        except Exception as e:
            logger.error(f"Error getting sheet names: {str(e)}")
            return []
    
    def get_dataframe_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get summary information about the DataFrame"""
        try:
            summary = {
                "rows": len(df),
                "columns": len(df.columns),
                "column_names": df.columns.tolist(),
                "column_types": df.dtypes.astype(str).to_dict(),
                "sample_data": df.head(5).to_dict(orient='records'),
                "missing_values": df.isnull().sum().to_dict(),
                "numeric_summary": {}
            }
            
            # Add summary statistics for numeric columns
            numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
            if len(numeric_cols) > 0:
                summary["numeric_summary"] = df[numeric_cols].describe().to_dict()
            
            return summary
        
        except Exception as e:
            logger.error(f"Error creating DataFrame summary: {str(e)}")
            return {}
    
    def ask_question(self, df: pd.DataFrame, question: str, file_name: str = "data") -> Dict[str, Any]:
        """
        Ask a question about the DataFrame using LLM with data context
        """
        try:
            # Get DataFrame summary
            summary = self.get_dataframe_summary(df)
            
            # Create context with data information
            context = f"""
You are analyzing a dataset from the file: {file_name}

Dataset Information:
- Total Rows: {len(df)}
- Total Columns: {len(df.columns)}
- Column Names and Types: {json.dumps(summary['column_types'], indent=2)}

Sample Data (first 5 rows):
{df.head(5).to_string()}

Statistics for Numeric Columns:
{df.describe().to_string() if len(df.select_dtypes(include=['int64', 'float64']).columns) > 0 else 'No numeric columns'}

Missing Values:
{json.dumps(summary['missing_values'], indent=2)}
"""
            
            # Add specific calculations if needed
            prompt = f"""{context}

User Question: {question}

Please analyze the data and provide a clear, accurate answer to the question.
If calculations are needed, show your work.
If the question requires specific data points, reference them.
Format numbers appropriately (currency, percentages, etc.).
"""
            
            # Get response from LLM
            response = self.llm.invoke(prompt)
            
            result = {
                "question": question,
                "answer": response.content,
                "file_name": file_name,
                "data_shape": {"rows": len(df), "columns": len(df.columns)}
            }
            
            logger.info(f"Question answered for {file_name}: {question}")
            return result
        
        except Exception as e:
            logger.error(f"Error answering question: {str(e)}")
            return {
                "question": question,
                "answer": f"Error processing question: {str(e)}",
                "error": True
            }
    
    def extract_data_to_text(self, df: pd.DataFrame, max_rows: int = 100) -> str:
        """
        Convert DataFrame to text format for embedding/RAG
        """
        try:
            text_parts = []
            
            # Add column information
            text_parts.append("Dataset Columns:")
            for col in df.columns:
                dtype = df[col].dtype
                text_parts.append(f"- {col} ({dtype})")
            
            text_parts.append("\nDataset Summary:")
            text_parts.append(f"Total rows: {len(df)}")
            text_parts.append(f"Total columns: {len(df.columns)}")
            
            # Add sample data
            text_parts.append("\nSample Data (first few rows):")
            sample_df = df.head(min(max_rows, len(df)))
            text_parts.append(sample_df.to_string())
            
            # Add statistics for numeric columns
            numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
            if len(numeric_cols) > 0:
                text_parts.append("\nNumeric Column Statistics:")
                text_parts.append(df[numeric_cols].describe().to_string())
            
            return "\n".join(text_parts)
        
        except Exception as e:
            logger.error(f"Error converting DataFrame to text: {str(e)}")
            return f"Error: {str(e)}"
    
    def validate_excel_file(self, file_path: str) -> bool:
        """Validate if file is a valid Excel/CSV file"""
        try:
            file_ext = Path(file_path).suffix.lower()
            if file_ext not in ['.xlsx', '.xls', '.xlsm', '.csv']:
                return False
            
            # Try to load the file
            df = self.load_excel_file(file_path)
            return df is not None and len(df) > 0
        
        except Exception:
            return False


def get_excel_service() -> ExcelService:
    """Get ExcelService instance"""
    return ExcelService()
