import os

import certifi
from dotenv import load_dotenv
from fastapi import FastAPI
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

app = FastAPI()

load_dotenv()

# Use environment variable for MongoDB connection string
uri = os.getenv("MONGO_URI")
if uri is None:
    raise ValueError("MongoDB connection string not found in .env file")

client = MongoClient(uri, server_api=ServerApi('1'), tlsCAFile=certifi.where())
ecom_db = client.get_database('ecommerce')
products_collection = ecom_db["products"]
orders_collection = ecom_db["orders"]

# Import routes
from routes import get_products, create_order

app.include_router(get_products.router)
app.include_router(create_order.router)
