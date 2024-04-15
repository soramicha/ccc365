from fastapi import APIRouter, Depends
from enum import Enum
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/bottler",
    tags=["bottler"],
    dependencies=[Depends(auth.get_api_key)],
)

class PotionInventory(BaseModel):
    potion_type: list[int]
    quantity: int

@router.post("/deliver/{order_id}")
def post_deliver_bottles(potions_delivered: list[PotionInventory], order_id: int):
    with db.engine.begin() as connection:
        if potions_delivered[0].potion_type == [0, 100, 0, 0]: # if it's green
                connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_green_potions = num_green_potions + {potions_delivered[0].quantity}, num_green_ml = num_green_ml - (100 * {potions_delivered[0].quantity})"))
        if potions_delivered[0].potion_type == [100, 0, 0, 0]: # if it's red
            connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET red_potions = red_potions + {potions_delivered[0].quantity}, red_ml = red_ml - (100 * {potions_delivered[0].quantity})"))
        if potions_delivered[0].potion_type == [0, 0, 100, 0]: # if it's blue
            connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET blue_potions = blue_potions + {potions_delivered[0].quantity}, blue_ml = blue_ml - (100 * {potions_delivered[0].quantity})"))
    print(f"potions delivered: {potions_delivered} order_id: {order_id}")

    return "OK"

@router.post("/plan")
def get_bottle_plan():
    """
    Go from barrel to bottle.
    """
    
    with db.engine.begin() as connection:
        green = connection.execute(sqlalchemy.text("SELECT num_green_ml FROM global_inventory"))
        red = connection.execute(sqlalchemy.text("SELECT red_ml FROM global_inventory"))
        blue = connection.execute(sqlalchemy.text("SELECT blue_ml FROM global_inventory"))
        
        
    # Each bottle has a quantity of what proportion of red, blue, and green potion to add.
    # Expressed in integers from 1 to 100 that must sum up to 100.

    numblue = int(blue.fetchone()[0] / 100)
    if numblue != 0:
        return [
                {
                    "potion_type": [0, 0, 100, 0],
                    "quantity": numblue,
                }
            ]
    numred = int(red.fetchone()[0] / 100)
    if numred != 0:
        return [
            {
                "potion_type": [100, 0, 0, 0],
                "quantity": numred,
            }
        ]
    numgreen = int(green.fetchone()[0] / 100)
    if numgreen != 0:
        return [
                {
                    "potion_type": [0, 100, 0, 0],
                    "quantity": numgreen,
                }
            ]
    return [
            {
                "potion_type": [0, 0, 100, 0],
                "quantity": 0,
            }
        ]

if __name__ == "__main__":
    print(get_bottle_plan())