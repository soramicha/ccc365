from fastapi import APIRouter
import sqlalchemy
from src import database as db

router = APIRouter()

@router.get("/catalog/", tags=["catalog"])
def get_catalog():    
    with db.engine.begin() as connection:
        red = connection.execute(sqlalchemy.text("SELECT red_potions FROM global_inventory"))
        green = connection.execute(sqlalchemy.text("SELECT num_green_potions FROM global_inventory"))
        blue = connection.execute(sqlalchemy.text("SELECT blue_potions FROM global_inventory"))
        
    """
    Each unique item combination must have only a single price.
    """
    mylist = []
    if blue.fetchone()[0] > 0:
        mylist.append({
                    "sku": "BLUE_POTION_0",
                    "name": "blue potion",
                    "quantity": 1,
                    "price": 60,
                    "potion_type": [0, 0, 100, 0],
                }
            )
    if red.fetchone()[0] > 0:
        mylist.append(
                {
                    "sku": "RED_POTION_0",
                    "name": "red potion",
                    "quantity": 1,
                    "price": 50,
                    "potion_type": [100, 0, 0, 0],
                }
        )
    if green.fetchone()[0] > 0:
        mylist.append(
                {
                    "sku": "GREEN_POTION_0",
                    "name": "green potion",
                    "quantity": 1,
                    "price": 40,
                    "potion_type": [0, 100, 0, 0],
                }
        )
    return mylist