# SPDX-License-Identifier: MIT
"""Common service impl with frequently db operations"""

from typing import Dict, Generic, TypeVar

from pydantic import BaseModel

from fastlib.mapper.impl.base_mapper_impl import SqlModelMapper
from fastlib.schema import SortItem
from fastlib.service.base_service import BaseService

T = TypeVar("T", bound=BaseModel)
M = TypeVar("M", bound=SqlModelMapper)
IDType = TypeVar("IDType", int, str)


class BaseServiceImpl(Generic[M, T], BaseService[T]):
    def __init__(self, mapper: M):
        self.mapper = mapper

    async def save(self, *, data: T) -> T:
        return await self.mapper.insert(data=data)

    async def batch_save(self, *, data_list: list[T]) -> int:
        return await self.mapper.batch_insert(data_list=data_list)

    async def retrieve_by_id(self, *, id: IDType) -> T:
        return await self.mapper.select_by_id(id=id)

    async def retrieve_by_ids(self, *, ids: list[IDType]) -> list[T]:
        return await self.mapper.select_by_ids(ids=ids)

    async def retrieve_data_list(
        self, *, current: int, page_size: int, **kwargs
    ) -> tuple[
        list[T],
        int,
    ]:
        return await self.mapper.select_by_page(current=current, page_size=page_size, **kwargs)

    async def retrieve_ordered_data_list(
        self,
        *,
        current: int,
        page_size: int,
        sort: list[SortItem] = None,
        **kwargs,
    ) -> tuple[
        list[T],
        int,
    ]:
        return await self.mapper.select_by_ordered_page(
            current=current,
            page_size=page_size,
            sort=sort,
            **kwargs,
        )

    async def modify_by_id(self, *, data: T) -> None:
        affect_row: int = await self.mapper.update_by_id(data=data)
        if affect_row != 1:
            raise ValueError

    async def batch_modify_by_ids(self, *, ids: list[IDType], data: Dict) -> None:
        affect_row: int = await self.mapper.batch_update_by_ids(ids=ids, data=data)
        if len(ids) != affect_row:
            raise ValueError

    async def remove_by_id(self, *, id: IDType) -> None:
        affect_row: int = await self.mapper.delete_by_id(id=id)
        if affect_row != 1:
            raise ValueError

    async def batch_remove_by_ids(self, *, ids: list[IDType]) -> None:
        affect_row: int = await self.mapper.batch_delete_by_ids(ids=ids)
        if len(ids) != affect_row:
            raise ValueError
