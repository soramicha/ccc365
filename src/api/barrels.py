from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db
import os
import dotenv
from sqlalchemy import create_engine

router = APIRouter(
    prefix="/barrels",
    tags=["barrels"],
    dependencies=[Depends(auth.get_api_key)],
)

class Barrel(BaseModel):
    sku: str

    ml_per_barrel: int
    potion_type: list[int]
    price: int

    quantity: int

@router.post("/deliver/{order_id}")
def post_deliver_barrels(barrels_delivered: list[Barrel], order_id: int):
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET gold = gold - {barrels_delivered[0].price}, num_green_ml = num_green_ml + {barrels_delivered[0].ml_per_barrel}"))

    print(f"barrels delievered: {barrels_delivered} order_id: {order_id}")

    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    print(wholesale_catalog)
    
    #num_green_potions = 50
    print("Begin Connection")
    with db.engine.begin() as connection:
        print("Connected")
        result_potions = connection.execute(sqlalchemy.text('SELECT num_green_potions FROM global_inventory'))
        # get the values of the number of green potions
        for i in result_potions.all():
            num_green_potions = i[0]

    # if there are less than 10 green potions, then buy a small green barrel, otherwise do nothing
    # make sure you have enough gold before purchasing a small green barrel
    if num_green_potions < 10:
        num = 1
    else:
        num = 0
    
    return [
            {
                "sku": "SMALL_GREEN_BARREL",
                "quantity": num,
            }
        ]

