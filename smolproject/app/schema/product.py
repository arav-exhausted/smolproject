from pydantic import BaseModel, Field
from typing import Annotated



class Product(BaseModel):
    id: str
    sku: Annotated[str,Field(min_length=6,max_length=30,title="SKU",description="Stock Keeping Unit")]
    name: str