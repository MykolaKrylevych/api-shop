from ..base import BaseProduct
from typing import Optional, List


class SchemasProductOut(BaseProduct):
    id: Optional[int]
    photo_urls: List[str]

