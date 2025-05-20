from typing import List, Optional, Tuple

from pydantic import UUID4
from sqlalchemy import UnaryExpression, asc, delete, desc, func, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from internal.domains.entities import GetMultiPostsFilter, PostEntity
from internal.infrastructures.relational_db.abstraction import AbstractPostRepo
from internal.infrastructures.relational_db.postgres.models import Post, PostModelMapper
from utils.time_utils import DATETIME_DEFAULT_FORMAT, from_str_to_dt


class PostRepo(AbstractPostRepo):
    def __init__(self, session: AsyncSession):
        self.session = session
        self.sort_fields = {
            "created_at": Post.created_at,
            "updated_at": Post.updated_at,
        }

    async def create(self, entity: PostEntity) -> UUID4:
        obj_in_data = entity.to_dict(exclude_none=True)
        stmt = insert(Post).values(**obj_in_data).returning(Post.id_)
        result = await self.session.execute(stmt)
        new_id = result.scalar()
        return new_id

    async def get_by_id(self, id_: UUID4) -> Optional[PostEntity]:
        stmt = select(Post).filter(Post.id_ == id_)
        token_ = (await self.session.execute(stmt)).scalars().first()
        if not token_:
            return None
        return PostModelMapper.to_entity(model=token_)

    async def get_multi(
        self, filter_: GetMultiPostsFilter
    ) -> Tuple[List[PostEntity], Optional[int]]:
        sort_stmt: Optional[UnaryExpression] = None

        if filter_.sort_field not in self.sort_fields:
            sort_stmt = desc(Post.created_at)
        if filter_.sort_order == "DESC":
            sort_stmt = desc(self.sort_fields[filter_.sort_field])
        elif filter_.sort_order == "ASC":
            sort_stmt = asc(self.sort_fields[filter_.sort_field])
        else:
            sort_stmt = desc(Post.created_at)

        filter_stmt = []
        if filter_.from_date is not None and filter_.to_date is not None:
            from_date_dt = from_str_to_dt(
                str_time=filter_.from_date, format_=DATETIME_DEFAULT_FORMAT
            )
            to_date_dt = from_str_to_dt(
                str_time=filter_.to_date, format_=DATETIME_DEFAULT_FORMAT
            )
            filter_stmt.append(Post.created_at >= from_date_dt)
            filter_stmt.append(Post.created_at <= to_date_dt)

        # Count query - only count the "id" column
        # optional call count query
        total_count: Optional[int] = None
        if filter_.enable_count:
            count_q = select(func.count(Post.id_)).filter(*filter_stmt)
            total_count = (await self.session.execute(count_q)).scalar()

        # Main query with sorting, offset, and limit
        q = select(Post)
        if filter_stmt:
            q = q.filter(*filter_stmt)
        q = q.order_by(sort_stmt).offset(filter_.offset).limit(filter_.limit)
        result = (await self.session.execute(q)).scalars().all()
        posts = [PostModelMapper.to_entity(model=post_) for post_ in result]
        return posts, total_count

    async def update(self, entity: PostEntity):
        obj_in_data = entity.to_dict(exclude_none=True)
        stmt = update(Post).where(Post.id_ == entity.id_).values(**obj_in_data)
        await self.session.execute(stmt)
        return

    async def delete(self, id_: UUID4):
        stmt = delete(Post).where(Post.id_ == id_)
        await self.session.execute(stmt)
        return
