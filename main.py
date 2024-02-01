from datetime import datetime
from typing import List
from uuid import uuid4

import certifi
from bson import ObjectId
from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

app = FastAPI()

# TODO: From .env
uri = "mongodb+srv://mihir67mj:njtJ0K3JTYGSnxa5@cluster0.ksbp6er.mongodb.net/?retryWrites=true&w=majority"

# TODO: Should be a singleton
client = MongoClient(uri, server_api=ServerApi('1'), tlsCAFile=certifi.where())

# TODO: Should we client.close()?

ecom_db = client.get_database('ecommerce')
products_collection = ecom_db["products"]
orders_collection = ecom_db["orders"]


@app.get("/products")
async def get_products(min_price: float = Query(None, title="Minimum Price", description="Minimum price of the "
                                                                                         "product to be included in "
                                                                                         "the results", gt=0),
                       max_price: float = Query(None, title="Maximum Price", description="Maximum price of the "
                                                                                         "product to be included in "
                                                                                         "the results", gt=0),
                       limit: int = Query(10, title="Limit", description="Number of records to retrieve", gt=0),
                       offset: int = Query(0, title="Offset", description="Offset for pagination", ge=0)):
    pipeline = [
        {"$match": {"product_price": {"$gte": min_price} if min_price is not None else {"$gte": 0}}},
        {"$match": {"product_price": {"$lte": max_price} if max_price is not None else {"$exists": True}}},
        {"$facet": {
            "data": [
                {"$skip": offset},
                {"$limit": limit},
                {"$project": {"_id": 1, "product_name": 1, "product_price": 1, "product_quantity": 1}},
                {"$addFields": {"id": {"$toString": "$_id"}}},
                {"$project": {"_id": 0}},
                {"$addFields": {"quantity": "$product_quantity"}},
                {"$addFields": {"price": "$product_price"}},
                {"$project": {"product_name": 1, "price": 1, "quantity": 1, "id": 1}}
            ],
            "page": [
                {"$count": "total"},
                {
                    "$addFields": {
                        "limit": limit,
                        "nextOffset": {
                            "$cond": {
                                "if": {
                                    "$lt": [
                                        {"$add": [offset, limit]},
                                        "$total"
                                    ]
                                },
                                "then": {"$add": [offset, limit]},
                                "else": None
                            }
                        },
                        "prevOffset": {
                            "$cond": {
                                "if": {
                                    "$gte": [offset, limit]
                                },
                                "then": {"$subtract": [offset, limit]},
                                "else": None
                            }
                        },
                    }
                }
            ]
        }}
    ]

    [result] = list(products_collection.aggregate(pipeline))

    return result


class OrderItem(BaseModel):
    product_id: str
    bought_quantity: int

    @staticmethod
    def validate_bought_quantity(value):
        if value <= 0:
            raise ValueError("Bought quantity must be greater than 0")
        return value


class UserAddress(BaseModel):
    city: str
    country: str
    zip_code: str


class OrderDto(BaseModel):
    items: List[OrderItem]
    user_address: UserAddress
    createdOn: datetime = None


@app.post("/orders/")
async def create_order(order: OrderDto):
    order_data = order.model_dump()

    order_data["createdOn"] = datetime.now()

    total_amount = 0.0
    for order_item in order.items:
        product = products_collection.find_one({"_id": ObjectId(order_item.product_id)})

        if not product:
            raise HTTPException(status_code=404, detail=f"Product with ID {order_item.product_id} not found")

        if order_item.bought_quantity <= 0:
            raise HTTPException(
                status_code=400,
                detail=f"Bought quantity must be greater than 0"
            )

        available_quantity = product.get("product_quantity")
        if order_item.bought_quantity > available_quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient quantity available for product {order_item.product_id}"
            )

        item_price = product.get("product_price")
        total_amount += order_item.bought_quantity * item_price

    order_data["total_amount"] = total_amount
    order_data["_id"] = str(uuid4())

    result = orders_collection.insert_one(order_data)
    assert result.acknowledged

    return orders_collection.find_one({"_id": result.inserted_id})
