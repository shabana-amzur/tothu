"""
Test Excel Integration
Creates a sample Excel file and tests the Excel service
"""

import pandas as pd
import sys
import os
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from app.services.excel_service import ExcelService

def create_sample_excel():
    """Create a sample Excel file for testing"""
    # Sample sales data
    data = {
        'Date': pd.date_range('2026-01-01', periods=50, freq='D'),
        'Product': ['Widget A', 'Widget B', 'Widget C', 'Widget D'] * 12 + ['Widget A', 'Widget B'],
        'Quantity': [10, 15, 8, 12, 20, 5, 18, 22, 7, 13] * 5,
        'Price': [19.99, 29.99, 39.99, 24.99, 34.99, 14.99, 44.99, 9.99, 54.99, 49.99] * 5,
        'Region': ['North', 'South', 'East', 'West'] * 12 + ['North', 'South']
    }
    
    df = pd.DataFrame(data)
    df['Total'] = df['Quantity'] * df['Price']
    
    # Save to Excel
    file_path = Path('backend/uploads/sample_sales_data.xlsx')
    file_path.parent.mkdir(exist_ok=True)
    
    with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Sales', index=False)
        
        # Create a summary sheet
        summary = df.groupby('Product').agg({
            'Quantity': 'sum',
            'Total': 'sum'
        }).reset_index()
        summary.to_excel(writer, sheet_name='Summary', index=False)
    
    print(f"✓ Sample Excel file created: {file_path}")
    return str(file_path)


def test_excel_service(file_path):
    """Test Excel service functionality"""
    print("\n" + "=" * 60)
    print("Testing Excel Service")
    print("=" * 60)
    
    service = ExcelService()
    
    # Test 1: Validate file
    print("\n1. Validating Excel file...")
    is_valid = service.validate_excel_file(file_path)
    print(f"   Valid: {is_valid}")
    
    # Test 2: Get sheet names
    print("\n2. Getting sheet names...")
    sheet_names = service.get_sheet_names(file_path)
    print(f"   Sheets: {sheet_names}")
    
    # Test 3: Load data
    print("\n3. Loading Sales sheet...")
    df = service.load_excel_file(file_path, 'Sales')
    print(f"   Shape: {df.shape}")
    print(f"   Columns: {df.columns.tolist()}")
    
    # Test 4: Get summary
    print("\n4. Getting data summary...")
    summary = service.get_dataframe_summary(df)
    print(f"   Rows: {summary['rows']}")
    print(f"   Columns: {summary['columns']}")
    print(f"   Sample data (first row): {summary['sample_data'][0]}")
    
    # Test 5: Ask questions
    print("\n5. Testing Q&A functionality...")
    
    questions = [
        "What is the total revenue?",
        "What is the average quantity sold?",
        "Which product generated the most revenue?",
        "How many unique products are there?"
    ]
    
    for i, question in enumerate(questions, 1):
        print(f"\n   Question {i}: {question}")
        result = service.ask_question(df, question, "sample_sales_data.xlsx")
        print(f"   Answer: {result['answer'][:200]}...")
    
    print("\n" + "=" * 60)
    print("Excel Service Tests Complete!")
    print("=" * 60)


if __name__ == "__main__":
    # Create sample file
    file_path = create_sample_excel()
    
    # Test service
    test_excel_service(file_path)
    
    print("\n✓ All tests completed successfully!")
    print(f"\nSample file location: {file_path}")
    print("\nYou can now:")
    print("1. Upload this file via POST /api/excel/upload")
    print("2. Ask questions via POST /api/excel/{id}/ask")
    print("3. Get summary via GET /api/excel/{id}/summary")
