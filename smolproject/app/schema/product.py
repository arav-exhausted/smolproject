from pydantic import BaseModel, Field
from typing import Annotated
from uuid import UUID


class Product(BaseModel):
    id: UUID
    sku: Annotated[str,Field(min_length=6,max_length=30,title="SKU",description="Stock Keeping Unit")]
    name: str