from fastapi import APIRouter
import sqlalchemy
from src import database as db

router = APIRouter()

@router.get("/catalog/", tags=["catalog"])
def get_catalog():    
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT num_green_potions FROM global_inventory"))
        
    """
    Each unique item combination must have only a single price.
    """
    num = result.fetchone()[0]
    if num > 0:
        return [
                {
                    "sku": "GREEN_POTION_0",
                    "name": "green potion",
                    "quantity": num,
                    "price": 50,
                    "potion_type": [0, 100, 0, 0],
                }
            ]
    return []