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
import re
# import gspread
# from oauth2client.service_account import ServiceAccountCredentials

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
    
    def is_google_sheets_url(self, url: str) -> bool:
        """Check if URL is a Google Sheets URL"""
        patterns = [
            r'docs\.google\.com/spreadsheets',
            r'drive\.google\.com.*spreadsheets'
        ]
        return any(re.search(pattern, url) for pattern in patterns)
    
    def extract_sheet_id(self, url: str) -> Optional[str]:
        """Extract Google Sheets ID from URL"""
        patterns = [
            r'/spreadsheets/d/([a-zA-Z0-9-_]+)',
            r'id=([a-zA-Z0-9-_]+)'
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    def load_google_sheet(self, url: str, sheet_name: Optional[str] = None) -> pd.DataFrame:
        """Load Google Sheet from URL into pandas DataFrame"""
        try:
            # Extract sheet ID
            sheet_id = self.extract_sheet_id(url)
            if not sheet_id:
                raise ValueError("Invalid Google Sheets URL")
            
            # Use public CSV export (no auth required for public sheets)
            if sheet_name:
                csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
            else:
                csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
            
            # Load from public URL
            df = pd.read_csv(csv_url)
            logger.info(f"Loaded Google Sheet: {sheet_id} with shape {df.shape}")
            return df
        
        except Exception as e:
            logger.error(f"Error loading Google Sheet {url}: {str(e)}")
            # Try alternative method
            try:
                # For public sheets, try direct export URL
                if '/edit' in url:
                    export_url = url.replace('/edit', '/export?format=csv')
                else:
                    export_url = f"{url}/export?format=csv"
                df = pd.read_csv(export_url)
                logger.info(f"Loaded Google Sheet via alternative method with shape {df.shape}")
                return df
            except Exception as e2:
                logger.error(f"Alternative method also failed: {str(e2)}")
                raise ValueError("Failed to load Google Sheet. Make sure the sheet is publicly accessible (Anyone with the link can view).")
    
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

ALL DATA (all {len(df)} rows):
{df.to_string()}

Statistics for Numeric Columns:
{df.describe().to_string() if len(df.select_dtypes(include=['int64', 'float64']).columns) > 0 else 'No numeric columns'}

Missing Values:
{json.dumps(summary['missing_values'], indent=2)}

Date Columns (if any):
{json.dumps({col: str(df[col].dtype) for col in df.columns if 'date' in str(df[col].dtype).lower() or 'datetime' in str(df[col].dtype).lower()}, indent=2)}
"""
            
            # Add specific calculations if needed
            prompt = f"""{context}

User Question: {question}

IMPORTANT INSTRUCTIONS:
1. Analyze the COMPLETE dataset provided above (all {len(df)} rows)
2. Give EXACT answers with specific values from the data
3. Be CONCISE - give direct answers without lengthy explanations
4. For simple questions (who/what/when/count), answer in 1-2 sentences maximum
5. For date questions, provide the exact date
6. For counting questions, provide just the number or name
7. Show specific data values only when necessary
8. DO NOT provide analysis unless explicitly asked
9. DO NOT explain the dataset structure unless asked
10. Answer ONLY what was asked - nothing more

Example good answers:
- "Who completed most assignments?" → "John Smith completed 15 assignments, the most in the dataset."
- "How many students?" → "There are 42 students."
- "What is the latest date?" → "2026-01-15"

Provide a BRIEF, DIRECT answer to the question.
"""
            
            # Get response from LLM
            response = self.llm.invoke(prompt)
            
            result = {
                "question": question,
                "answer": response.content,
                "file_name": file_name,
                "data_shape": {"rows": len(df), "columns": len(df.columns)},
                "error": False
            }
            
            logger.info(f"Question answered for {file_name}: {question}")
            return result
        
        except Exception as e:
            logger.error(f"Error answering question: {str(e)}")
            error_msg = str(e)
            
            # Check if it's a rate limit error
            if "429" in error_msg or "quota" in error_msg.lower():
                error_msg = "⚠️ Rate limit exceeded. Please wait a moment and try again, or check your API quota at https://ai.google.dev/gemini-api/docs/rate-limits"
            
            return {
                "question": question,
                "answer": error_msg,
                "file_name": file_name,
                "data_shape": {"rows": len(df), "columns": len(df.columns)},
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
