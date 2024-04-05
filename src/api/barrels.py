from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth

# changes made

import sqlalchemy
from src import database as db
import os
import dotenv
from sqlalchemy import create_engine

CREATE TABLE global_inventory (
    id bigint generated always as identity,
    num_green_potions int,
    num_green_ml int,
    gold int
);

with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT num_green_potions FROM global_inventory"))
        if num_green_potions < 10:
            connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_green_potions = num_green_potions + 1"))

def database_connection_url():
    dotenv.load_dotenv()

    return os.environ.get("POSTGRES_URI")

engine = create_engine(database_connection_url(), pool_pre_ping=True)

# changes made

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
    """ """
    print(f"barrels delievered: {barrels_delivered} order_id: {order_id}")

    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print(wholesale_catalog)

    return [
        {
            "sku": "SMALL_RED_BARREL",
            "quantity": 1,
        }
    ]

