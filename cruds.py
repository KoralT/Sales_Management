from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from bson import ObjectId
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost/",
    "http://localhost:8000/",
    "http://localhost:3000",
    "https://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=[""],
    allow_headers=[""],
)

client = MongoClient("mongodb://localhost:27017/")
db = client["products_list"]
collection = db["products"]

class Product(BaseModel):
    _id: ObjectId
    name: str
    description: str
    price: float
    stock: int
    category: str

@app.post("/products")
def create_product(product: Product):
    product_dict = product.dict()
    result = collection.insert_one(product_dict)
    product_dict["_id"] = str(result.inserted_id)
    return product_dict

@app.get("/")
def read_products(skip: int = 0, limit: int = 100):
    products = collection.find().skip(skip).limit(limit)
    return list(map(lambda p: {**p, '_id': str(p['_id'])}, products))

@app.get("/products/{product_id}")
def read_product(product_id: str):
    product = collection.find_one({'_id': ObjectId(product_id)})
    product['_id'] = str(product['_id'])
    if product:
        return product
    else:
        raise HTTPException(status_code=404, detail="Product not found")


@app.put("/products/{product_id}")
def update_product(product_id: str, product: Product):
    product_dict = product.dict()
    result = collection.replace_one({"_id": ObjectId(product_id)}, product_dict)
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    product_dict["_id"] = product_id
    return product_dict


@app.delete("/products/{product_id}")
def delete_product(product_id: str):
    result = collection.delete_one({"_id": ObjectId(product_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product deleted successfully"}
    
    