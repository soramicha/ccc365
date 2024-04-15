from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db

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
        if barrels_delivered[0].sku == "SMALL_BLUE_BARREL" or barrels_delivered[0].sku == "MINI_BLUE_BARREL":
            connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET gold = gold - {barrels_delivered[0].price}, blue_ml = blue_ml + {barrels_delivered[0].ml_per_barrel}"))
        if barrels_delivered[0].sku == "SMALL_RED_BARREL" or barrels_delivered[0].sku == "MINI_RED_BARREL":
            connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET gold = gold - {barrels_delivered[0].price}, red_ml = red_ml + {barrels_delivered[0].ml_per_barrel}"))
        if barrels_delivered[0].sku == "SMALL_GREEN_BARREL" or barrels_delivered[0].sku == "MINI_GREEN_BARREL":
            connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET gold = gold - {barrels_delivered[0].price}, num_green_ml = num_green_ml + {barrels_delivered[0].ml_per_barrel}"))
    print(f"barrels delievered: {barrels_delivered} order_id: {order_id}")

    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    print(wholesale_catalog)
  
    with db.engine.begin() as connection:
        green = connection.execute(sqlalchemy.text('SELECT num_green_potions FROM global_inventory'))
        blue = connection.execute(sqlalchemy.text('SELECT blue_potions FROM global_inventory'))
        red = connection.execute(sqlalchemy.text('SELECT red_potions FROM global_inventory'))
        result = connection.execute(sqlalchemy.text('SELECT gold FROM global_inventory'))
    
    gold = result.fetchone()[0]
    if gold < 60:
        return [
            {
                "sku": "SMALL_GREEN_BARREL",
                "quantity": 0,
            }
        ]
    if blue.fetchone()[0] < 1 and gold >= 60:
        return [
            {
                "sku": "MINI_BLUE_BARREL",
                "quantity": 1,
            }
        ]
    elif red.fetchone()[0] < 1 and gold >= 60:
        return [
                {
                    "sku": "MINI_RED_BARREL",
                    "quantity": 1,
                }
            ]
    elif green.fetchone()[0] < 1 and gold >= 60:
        return [
            {
                "sku": "MINI_GREEN_BARREL",
                "quantity": 1,
            }
        ]
    elif blue.fetchone()[0] < 1 and gold >= 120:
        return [
            {
                "sku": "SMALL_BLUE_BARREL",
                "quantity": 1,
            }
        ]
    elif red.fetchone()[0] < 1 and gold >= 100:
        return [
                {
                    "sku": "SMALL_RED_BARREL",
                    "quantity": 1,
                }
            ]
    elif green.fetchone()[0] < 1 and gold >= 100:
        return [
            {
                "sku": "SMALL_GREEN_BARREL",
                "quantity": 1,
            }
        ]