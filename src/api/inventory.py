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
            all = connection.execute(sqlalchemy.text("SELECT SUM(gold), SUM(ml), SUM(potions) FROM ledger"))
        x = all.fetchone()
    except IntegrityError:
        return "INTEGRITY ERROR!"
    return {"number_of_potions": x[2], "ml_in_barrels": x[1], "gold": x[0]}


# Gets called once a day
@router.post("/plan")
def get_capacity_plan():
    """ 
    Start with 1 capacity for 50 potions and 1 capacity for 10000 ml of potion. Each additional 
    capacity unit costs 1000 gold.
    """
    p_c = 0
    m_c = 0
    try:
        with db.engine.begin() as connection:
            gold = connection.execute(sqlalchemy.text("SELECT SUM(gold), SUM(ml), SUM(potions) FROM ledger"))
        gold = gold.fetchone()
        if gold[0] >= 1000 and gold[1] >= 19000:
            m_c = 1
        if gold[0] >= 2000 and gold [2] >= 40:
            p_c = 1
    except IntegrityError:
        return "INTEGRITY ERROR!"
    return {
        "potion_capacity": p_c,
        "ml_capacity": m_c
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
            connection.execute(sqlalchemy.text("INSERT INTO ledger (gold, description) VALUES (:total, 'purchased capacity plan')"), [{"total": total}])
    except IntegrityError:
        return "INTEGRITY ERROR!"
    return "Successfully delivered capacity plan"
