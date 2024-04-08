from fastapi import APIRouter
import sqlalchemy
from src import database as db

router = APIRouter()

@router.get("/catalog/", tags=["catalog"])
def get_catalog():    
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT num_green_potions FROM global_inventory"))
    
    num = 0
    for i in result:
        num = i[0]
    
    """
    Each unique item combination must have only a single price.
    """
    
    return [
            {
                "sku": "GREEN_POTION_0",
                "name": "green potion",
                "quantity": num,
                "price": 150,
                "potion_type": [0, 0, 100, 0],
            }
        ]