from fastapi import APIRouter
import sqlalchemy
from src import database as db
import os
import dotenv
from sqlalchemy import create_engine

router = APIRouter()

@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    
    # put in connect db code here
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT num_green_potions FROM global_inventory"))
            
    """
    Each unique item combination must have only a single price.
    """

    return [
            {
                "sku": "RED_POTION_0",
                "name": "red potion",
                "quantity": result, #1, # change things here
                "price": 50,
                "potion_type": [100, 0, 0, 0],
            }
        ]