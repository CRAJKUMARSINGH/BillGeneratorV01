
"""
DataFrame Safety Utilities for Bill Generator App
Fixes the ambiguous truth value errors by providing safe DataFrame operations
"""

import pandas as pd
from typing import Any, Union, Optional

class DataFrameSafetyUtils:
    """Utility class to handle DataFrame operations safely"""

    @staticmethod
    def is_valid_dataframe(data: Any) -> bool:
        """
        Safely check if data is a valid non-empty DataFrame
        Returns True only if data is a DataFrame with content
        """
        return (isinstance(data, pd.DataFrame) and 
                not data.empty and 
                len(data) > 0)

    @staticmethod
    def is_dataframe_or_data(data: Any) -> bool:
        """
        Check if data is either a valid DataFrame OR other valid data structure
        Safe replacement for ambiguous DataFrame boolean checks
        """
        if data is None:
            return False

        # If it's a DataFrame, check if it has content
        if isinstance(data, pd.DataFrame):
            return not data.empty and len(data) > 0

        # If it's a list or dict, check if it has content
        if isinstance(data, (list, dict)):
            return len(data) > 0

        # For other types, check truthiness safely
        return bool(data)

    @staticmethod
    def safe_dataframe_check(data: Any, check_content: bool = True) -> bool:
        """
        Comprehensive safe check for DataFrame existence and content

        Args:
            data: Data to check
            check_content: If True, also verify DataFrame has content

        Returns:
            bool: True if data passes all checks
        """
        if data is None:
            return False

        if not isinstance(data, pd.DataFrame):
            return False

        if check_content:
            return not data.empty and len(data) > 0

        return True

    @staticmethod
    def get_safe_dataframe(data: Any, default_columns: list = None) -> pd.DataFrame:
        """
        Safely convert data to DataFrame or return empty DataFrame

        Args:
            data: Data to convert
            default_columns: Columns for empty DataFrame

        Returns:
            pd.DataFrame: Valid DataFrame
        """
        if DataFrameSafetyUtils.is_valid_dataframe(data):
            return data

        if isinstance(data, (list, dict)):
            try:
                return pd.DataFrame(data)
            except:
                pass

        # Return empty DataFrame with specified columns
        if default_columns:
            return pd.DataFrame(columns=default_columns)

        return pd.DataFrame()

# Save the utility to a file
with open('/home/user/output/dataframe_safety_utils.py', 'w') as f:
    f.write(dataframe_safety_utils)

print("✅ Created DataFrame Safety Utilities")
