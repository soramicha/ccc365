from sqlite3 import IntegrityError
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
    
    # mixing only 1 potion
    
    with db.engine.begin() as connection:
        try:
            purplergbd = connection.execute(sqlalchemy.text("SELECT red, green, blue, dark FROM mypotiontypes WHERE name = 'burple'"))
            bluergbd = connection.execute(sqlalchemy.text("SELECT red, green, blue, dark FROM mypotiontypes WHERE name = 'bluey_mooey'"))
            redrgbd = connection.execute(sqlalchemy.text("SELECT red, green, blue, dark FROM mypotiontypes WHERE name = 'RARA_RED'"))
            greenrgbd = connection.execute(sqlalchemy.text("SELECT red, green, blue, dark FROM mypotiontypes WHERE name = 'GOOGOOGREEN'"))
            purple = purplergbd.fetchone()
            blue = bluergbd.fetchone()
            red = redrgbd.fetchone()
            green = greenrgbd.fetchone()
        except IntegrityError:
            return "INTEGRITY ERROR!"
        else:
            if potions_delivered[0].potion_type == [green[0], green[1], green[2], green[3]]: # if it's green
                    connection.execute(sqlalchemy.text("UPDATE mypotiontypes SET potions = potions + :potions, ml = ml - (100 * :potions) WHERE name = 'GOOGOOGREEN'"), [{"potions": potions_delivered[0].quantity}])
            if potions_delivered[0].potion_type == [red[0], red[1], red[2], red[3]]: # if it's red
                connection.execute(sqlalchemy.text("UPDATE mypotiontypes SET potions = potions + :potions, ml = ml - (100 * :potions) WHERE name = 'RARA_RED'"), [{"potions": potions_delivered[0].quantity}])
            if potions_delivered[0].potion_type == [blue[0], blue[1], blue[2], blue[3]]: # if it's blue
                connection.execute(sqlalchemy.text("UPDATE mypotiontypes SET potions = potions + :potions, ml = ml - (100 * :potions) WHERE name = 'bluey_mooey'"), [{"potions": potions_delivered[0].quantity}])
            if potions_delivered[0].potion_type == [purple[0], purple[1], purple[2], purple[3]]: # if it's purple
                connection.execute(sqlalchemy.text("UPDATE mypotiontypes SET potions = potions + :potions, ml = ml - (50 * :potions) WHERE name = 'bluey_mooey'"), [{"potions": potions_delivered[0].quantity}])
                connection.execute(sqlalchemy.text("UPDATE mypotiontypes SET potions = potions + :potions, ml = ml - (50 * :potions) WHERE name = 'RARA_RED'"), [{"potions": potions_delivered[0].quantity}])
            # update global inventory
            connection.execute(sqlalchemy.text("UPDATE global_inventory SET potions_total = potions_total + :quantity"), [{"quantity": potions_delivered[0].quantity}])
            connection.execute(sqlalchemy.text("UPDATE global_inventory SET ml_total = ml_total - (:quantity * 100)"), [{"quantity": potions_delivered[0].quantity}])
    print(f"potions delivered: {potions_delivered} order_id: {order_id}")

    return "OK"

@router.post("/plan")
def get_bottle_plan():
    """
    Go from barrel to bottle.
    """
    
    # making 1 bottle at a time!
    
    with db.engine.begin() as connection:
        try:
            ml = connection.execute(sqlalchemy.text("SELECT ml FROM mypotiontypes ORDER BY id ASC"))
        except IntegrityError:
            return "INTEGRITY ERROR!"
        else:
            # Each bottle has a quantity of what proportion of red, blue, and green potion to add.
            # Expressed in integers from 1 to 100 that must sum up to 100.

            ml = ml.fetchall()
            
            potioncount = connection.execute(sqlalchemy.text("SELECT potion_history FROM global_inventory"))
            potionhistory = potioncount.fetchone()[0]
            # purple potion
            if ml[1][0] >= 50 and ml[2][0] >= 50 and (potionhistory + 1) % 4 == 2:
                connection.execute(sqlalchemy.text("UPDATE global_inventory SET potion_history = potion_history + 1"))
                connection.execute(sqlalchemy.text("UPDATE mypotiontypes SET potions = potions + 1 WHERE name = 'burple'"))
                purplergbd = connection.execute(sqlalchemy.text("SELECT red, green, blue, dark FROM mypotiontypes WHERE name = 'burple'"))
                rgbd = purplergbd.fetchone()
                return [
                        {
                            "potion_type": [rgbd[0], rgbd[1], rgbd[2], rgbd[3]],
                            "quantity": 1,
                        }
                    ]
            elif ml[2][0] >= 100 and (potionhistory + 1) % 4 == 1:
                connection.execute(sqlalchemy.text("UPDATE global_inventory SET potion_history = potion_history + 1"))
                connection.execute(sqlalchemy.text("UPDATE mypotiontypes SET potions = potions + 1 WHERE name = 'bluey_mooey'"))
                bluergbd = connection.execute(sqlalchemy.text("SELECT red, green, blue, dark FROM mypotiontypes WHERE name = 'bluey_mooey'"))
                rgbd = bluergbd.fetchone()
                return [
                        {
                            "potion_type": [rgbd[0], rgbd[1], rgbd[2], rgbd[3]],
                            "quantity": 1,
                        }
                    ]
            
            elif ml[1][0] >= 100 and (potionhistory + 1) % 4 == 0:
                connection.execute(sqlalchemy.text("UPDATE global_inventory SET potion_history = potion_history + 1"))
                connection.execute(sqlalchemy.text("UPDATE mypotiontypes SET potions = potions + 1 WHERE name = 'RARA_RED'"))
                redrgbd = connection.execute(sqlalchemy.text("SELECT red, green, blue, dark FROM mypotiontypes WHERE name = 'RARA_RED'"))
                rgbd = redrgbd.fetchone()
                return [
                    {
                        "potion_type": [rgbd[0], rgbd[1], rgbd[2], rgbd[3]],
                        "quantity": 1,
                    }
                ]
            
            elif ml[0][0] >= 100 and (potionhistory + 1) % 4 == 3:
                connection.execute(sqlalchemy.text("UPDATE global_inventory SET potion_history = potion_history + 1"))    
                connection.execute(sqlalchemy.text("UPDATE mypotiontypes SET potions = potions + 1 WHERE name = 'GOOGOOGREEN'"))
                greenrgbd = connection.execute(sqlalchemy.text("SELECT red, green, blue, dark FROM mypotiontypes WHERE name = 'GOOGOOGREEN'"))
                rgbd = greenrgbd.fetchone()
                return [
                        {
                            "potion_type": [rgbd[0], rgbd[1], rgbd[2], rgbd[3]],
                            "quantity": 1,
                        }
                    ]
            return []

if __name__ == "__main__":
    print(get_bottle_plan())