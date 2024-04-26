from sqlite3 import IntegrityError
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import math
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/inventory",
    tags=["inventory"],
    dependencies=[Depends(auth.get_api_key)],
)

@router.get("/audit")
def get_inventory():
    # query in the actual data
    try:
        with db.engine.begin() as connection:
            all = connection.execute(sqlalchemy.text("SELECT SUM(ml), SUM(potions) FROM mypotiontypes"))
            gold = connection.execute(sqlalchemy.text("SELECT gold FROM global_inventory"))
        x = all.fetchone()
    except IntegrityError:
        return "INTEGRITY ERROR!"
    return {"number_of_potions": x[1], "ml_in_barrels": x[0], "gold": gold.fetchone()[0]}


# Gets called once a day
@router.post("/plan")
def get_capacity_plan():
    """ 
    Start with 1 capacity for 50 potions and 1 capacity for 10000 ml of potion. Each additional 
    capacity unit costs 1000 gold.
    """
    
    try:
        with db.engine.begin() as connection:
            gold = connection.execute(sqlalchemy.text("SELECT gold FROM global_inventory"))
            
        if gold.fetchone()[0] >= 1500:
            return {
                "potion_capacity": 0,
                "ml_capacity": 1
            }
    except IntegrityError:
        return "INTEGRITY ERROR!"
    return {
        "potion_capacity": 0,
        "ml_capacity": 0
    }

class CapacityPurchase(BaseModel):
    potion_capacity: int
    ml_capacity: int

# Gets called once a day
@router.post("/deliver/{order_id}")
def deliver_capacity_plan(capacity_purchase : CapacityPurchase, order_id: int):
    """ 
    Start with 1 capacity for 50 potions and 1 capacity for 10000 ml of potion. Each additional 
    capacity unit costs 1000 gold.
    """
    try:
        with db.engine.begin() as connection:
            total = 1000 * (capacity_purchase.potion_capacity + capacity_purchase.ml_capacity)
            connection.execute(sqlalchemy.text("UPDATE global_inventory SET gold = gold - 1000 * :total"), [{"total": total}])
    except IntegrityError:
        return "INTEGRITY ERROR!"
    return "Successfully delivered capacity plan"
