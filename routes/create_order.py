# routes/create_order.py
from fastapi import APIRouter, HTTPException
from datetime import datetime
from bson import ObjectId
from typing import List
from uuid import uuid4
from pydantic import BaseModel

from main import orders_collection, products_collection, app

router = APIRouter()


class OrderItem(BaseModel):
    product_id: str
    bought_quantity: int


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

        new_quantity = available_quantity - order_item.bought_quantity
        products_collection.update_one(
            {"_id": ObjectId(order_item.product_id)},
            {"$set": {"product_quantity": new_quantity}}
        )

    order_data["total_amount"] = total_amount
    order_data["_id"] = str(uuid4())

    result = orders_collection.insert_one(order_data)
    assert result.acknowledged

    return orders_collection.find_one({"_id": result.inserted_id})
