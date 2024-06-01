from typing import Type

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.base_class import Base
from db.session import get_session


class BaseCrud:
    model: Type[Base]

    def __init__(self, db: AsyncSession = Depends(get_session)):
        self.session = db
