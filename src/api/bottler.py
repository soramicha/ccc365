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
                    connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_green_potions = num_green_potions + :potions, num_green_ml = num_green_ml - (100 * :potions)"), [{"potions": potions_delivered[0].quantity}])
            if potions_delivered[0].potion_type == [red[0], red[1], red[2], red[3]]: # if it's red
                connection.execute(sqlalchemy.text("UPDATE global_inventory SET red_potions = red_potions + :potions, red_ml = red_ml - (100 * :potions)"), [{"potions": potions_delivered[0].quantity}])
            if potions_delivered[0].potion_type == [blue[0], blue[1], blue[2], blue[3]]: # if it's blue
                connection.execute(sqlalchemy.text("UPDATE global_inventory SET blue_potions = blue_potions + :potions, blue_ml = blue_ml - (100 * :potions)"), [{"potions": potions_delivered[0].quantity}])
            if potions_delivered[0].potion_type == [purple[0], purple[1], purple[2], purple[3]]: # if it's purple
                connection.execute(sqlalchemy.text("UPDATE global_inventory SET purple_potions = purple_potions + :potions, red_ml = red_ml - (50 * :potions), blue_ml = blue_ml - (50 * :potions)"), [{"potions": potions_delivered[0].quantity}])
    
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
            green = connection.execute(sqlalchemy.text("SELECT num_green_ml FROM global_inventory"))
            red = connection.execute(sqlalchemy.text("SELECT red_ml FROM global_inventory"))
            blue = connection.execute(sqlalchemy.text("SELECT blue_ml FROM global_inventory"))
        except IntegrityError:
            return "INTEGRITY ERROR!"
        else:
            # Each bottle has a quantity of what proportion of red, blue, and green potion to add.
            # Expressed in integers from 1 to 100 that must sum up to 100.

            numblue = blue.fetchone()[0]
            numred = red.fetchone()[0]
            numgreen = green.fetchone()[0]
            
            potioncount = connection.execute(sqlalchemy.text("SELECT potion_history FROM global_inventory"))
            potionhistory = potioncount.fetchone()[0]
            # purple potion
            if numblue >= 50 and numred >= 50 and (potionhistory + 1) % 4 == 3:
                connection.execute(sqlalchemy.text("UPDATE global_inventory SET potion_history = potion_history + 1"))
                purplergbd = connection.execute(sqlalchemy.text("SELECT red, green, blue, dark FROM mypotiontypes WHERE name = 'burple'"))
                rgbd = purplergbd.fetchone()
                return [
                        {
                            "potion_type": [rgbd[0], rgbd[1], rgbd[2], rgbd[3]],
                            "quantity": 1,
                        }
                    ]
            elif numblue >= 100 and (potionhistory + 1) % 4 == 2:
                connection.execute(sqlalchemy.text("UPDATE global_inventory SET potion_history = potion_history + 1"))
                bluergbd = connection.execute(sqlalchemy.text("SELECT red, green, blue, dark FROM mypotiontypes WHERE name = 'bluey_mooey'"))
                rgbd = bluergbd.fetchone()
                return [
                        {
                            "potion_type": [rgbd[0], rgbd[1], rgbd[2], rgbd[3]],
                            "quantity": 1,
                        }
                    ]
            
            elif numred >= 100 and (potionhistory + 1) % 4 == 1:
                connection.execute(sqlalchemy.text("UPDATE global_inventory SET potion_history = potion_history + 1"))
                redrgbd = connection.execute(sqlalchemy.text("SELECT red, green, blue, dark FROM mypotiontypes WHERE name = 'RARA_RED'"))
                rgbd = redrgbd.fetchone()
                return [
                    {
                        "potion_type": [rgbd[0], rgbd[1], rgbd[2], rgbd[3]],
                        "quantity": 1,
                    }
                ]
            
            elif numgreen >= 100 and (potionhistory + 1) % 4 == 4:
                connection.execute(sqlalchemy.text("UPDATE global_inventory SET potion_history = potion_history + 1"))     
                greenrgbd = connection.execute(sqlalchemy.text("SELECT red, green, blue, dark FROM mypotiontypes WHERE name = 'GOOGOOGREEN'"))
                rgbd = greenrgbd.fetchone()
                return [
                        {
                            "potion_type": [rgbd[0], rgbd[1], rgbd[2], rgbd[3]],
                            "quantity": 1,
                        }
                    ]
            connection.execute(sqlalchemy.text("UPDATE global_inventory SET potion_history = potion_history + 1"))
            return [
                    {
                        "potion_type": [0, 0, 0, 0],
                        "quantity": 0,
                    }
                ]

if __name__ == "__main__":
    print(get_bottle_plan())