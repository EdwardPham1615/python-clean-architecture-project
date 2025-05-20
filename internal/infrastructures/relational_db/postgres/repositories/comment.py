from typing import List, Optional, Tuple

from pydantic import UUID4
from sqlalchemy import UnaryExpression, asc, delete, desc, func, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from internal.domains.entities import CommentEntity, GetMultiCommentsFilter
from internal.infrastructures.relational_db.abstraction import AbstractCommentRepo
from internal.infrastructures.relational_db.postgres.models import (
    Comment,
    CommentModelMapper,
)
from utils.time_utils import DATETIME_DEFAULT_FORMAT, from_str_to_dt


class CommentRepo(AbstractCommentRepo):
    def __init__(self, session: AsyncSession):
        self.session = session
        self.sort_fields = {
            "created_at": Comment.created_at,
            "updated_at": Comment.updated_at,
        }

    async def create(self, entity: CommentEntity) -> UUID4:
        obj_in_data = entity.to_dict(exclude_none=True)
        stmt = insert(Comment).values(**obj_in_data).returning(Comment.id_)
        result = await self.session.execute(stmt)
        new_id = result.scalar()
        return new_id

    async def get_by_id(self, id_: UUID4) -> Optional[CommentEntity]:
        stmt = select(Comment).filter(Comment.id_ == id_)
        token_ = (await self.session.execute(stmt)).scalars().first()
        if not token_:
            return None
        return CommentModelMapper.to_entity(model=token_)

    async def get_multi(
        self, filter_: GetMultiCommentsFilter
    ) -> Tuple[List[CommentEntity], Optional[int]]:
        sort_stmt: Optional[UnaryExpression] = None

        if filter_.sort_field not in self.sort_fields:
            sort_stmt = desc(Comment.created_at)
        if filter_.sort_order == "DESC":
            sort_stmt = desc(self.sort_fields[filter_.sort_field])
        elif filter_.sort_order == "ASC":
            sort_stmt = asc(self.sort_fields[filter_.sort_field])
        else:
            sort_stmt = desc(Comment.created_at)

        filter_stmt = []
        if filter_.post_id:
            filter_stmt.append(Comment.post_id == filter_.post_id)
        if filter_.from_date is not None and filter_.to_date is not None:
            from_date_dt = from_str_to_dt(
                str_time=filter_.from_date, format_=DATETIME_DEFAULT_FORMAT
            )
            to_date_dt = from_str_to_dt(
                str_time=filter_.to_date, format_=DATETIME_DEFAULT_FORMAT
            )
            filter_stmt.append(Comment.created_at >= from_date_dt)
            filter_stmt.append(Comment.created_at <= to_date_dt)

        # Count query - only count the "id" column
        # optional call count query
        total_count: Optional[int] = None
        if filter_.enable_count:
            count_q = select(func.count(Comment.id_)).filter(*filter_stmt)
            total_count = (await self.session.execute(count_q)).scalar()

        # Main query with sorting, offset, and limit
        q = select(Comment)
        if filter_stmt:
            q = q.filter(*filter_stmt)
        q = q.order_by(sort_stmt).offset(filter_.offset).limit(filter_.limit)
        result = (await self.session.execute(q)).scalars().all()
        comments = [CommentModelMapper.to_entity(model=comment_) for comment_ in result]
        return comments, total_count

    async def update(self, entity: CommentEntity):
        obj_in_data = entity.to_dict(exclude_none=True)
        stmt = update(Comment).where(Comment.id_ == entity.id_).values(**obj_in_data)
        await self.session.execute(stmt)
        return

    async def delete(self, id_: UUID4):
        stmt = delete(Comment).where(Comment.id_ == id_)
        await self.session.execute(stmt)
        return
