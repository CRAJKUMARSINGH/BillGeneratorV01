"""
Legacy data import module for BillGenerator.

This module provides functionality to import data from legacy systems
and older file formats, ensuring backward compatibility.
"""

import pandas as pd
import json
from pathlib import Path
from typing import Dict, List, Any
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def import_legacy_excel(file_path: str, format_version: str = "v1") -> Dict[str, Any]:
    """
    Import data from legacy Excel formats.
    
    Args:
        file_path (str): Path to the legacy Excel file
        format_version (str): Version of the legacy format ('v1', 'v2', etc.)
        
    Returns:
        Dict[str, Any]: Processed data ready for BillGenerator
    """
    try:
        # Read the Excel file
        df = pd.read_excel(file_path)
        
        # Apply format-specific transformations
        if format_version == "v1":
            processed_data = _process_v1_format(df)
        elif format_version == "v2":
            processed_data = _process_v2_format(df)
        else:
            # Default processing
            processed_data = _process_default_format(df)
        
        logger.info(f"Successfully imported legacy Excel file: {file_path}")
        return processed_data
    except Exception as e:
        logger.error(f"Error importing legacy Excel file {file_path}: {e}")
        raise

def _process_v1_format(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Process legacy v1 format Excel data.
    
    Args:
        df (pd.DataFrame): Raw data from Excel file
        
    Returns:
        Dict[str, Any]: Processed data
    """
    # Map legacy column names to current format
    column_mapping = {
        'Item No': 'item_no',
        'Description of Work': 'description',
        'Unit': 'unit',
        'Quantity': 'quantity',
        'Rate': 'rate',
        'Amount': 'amount'
    }
    
    # Rename columns
    df = df.rename(columns=column_mapping)
    
    # Ensure all required columns exist
    required_columns = ['item_no', 'description', 'unit', 'quantity', 'rate', 'amount']
    for col in required_columns:
        if col not in df.columns:
            df[col] = None
    
    # Convert data types
    df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce').fillna(0)
    df['rate'] = pd.to_numeric(df['rate'], errors='coerce').fillna(0)
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce').fillna(0)
    
    return {
        'data': df.to_dict('records'),
        'format_version': 'v1',
        'processed_date': pd.Timestamp.now().isoformat()
    }

def _process_v2_format(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Process legacy v2 format Excel data.
    
    Args:
        df (pd.DataFrame): Raw data from Excel file
        
    Returns:
        Dict[str, Any]: Processed data
    """
    # Map legacy column names to current format
    column_mapping = {
        'S.No': 'item_no',
        'Work Description': 'description',
        'Work Unit': 'unit',
        'Work Qty': 'quantity',
        'Work Rate': 'rate',
        'Work Amount': 'amount'
    }
    
    # Rename columns
    df = df.rename(columns=column_mapping)
    
    # Ensure all required columns exist
    required_columns = ['item_no', 'description', 'unit', 'quantity', 'rate', 'amount']
    for col in required_columns:
        if col not in df.columns:
            df[col] = None
    
    # Convert data types
    df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce').fillna(0)
    df['rate'] = pd.to_numeric(df['rate'], errors='coerce').fillna(0)
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce').fillna(0)
    
    return {
        'data': df.to_dict('records'),
        'format_version': 'v2',
        'processed_date': pd.Timestamp.now().isoformat()
    }

def _process_default_format(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Process default format Excel data.
    
    Args:
        df (pd.DataFrame): Raw data from Excel file
        
    Returns:
        Dict[str, Any]: Processed data
    """
    # Try to identify columns by common names
    possible_mappings = {
        'item_no': ['Item No', 'S.No', 'Item Number', 'No'],
        'description': ['Description', 'Description of Work', 'Work Description', 'Item Description'],
        'unit': ['Unit', 'Work Unit', 'Units'],
        'quantity': ['Quantity', 'Qty', 'Work Qty', 'Quantities'],
        'rate': ['Rate', 'Work Rate', 'Unit Rate'],
        'amount': ['Amount', 'Work Amount', 'Total Amount']
    }
    
    # Apply mappings
    for standard_col, possible_names in possible_mappings.items():
        for name in possible_names:
            if name in df.columns:
                df = df.rename(columns={name: standard_col})
                break
        if standard_col not in df.columns:
            df[standard_col] = None
    
    # Convert data types
    numeric_columns = ['quantity', 'rate', 'amount']
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    return {
        'data': df.to_dict('records'),
        'format_version': 'auto_detected',
        'processed_date': pd.Timestamp.now().isoformat()
    }

def import_legacy_csv(file_path: str) -> Dict[str, Any]:
    """
    Import data from legacy CSV formats.
    
    Args:
        file_path (str): Path to the legacy CSV file
        
    Returns:
        Dict[str, Any]: Processed data ready for BillGenerator
    """
    try:
        # Read the CSV file
        df = pd.read_csv(file_path)
        
        # Process using default format
        processed_data = _process_default_format(df)
        
        logger.info(f"Successfully imported legacy CSV file: {file_path}")
        return processed_data
    except Exception as e:
        logger.error(f"Error importing legacy CSV file {file_path}: {e}")
        raise

def import_legacy_json(file_path: str) -> Dict[str, Any]:
    """
    Import data from legacy JSON formats.
    
    Args:
        file_path (str): Path to the legacy JSON file
        
    Returns:
        Dict[str, Any]: Processed data ready for BillGenerator
    """
    try:
        # Read the JSON file
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Convert to DataFrame for processing
        if isinstance(data, list):
            df = pd.DataFrame(data)
        elif isinstance(data, dict) and 'data' in data:
            df = pd.DataFrame(data['data'])
        else:
            df = pd.DataFrame([data])
        
        # Process using default format
        processed_data = _process_default_format(df)
        
        logger.info(f"Successfully imported legacy JSON file: {file_path}")
        return processed_data
    except Exception as e:
        logger.error(f"Error importing legacy JSON file {file_path}: {e}")
        raise

def convert_legacy_data(input_file: str, output_file: str, file_type: str = 'excel', format_version: str = 'auto') -> bool:
    """
    Convert legacy data files to current format.
    
    Args:
        input_file (str): Path to the input legacy file
        output_file (str): Path to save the converted file
        file_type (str): Type of input file ('excel', 'csv', 'json')
        format_version (str): Version of the legacy format
        
    Returns:
        bool: True if conversion was successful, False otherwise
    """
    try:
        # Import the legacy data
        if file_type.lower() == 'excel':
            data = import_legacy_excel(input_file, format_version)
        elif file_type.lower() == 'csv':
            data = import_legacy_csv(input_file)
        elif file_type.lower() == 'json':
            data = import_legacy_json(input_file)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
        
        # Save in current format (JSON)
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Successfully converted {input_file} to {output_file}")
        return True
    except Exception as e:
        logger.error(f"Error converting legacy data: {e}")
        return False

# Example usage
if __name__ == "__main__":
    # Example of how to use the legacy import functions
    print("Legacy Import Module for BillGenerator")
    print("=====================================")
    print("Available functions:")
    print("- import_legacy_excel(file_path, format_version)")
    print("- import_legacy_csv(file_path)")
    print("- import_legacy_json(file_path)")
    print("- convert_legacy_data(input_file, output_file, file_type, format_version)")
# migration/legacy_import.py
"""
Simple legacy Excel importer which normalizes column names.
It produces a list of records suitable for feeding into the existing generation logic.
"""

import pandas as pd
from pathlib import Path

def import_legacy_excel(file_path):
    p = Path(file_path)
    df = pd.read_excel(p)
    df.columns = [c.strip() for c in df.columns]
    # basic normalization example
    mapping = {c: c.lower().replace(" ", "_") for c in df.columns}
    df = df.rename(columns=mapping)
    records = df.to_dict(orient="records")
    return records

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python migration/legacy_import.py <file.xlsx>")
    else:
        recs = import_legacy_excel(sys.argv[1])
        print(f"Imported {len(recs)} rows")
