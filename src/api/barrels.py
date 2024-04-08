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
        result = connection.execute(sqlalchemy.text("SELECT num_green_potions FROM global_inventory"))
        num_green_potions = 0
        for i in result:
            num_green_potions = int(i[0])
        total = num_green_potions * 100
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET gold = 0, num_green_ml = 2")) # gold - Barrel green's potion price, num_green_ml = total
    print(f"barrels delievered: {barrels_delivered} order_id: {order_id}")

    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    print(wholesale_catalog)
    
    num_green_potions = 0
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT num_green_potions FROM global_inventory"))
    for i in result:
        num_green_potions = int(i[0])
    if num_green_potions < 10:
        num = 1
    else:
        num = 0
    
    return [
            {
                "sku": "SMALL_GREEN_BARREL", # "SMALL_RED_BARREL",
                "quantity": num,
            }
        ]

