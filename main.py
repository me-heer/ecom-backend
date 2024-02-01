import certifi
from fastapi import FastAPI
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

app = FastAPI()

# TODO: From .env
uri = "mongodb+srv://mihir67mj:njtJ0K3JTYGSnxa5@cluster0.ksbp6er.mongodb.net/?retryWrites=true&w=majority"

client = MongoClient(uri, server_api=ServerApi('1'), tlsCAFile=certifi.where())
ecom_db = client.get_database('ecommerce')
products_collection = ecom_db["products"]
orders_collection = ecom_db["orders"]

# Import routes
from routes import get_products, create_order

# Include routes
app.include_router(get_products.router)
app.include_router(create_order.router)
