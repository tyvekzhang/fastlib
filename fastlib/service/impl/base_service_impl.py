# SPDX-License-Identifier: MIT
"""Base service implementation with transaction support"""

from typing import Any, Generic, Optional, TypeVar

from pydantic import BaseModel
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from fastlib.mapper.base_mapper import BaseMapper
from fastlib.schema import SortItem
from fastlib.service.base_service import BaseService

IDType = TypeVar("IDType", int, str)
ModelType = TypeVar("ModelType", bound=SQLModel)


class BaseServiceImpl(
    BaseService[ModelType],
    Generic[ModelType],
):
    """Base service implementation with common CRUD operations and transaction support"""

    def __init__(
        self,
        mapper: BaseMapper,
        model: type[ModelType],
    ):
        self.mapper = mapper
        self.model = model

    async def save(
        self, data: BaseModel, db_session: Optional[AsyncSession] = None
    ) -> BaseModel:
        """Insert a single record"""
        model_data = self.model(**data.model_dump())
        saved_data = await self.mapper.insert(data=model_data, db_session=db_session)
        return BaseModel.model_validate(saved_data)

    async def save_batch(
        self, data_list: list[BaseModel], db_session: Optional[AsyncSession] = None
    ) -> int:
        """Batch insert records"""
        model_list = [self.model(**data.model_dump()) for data in data_list]
        return await self.mapper.batch_insert(
            data_list=model_list, db_session=db_session
        )

    async def save_or_update(
        self, data: BaseModel, db_session: Optional[AsyncSession] = None
    ) -> bool:
        """Insert or update a record"""
        # Check if data exists (assuming data has id field)
        if hasattr(data, "id") and data.id:
            existing = await self.mapper.select_by_id(id=data.id, db_session=db_session)
            if existing:
                # Update existing
                model_data = self.model(**data.model_dump())
                count = await self.mapper.update_by_id(
                    data=model_data, db_session=db_session
                )
                return count > 0
        # Insert new
        model_data = self.model(**data.model_dump())
        saved_data = await self.mapper.insert(data=model_data, db_session=db_session)
        return saved_data is not None

    async def save_or_update_batch(
        self, data_list: list[BaseModel], db_session: Optional[AsyncSession] = None
    ) -> bool:
        """Batch insert or update records"""
        # Separate inserts and updates
        to_insert = []
        to_update = []

        for data in data_list:
            if hasattr(data, "id") and data.id:
                existing = await self.mapper.select_by_id(
                    id=data.id, db_session=db_session
                )
                if existing:
                    to_update.append(data)
                    continue
            to_insert.append(data)

        # Execute batch operations
        if to_insert:
            insert_models = [self.model(**data.model_dump()) for data in to_insert]
            await self.mapper.batch_insert(
                data_list=insert_models, db_session=db_session
            )

        if to_update:
            for data in to_update:
                model_data = self.model(**data.model_dump())
                await self.mapper.update_by_id(data=model_data, db_session=db_session)

        return True

    async def remove_by_id(
        self, id: IDType, db_session: Optional[AsyncSession] = None
    ) -> bool:
        """Delete record by ID"""
        count = await self.mapper.delete_by_id(id=id, db_session=db_session)
        return count > 0

    async def remove_by_ids(
        self, ids: list[IDType], db_session: Optional[AsyncSession] = None
    ) -> bool:
        """Batch delete records by IDs"""
        count = await self.mapper.batch_delete_by_ids(ids=ids, db_session=db_session)
        return count > 0

    async def remove(self, db_session: Optional[AsyncSession] = None, **kwargs) -> bool:
        """Delete records by conditions"""
        # This would need a more complex implementation based on your filter system
        # For now, we'll use a simple approach - get IDs first then delete
        records, _ = await self.mapper.select_by_page(db_session=db_session, **kwargs)
        if records:
            ids = [record.id for record in records]
            return await self.remove_by_ids(ids, db_session=db_session)
        return False

    async def update_by_id(
        self, data: BaseModel, db_session: Optional[AsyncSession] = None
    ) -> bool:
        """Update record by ID"""
        model_data = self.model(**data.model_dump())
        count = await self.mapper.update_by_id(data=model_data, db_session=db_session)
        return count > 0

    async def update_batch_by_ids(
        self,
        ids: list[IDType],
        data: dict[str, Any],
        db_session: Optional[AsyncSession] = None,
    ) -> bool:
        """Batch update records by IDs"""
        count = await self.mapper.batch_update_by_ids(
            ids=ids, data=data, db_session=db_session
        )
        return count > 0

    async def batch_update(
        self, data_list: list[BaseModel], db_session: Optional[AsyncSession] = None
    ) -> bool:
        """Batch update records"""
        model_list = [self.model(**data.model_dump()) for data in data_list]
        count = await self.mapper.batch_update(
            data_list=model_list, db_session=db_session
        )
        return count > 0

    async def update(
        self, data: BaseModel, db_session: Optional[AsyncSession] = None, **kwargs
    ) -> bool:
        """Update records by conditions"""
        # Get records matching conditions
        records = await self.list(db_session=db_session, **kwargs)
        if not records:
            return False

        # Update each record
        success_count = 0
        for record in records:
            # Merge update data with existing record
            update_data = data.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(record, key, value)

            # Convert to model and update
            model_data = self.model(**record.model_dump())
            count = await self.mapper.update_by_id(
                data=model_data, db_session=db_session
            )
            if count > 0:
                success_count += 1

        return success_count > 0

    async def get_by_id(
        self,
        id: IDType,
        fields: Optional[list[str]] = None,
        db_session: Optional[AsyncSession] = None,
    ) -> Optional[BaseModel]:
        """Get record by ID"""
        result = await self.mapper.select_by_id(
            id=id, fields=fields, db_session=db_session
        )
        if result:
            return BaseModel.model_validate(result)
        return None

    async def get_one(
        self, db_session: Optional[AsyncSession] = None, **kwargs
    ) -> Optional[BaseModel]:
        """Get one record by conditions"""
        records = await self.list(db_session=db_session, **kwargs)
        return records[0] if records else None

    async def list_by_ids(
        self,
        ids: list[IDType],
        fields: Optional[list[str]] = None,
        db_session: Optional[AsyncSession] = None,
    ) -> list[BaseModel]:
        """Get records by IDs"""
        results = await self.mapper.select_by_ids(
            ids=ids, fields=fields, db_session=db_session
        )
        return [BaseModel.model_validate(result) for result in results]

    async def list_all(
        self,
        fields: Optional[list[str]] = None,
        db_session: Optional[AsyncSession] = None,
        **kwargs,
    ) -> list[BaseModel]:
        """Get all records with optional filtering"""
        # Use a large page size to get all records
        records, _ = await self.mapper.select_by_page(
            current=1,
            page_size=10000,  # Adjust based on your needs
            count=False,
            fields=fields,
            db_session=db_session,
            **kwargs,
        )
        return [BaseModel.model_validate(record) for record in records]

    async def list(
        self, db_session: Optional[AsyncSession] = None, **kwargs
    ) -> list[BaseModel]:
        """Get records by conditions"""
        return await self.list_all(db_session=db_session, **kwargs)

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
        records, total = await self.mapper.select_by_page(
            current=current,
            page_size=page_size,
            count=count,
            fields=fields,
            db_session=db_session,
            **kwargs,
        )
        return [BaseModel.model_validate(record) for record in records], total

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
        records, total = await self.mapper.select_by_ordered_page(
            current=current,
            page_size=page_size,
            count=count,
            sort_list=sort_list,
            fields=fields,
            db_session=db_session,
            **kwargs,
        )
        return [BaseModel.model_validate(record) for record in records], total

    async def count(self, db_session: Optional[AsyncSession] = None, **kwargs) -> int:
        """Count records by conditions"""
        _, total = await self.mapper.select_by_page(
            current=1, page_size=1, count=True, db_session=db_session, **kwargs
        )
        return total

    async def exists(self, db_session: Optional[AsyncSession] = None, **kwargs) -> bool:
        """Check if records exist by conditions"""
        count = await self.count(db_session=db_session, **kwargs)
        return count > 0

    async def get_children_tree(
        self,
        parent_data: list[BaseModel],
        max_level: int = 5,
        db_session: Optional[AsyncSession] = None,
    ) -> list[BaseModel]:
        """Get children tree recursively"""
        results = await self.mapper.get_children_recursively(
            parent_data=parent_data,
            max_level=max_level,
            db_session=db_session,
        )
        return [BaseModel.model_validate(result) for result in results]
