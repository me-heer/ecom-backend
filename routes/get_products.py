# routes/get_products.py
from fastapi import APIRouter, Query

from main import products_collection

router = APIRouter()


@router.get("/products")
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
