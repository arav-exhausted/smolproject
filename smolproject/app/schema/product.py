from pydantic import BaseModel, Field, AnyUrl, field_validator, model_validator,computed_field, EmailStr
from typing import Annotated, Literal, Optional, List
from uuid import UUID
from datetime import datetime




class Seller(BaseModel):
    id: UUID
    name: Annotated[str,Field(
        min_length=2,
        max_length=60,
        title="Seller Name",
        description="Enter the name of the seller (2-60 words)",
        examples=["Samsung Official Store"," Apple exclusive store"],
    )]

    email : EmailStr
    website: AnyUrl

    @field_validator("email", mode="after")
    @classmethod
    def validate_seller_email_domain(cls, value:EmailStr):
        allowed_domains = ["mistore.in","hpworld.in"]
        domain = str(value).split("@")[-1].lower()
        if domain not in allowed_domains:
            raise ValueError(f"Seller email domain is not allowed :{domain}")
        return value



class Dimensions(BaseModel):
    length : Annotated[float,Field( ge=0,strict =True,description="the length of the product")]
    width : Annotated[float,Field( ge=0,strict =True,description="the width of the product")]
    height : Annotated[float,Field( ge=0,strict =True,description="the height of the product")]



class Product(BaseModel):
    id: UUID
    sku: Annotated[str,Field(min_length=6,max_length=30,title="SKU",description="Stock Keeping Unit")]
    name: Annotated[str,Field(
        min_length=1,
        max_length=80,
        title="Product Name",
        description="Enter the name of the product(1-80 words)",
        examples=["Samsung Model X, Apple model X"],
    )]
    description: Annotated[str,Field(max_length=200, description="Add a short product description")]

    category : Annotated[str, Field(max_length=100, description="Add which category it belongs", examples=["gaming, laptops "])]

    brand : Annotated[str, Field(max_length=20, description="Brand which the product belongs", examples=["Apple, Samsung"])]
    price : Annotated[float, Field(description="Price of the product", examples=["23456.43","23345.22"])]
    currency: Literal["INR"] = "INR"
    discount_percent : Annotated[int, Field( description="Any available discount",)]
    stock : Annotated[int, Field(ge=0, description="The stock available")]
    is_active : Annotated[bool, Field( description="Is product available for sale")]
    rating:Annotated[float, Field(description="add the ratings for the product")]

    tags  : Annotated[
        Optional[List[str]],
        Field(
            default= None,
            max_length= 10,
            description="Upto 10 tags",
        )
    ]
    image_urls : Annotated[
        List[AnyUrl],
        Field(
            max_length=1,
            description="The image link to the product",
        )
    ]

    dimensions_cm : Dimensions

    seller : Seller

    created_at : datetime

    @field_validator("sku", mode="after")
    @classmethod
    def validate_sku_format(cls, value:str):
        if "-" not in value:
            raise ValueError("SKU must have '-'")
        
        last = value.split("-")[-1]
        if not (len(last)==3 and last.isdigit()):
            raise ValueError("SKU must end with a 3-digit sequence like -234")
        return value
    

    @model_validator(mode="after")
    @classmethod
    def validate_rule(cls,model:"Product"):
        if model.stock==0 and model.is_active==True:
            raise ValueError("If stock is zero is_active must be false")
        if model.discount_percent>0 and model.rating==0:
            raise ValueError("Discounted price must have a rating")
        
        return model
        

    @computed_field
    @property
    def final_price(self) -> float:
        return round(self.price * (1-self.discount_percent / 100),2)
    @computed_field
    @property 
    def volume_cm3(self)->float:
        s = self.dimensions_cm
        return round(s.length * s.width * s.height, 2)