# SPDX-License-Identifier: MIT
"""Common schema with data validation."""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ListRequest(BaseModel):
    """
    Pagination and sorting parameters for list endpoints.

    Attributes:
        current: Current page number (1-based). Default: 1.
        page_size: Items per page (1-1000). Default: 10.
        count: Whether to return total count. Default: True.
        sort_str: Optional sorting string (e.g., "field:asc,field2:desc").
    """

    current: int = Field(
        default=1, gt=0, description="Current page number (1-based)", example=1
    )
    page_size: int = Field(
        default=10,
        ge=1,
        le=1000,
        description="Number of items per page (1-1000)",
        example=20,
    )
    count: bool = Field(
        default=True, description="Whether to return total count", example=True
    )
    sort_str: Optional[str] = Field(
        default=None,
        description='Optional sorting string (e.g., "field:asc,field2:desc")',
        example="created_at:desc,name:asc",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "current": 1,
                    "page_size": 20,
                    "count": True,
                    "sort_str": "created_at:desc,name:asc",
                }
            ]
        }
    )
