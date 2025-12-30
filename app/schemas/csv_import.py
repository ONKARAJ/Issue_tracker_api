"""
Pydantic schemas for CSV import operations.

This module provides schemas for:
- CSV import results
- Error reporting for import operations
- Import statistics
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from uuid import UUID


class ImportError(BaseModel):
    """
    Schema for individual import errors.
    
    Attributes:
        row_number: CSV row number (1-indexed)
        field: Field name that caused the error
        value: Value that caused the error
        error: Error message
        raw_data: Raw row data for debugging
    """
    
    row_number: int = Field(description="CSV row number (1-indexed)")
    field: Optional[str] = Field(None, description="Field name that caused the error")
    value: Optional[str] = Field(None, description="Value that caused the error")
    error: str = Field(description="Error message")
    raw_data: Dict[str, str] = Field(description="Raw row data for debugging")


class CSVImportResponse(BaseModel):
    """
    Schema for CSV import responses.
    
    Attributes:
        created_count: Number of successfully created issues
        failed_count: Number of failed rows
        total_rows: Total number of rows processed
        errors: List of import errors
        message: Summary message
    """
    
    created_count: int = Field(description="Number of successfully created issues")
    failed_count: int = Field(description="Number of failed rows")
    total_rows: int = Field(description="Total number of rows processed")
    errors: List[ImportError] = Field(default=[], description="Import errors")
    message: str = Field(description="Import summary message")
