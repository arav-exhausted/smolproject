# importing the basic libraries required  

from fastapi import FastAPI, HTTPException , Query, Path
from service.products import get_all_products, add_product , remove_product
from schema.product import Product
from uuid import uuid4, UUID
from datetime import datetime
# call the api in the form of app
app = FastAPI()



# using the get operation directing the database as what appears on the home page
@app.get('/')

# defined the root function which displays good morning
def root():
    return{"Good":"Morning"}


# gets the data to the products page

@app.get("/products")

# defined the function which lists the data throught the Query form
# the function 
def list_products(
    name: str= Query(
        default=None,
        min_length=1,
        max_length=50,
        description="Search by product name(case insensitive)",
    ),
    sort_by_price: bool =Query(default = False,description="Sort products by price"),
    order: str = Query(default = "asc",  description="Sort order when sort_by_price=true(asc,desc)"),
    limit:int = Query(
        default=10,
        ge=1,
        le=100,
        description="Number of items to return",),
    offset:int =Query(
        default=0, 
        ge=0,
        description="Pagination Offset",),
):


    products = get_all_products()
    if name:
        needle = name.strip().lower()
        products = [p for p in  products if needle in p.get("name", "").lower()]
    if not products:
        raise HTTPException(status_code=404, detail=f"NO product found matching name = {name}")
    
    if sort_by_price:
        reverse = order=="desc"
        products= sorted(products,key=lambda p:p.get("price",0), reverse=reverse)
    
    total = len(products)
    products = products[offset:offset+limit]
    
    return{"total":total,"limit":limit,"items":products}

@app.get("/products/{product_id}")

def get_product_by_id(product_id: str = Path(...,min_length=36,max_length=36,description="UUID of the product")):
    products = get_all_products()

    for product in products:
        if product["id"] == product_id:
            return product
        
    raise HTTPException(status_code=404, detail="Product not Found!")


@app.post("/products",status_code=201)

def create_product(product: Product):
    product_dict = product.model_dump(mode="json")
    product_dict["id"] = str(uuid4())    
    product_dict["created_at"] = datetime.utcnow().isoformat() + "Z"
    try:
        add_product(product_dict)
    except ValueError as e:
        raise HTTPException(status_code=400,detail=str(e))
    return product_dict


@app.delete("/products/{product_id}")
def delete_product(product_id:UUID = Path(...,description="Product ID", examples=["H423-4RD-993"])):
    try:
       response= remove_product(str(product_id))
       return response
    except Exception as e:
        raise HTTPException(status_code=400,detail=str(e))
    