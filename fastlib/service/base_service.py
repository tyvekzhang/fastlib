# SPDX-License-Identifier: MIT
"""Abstract service with common database operations."""

from abc import ABC, abstractmethod
from typing import Any, Generic, Optional, TypeVar

from pydantic import BaseModel
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from fastlib.schema import SortItem

IDType = TypeVar("IDType", int, str)
ModelType = TypeVar("ModelType", bound=SQLModel)


class BaseService(Generic[ModelType], ABC):
    """Base service interface with common CRUD operations"""

    @abstractmethod
    async def save(
        self, data: BaseModel, db_session: Optional[AsyncSession] = None
    ) -> BaseModel:
        """Insert a single record"""
        pass

    @abstractmethod
    async def save_batch(
        self, data_list: list[BaseModel], db_session: Optional[AsyncSession] = None
    ) -> int:
        """Batch insert records"""
        pass

    @abstractmethod
    async def save_or_update(
        self, data: BaseModel, db_session: Optional[AsyncSession] = None
    ) -> bool:
        """Insert or update a record"""
        pass

    @abstractmethod
    async def save_or_update_batch(
        self, data_list: list[BaseModel], db_session: Optional[AsyncSession] = None
    ) -> bool:
        """Batch insert or update records"""
        pass

    @abstractmethod
    async def remove_by_id(
        self, id: IDType, db_session: Optional[AsyncSession] = None
    ) -> bool:
        """Delete record by ID"""
        pass

    @abstractmethod
    async def remove_by_ids(
        self, ids: list[IDType], db_session: Optional[AsyncSession] = None
    ) -> bool:
        """Batch delete records by IDs"""
        pass

    @abstractmethod
    async def remove(self, db_session: Optional[AsyncSession] = None, **kwargs) -> bool:
        """Delete records by conditions"""
        pass

    @abstractmethod
    async def update_by_id(
        self, data: BaseModel, db_session: Optional[AsyncSession] = None
    ) -> bool:
        """Update record by ID"""
        pass

    @abstractmethod
    async def update_batch_by_ids(
        self,
        ids: list[IDType],
        data: dict[str, Any],
        db_session: Optional[AsyncSession] = None,
    ) -> bool:
        """Batch update records by IDs"""
        pass

    @abstractmethod
    async def batch_update(
        self, data_list: list[BaseModel], db_session: Optional[AsyncSession] = None
    ) -> bool:
        """Batch update records"""
        pass

    @abstractmethod
    async def update(
        self, data: BaseModel, db_session: Optional[AsyncSession] = None, **kwargs
    ) -> bool:
        """Update records by conditions"""
        pass

    @abstractmethod
    async def get_by_id(
        self,
        id: IDType,
        fields: Optional[list[str]] = None,
        db_session: Optional[AsyncSession] = None,
    ) -> Optional[BaseModel]:
        """Get record by ID"""
        pass

    @abstractmethod
    async def get_one(
        self, db_session: Optional[AsyncSession] = None, **kwargs
    ) -> Optional[BaseModel]:
        """Get one record by conditions"""
        pass

    @abstractmethod
    async def list_by_ids(
        self,
        ids: list[IDType],
        fields: Optional[list[str]] = None,
        db_session: Optional[AsyncSession] = None,
    ) -> list[BaseModel]:
        """Get records by IDs"""
        pass

    @abstractmethod
    async def list_all(
        self,
        fields: Optional[list[str]] = None,
        db_session: Optional[AsyncSession] = None,
        **kwargs,
    ) -> list[BaseModel]:
        """Get all records with optional filtering"""
        pass

    @abstractmethod
    async def list(
        self, db_session: Optional[AsyncSession] = None, **kwargs
    ) -> list[BaseModel]:
        """Get records by conditions"""
        pass

    @abstractmethod
    async def page(
        self,
        current: int = 1,
        page_size: int = 100,
        count: bool = True,
        fields: Optional[list[str]] = None,
        db_session: Optional[AsyncSession] = None,
        **kwargs,
    ) -> tuple[list[BaseModel], int]:
        """Paginated query"""
        pass

    @abstractmethod
    async def page_ordered(
        self,
        current: int = 1,
        page_size: int = 100,
        count: bool = True,
        sort_list: Optional[list[SortItem]] = None,
        fields: Optional[list[str]] = None,
        db_session: Optional[AsyncSession] = None,
        **kwargs,
    ) -> tuple[list[BaseModel], int]:
        """Paginated query with ordering"""
        pass

    @abstractmethod
    async def count(self, db_session: Optional[AsyncSession] = None, **kwargs) -> int:
        """Count records by conditions"""
        pass

    @abstractmethod
    async def exists(self, db_session: Optional[AsyncSession] = None, **kwargs) -> bool:
        """Check if records exist by conditions"""
        pass

    @abstractmethod
    async def get_children_tree(
        self,
        parent_data: list[BaseModel],
        max_level: int = 5,
        db_session: Optional[AsyncSession] = None,
    ) -> list[BaseModel]:
        """Get children tree recursively"""
        pass
