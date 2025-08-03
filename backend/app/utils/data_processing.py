import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple
import os
from datetime import datetime
import json

def detect_column_types(df: pd.DataFrame) -> Dict[str, str]:
    """Detect the data type of each column."""
    column_types = {}
    
    for column in df.columns:
        # Check if it's numeric
        if pd.api.types.is_numeric_dtype(df[column]):
            if df[column].dtype in ['int64', 'int32']:
                column_types[column] = 'integer'
            else:
                column_types[column] = 'float'
        # Check if it's datetime
        elif pd.api.types.is_datetime64_any_dtype(df[column]):
            column_types[column] = 'datetime'
        # Check if it's categorical (low cardinality)
        elif df[column].nunique() < min(50, len(df) * 0.1):
            column_types[column] = 'categorical'
        # Default to string
        else:
            column_types[column] = 'string'
    
    return column_types

def get_column_info(df: pd.DataFrame) -> Dict[str, Any]:
    """Get comprehensive information about each column."""
    column_info = {}
    
    for column in df.columns:
        info = {
            'type': detect_column_types(df)[column],
            'missing_count': df[column].isnull().sum(),
            'missing_percentage': (df[column].isnull().sum() / len(df)) * 100,
            'unique_count': df[column].nunique(),
            'unique_percentage': (df[column].nunique() / len(df)) * 100
        }
        
        # Add type-specific information
        if info['type'] in ['integer', 'float']:
            info.update({
                'min': float(df[column].min()) if not df[column].isnull().all() else None,
                'max': float(df[column].max()) if not df[column].isnull().all() else None,
                'mean': float(df[column].mean()) if not df[column].isnull().all() else None,
                'std': float(df[column].std()) if not df[column].isnull().all() else None
            })
        elif info['type'] == 'categorical':
            value_counts = df[column].value_counts()
            info.update({
                'top_values': value_counts.head(5).to_dict(),
                'value_counts': value_counts.to_dict()
            })
        
        column_info[column] = info
    
    return column_info

def clean_dataframe(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Clean the dataframe and return cleaning report."""
    original_shape = df.shape
    cleaning_report = {
        'original_shape': original_shape,
        'missing_values': {},
        'outliers': {},
        'duplicates_removed': 0,
        'columns_processed': len(df.columns)
    }
    
    # Remove duplicates
    initial_rows = len(df)
    df = df.drop_duplicates()
    cleaning_report['duplicates_removed'] = initial_rows - len(df)
    
    # Handle missing values
    for column in df.columns:
        missing_count = df[column].isnull().sum()
        if missing_count > 0:
            cleaning_report['missing_values'][column] = missing_count
            
            # Fill missing values based on column type
            if df[column].dtype in ['int64', 'float64']:
                # For numeric columns, fill with median
                df[column] = df[column].fillna(df[column].median())
            else:
                # For categorical/string columns, fill with mode
                mode_value = df[column].mode()
                if not mode_value.empty:
                    df[column] = df[column].fillna(mode_value[0])
                else:
                    df[column] = df[column].fillna('Unknown')
    
    # Detect and handle outliers for numeric columns
    for column in df.columns:
        if df[column].dtype in ['int64', 'float64']:
            Q1 = df[column].quantile(0.25)
            Q3 = df[column].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outliers = df[(df[column] < lower_bound) | (df[column] > upper_bound)]
            if len(outliers) > 0:
                cleaning_report['outliers'][column] = len(outliers)
                # Cap outliers instead of removing them
                df[column] = df[column].clip(lower=lower_bound, upper=upper_bound)
    
    cleaning_report['final_shape'] = df.shape
    cleaning_report['rows_removed'] = original_shape[0] - df.shape[0]
    
    return df, cleaning_report

def save_dataframe_info(df: pd.DataFrame, file_path: str, user_id: int) -> Dict[str, Any]:
    """Save dataframe information and return metadata."""
    # Clean the data
    df_cleaned, cleaning_report = clean_dataframe(df)
    
    # Get column information
    column_info = get_column_info(df_cleaned)
    
    # Create metadata
    metadata = {
        'user_id': user_id,
        'row_count': len(df_cleaned),
        'column_count': len(df_cleaned.columns),
        'column_info': column_info,
        'cleaning_report': cleaning_report,
        'uploaded_at': datetime.now().isoformat(),
        'file_size': os.path.getsize(file_path) if os.path.exists(file_path) else 0
    }
    
    return metadata

def validate_csv_file(file_path: str) -> Tuple[bool, str]:
    """Validate if the file is a valid CSV."""
    try:
        # Try to read the first few rows
        df = pd.read_csv(file_path, nrows=5)
        
        # Check if dataframe is not empty
        if df.empty:
            return False, "CSV file is empty"
        
        # Check if there are any columns
        if len(df.columns) == 0:
            return False, "CSV file has no columns"
        
        return True, "Valid CSV file"
    
    except Exception as e:
        return False, f"Invalid CSV file: {str(e)}"

def get_dataframe_preview(df: pd.DataFrame, max_rows: int = 10) -> Dict[str, Any]:
    """Get a preview of the dataframe for display."""
    preview = {
        'head': df.head(max_rows).to_dict('records'),
        'tail': df.tail(max_rows).to_dict('records'),
        'shape': df.shape,
        'columns': list(df.columns),
        'dtypes': df.dtypes.to_dict(),
        'info': get_column_info(df)
    }
    
    return preview 