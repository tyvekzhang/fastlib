# SPDX-License-Identifier: MIT
"""Database Model Base Classes"""

from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, DateTime, Integer
from sqlmodel import Field
from sqlmodel import SQLModel as _SQLModel

from fastlib.utils.snowflake_util import snowflake_id


class BaseModel(_SQLModel):
    """
    Identifier for a model
    """

    id: int = Field(
        default_factory=snowflake_id,
        primary_key=True,
        sa_type=BigInteger,
        sa_column_kwargs={"comment": "主键"},
    )


class TreeModel(BaseModel):
    """
    Identifier for a model
    """

    parent_id: int = Field(
        index=True,
        sa_type=BigInteger,
        sa_column_kwargs={"comment": "父id"},
    )

    sort: int = Field(
        index=True,
        sa_type=Integer,
        sa_column_kwargs={"comment": "排序"},
    )


class ModelExt(_SQLModel):
    """
    Create time and update time for a model, can be automatically generated
    """

    create_at: Optional[datetime] = Field(
        sa_type=DateTime,
        default_factory=datetime.utcnow,
        sa_column_kwargs={"comment": "创建时间"},
    )
    update_at: Optional[datetime] = Field(
        sa_type=DateTime,
        default_factory=datetime.utcnow,
        sa_column_kwargs={
            "onupdate": datetime.utcnow,
            "comment": "更新时间",
        },
    )
