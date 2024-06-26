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
    with db.engine.begin() as connection:
        try:
            purplergbd = connection.execute(sqlalchemy.text("SELECT red, green, blue, dark FROM mypotiontypes WHERE name = 'burple'"))
            bluergbd = connection.execute(sqlalchemy.text("SELECT red, green, blue, dark FROM mypotiontypes WHERE name = 'bluey_mooey'"))
            redrgbd = connection.execute(sqlalchemy.text("SELECT red, green, blue, dark FROM mypotiontypes WHERE name = 'RARA_RED'"))
            greenrgbd = connection.execute(sqlalchemy.text("SELECT red, green, blue, dark FROM mypotiontypes WHERE name = 'GOOGOOGREEN'"))
            yellowrgbd = connection.execute(sqlalchemy.text("SELECT red, green, blue, dark FROM mypotiontypes WHERE name = 'yeeLOW'"))
            purple = purplergbd.fetchone()
            blue = bluergbd.fetchone()
            red = redrgbd.fetchone()
            green = greenrgbd.fetchone()
            yellow = yellowrgbd.fetchone()
        except IntegrityError:
            return "INTEGRITY ERROR!"
        else:
            for i in potions_delivered:
                if i.potion_type == [green[0], green[1], green[2], green[3]]: # if it's green
                    print("is making green!")
                    connection.execute(sqlalchemy.text("INSERT INTO ledger (gold, potions, ml, potion_type, description) VALUES (0, :potions, -:ml, 1, 'bottled green potion')"), [{"potions": i.quantity, "ml": 100 * i.quantity}])
                if i.potion_type == [yellow[0], yellow[1], yellow[2], yellow[3]]: # if it's yellow
                    print("is making yellow!")
                    connection.execute(sqlalchemy.text("INSERT INTO ledger (gold, potions, ml, potion_type, description) VALUES (0, :potions, 0, 5, 'bottled yellow potion')"), [{"potions": i.quantity}])
                    connection.execute(sqlalchemy.text("INSERT INTO ledger (gold, potions, ml, potion_type, description) VALUES (0, 0, -:ml, 2, 'helped make yellow potion')"), [{"ml": 50 * i.quantity}])
                    connection.execute(sqlalchemy.text("INSERT INTO ledger (gold, potions, ml, potion_type, description) VALUES (0, 0, -:ml, 1, 'helped make yellow potion')"), [{"ml": 50 * i.quantity}])
                if i.potion_type == [red[0], red[1], red[2], red[3]]: # if it's red
                    print("is making red!")
                    connection.execute(sqlalchemy.text("INSERT INTO ledger (gold, potions, ml, potion_type, description) VALUES (0, :potions, -:ml, 2, 'bottled red potion')"), [{"potions": i.quantity, "ml": 100 * i.quantity}])
                if i.potion_type == [blue[0], blue[1], blue[2], blue[3]]: # if it's blue
                    print("is making blue!")
                    connection.execute(sqlalchemy.text("INSERT INTO ledger (gold, potions, ml, potion_type, description) VALUES (0, :potions, -:ml, 3, 'bottled blue potion')"), [{"potions": i.quantity, "ml": 100 * i.quantity}])
                if i.potion_type == [purple[0], purple[1], purple[2], purple[3]]: # if it's purple
                    print("is making purple!")
                    connection.execute(sqlalchemy.text("INSERT INTO ledger (gold, potions, ml, potion_type, description) VALUES (0, :potions, 0, 4, 'bottled purple potion')"), [{"potions": i.quantity, "ml": 100 * i.quantity}])
                    connection.execute(sqlalchemy.text("INSERT INTO ledger (gold, potions, ml, potion_type, description) VALUES (0, 0, -:ml, 2, 'helped make purple potion')"), [{"ml": 50 * i.quantity}])
                    connection.execute(sqlalchemy.text("INSERT INTO ledger (gold, potions, ml, potion_type, description) VALUES (0, 0, -:ml, 3, 'helped make purple potion')"), [{"ml": 50 * i.quantity}])
                connection.execute(sqlalchemy.text("UPDATE global_inventory SET potion_history = potion_history + 1"))
    print(f"potions delivered: {potions_delivered} order_id: {order_id}")

    return "OK"

@router.post("/plan")
def get_bottle_plan():
    """
    Go from barrel to bottle.
    """
    
    with db.engine.begin() as connection:
        try:
            ml_green = connection.execute(sqlalchemy.text("SELECT COALESCE(SUM(ml), 0) FROM ledger WHERE potion_type = 1"))
            ml_red = connection.execute(sqlalchemy.text("SELECT COALESCE(SUM(ml), 0) FROM ledger WHERE potion_type = 2"))
            ml_blue = connection.execute(sqlalchemy.text("SELECT COALESCE(SUM(ml), 0) FROM ledger WHERE potion_type = 3"))
        except IntegrityError:
            return "INTEGRITY ERROR!"
        else:
            # Each bottle has a quantity of what proportion of red, blue, and green potion to add.
            # Expressed in integers from 1 to 100 that must sum up to 100.

            ml_green = ml_green.fetchone()
            ml_red = ml_red.fetchone()
            ml_blue = ml_blue.fetchone()
            
            potioncount = connection.execute(sqlalchemy.text("SELECT potion_history FROM global_inventory"))
            potionhistory = potioncount.fetchone()[0]
            quantity = 1
            mylist = []
            b = ml_blue[0]
            r = ml_red[0]
            g = ml_green[0]
            # purple potion
            if ml_blue[0] >= 50 and ml_red[0] >= 50 or (potionhistory % 4 == 2 and ml_red[0] >= 50 and ml_blue[0] >= 50):
                    purplergbd = connection.execute(sqlalchemy.text("SELECT red, green, blue, dark FROM mypotiontypes WHERE name = 'burple'"))
                    rgbd = purplergbd.fetchone()
                    if ml_red[0] >= 500 and ml_blue[0] >= 500:
                        quantity = 10
                    mylist.append(
                            {
                                "potion_type": [rgbd[0], rgbd[1], rgbd[2], rgbd[3]],
                                "quantity": quantity,
                            }
                    )
                    # get updated stats
                    b -= 50 * quantity
                    r -= 50 * quantity
            # added yeeLOW potion
            if g >= 50 and r >= 50 or (potionhistory % 4 == 2 and r >= 50 and g >= 50):
                    yellowrgbd = connection.execute(sqlalchemy.text("SELECT red, green, blue, dark FROM mypotiontypes WHERE name = 'yeeLOW'"))
                    rgbd = yellowrgbd.fetchone()
                    if r >= 500 and g >= 500:
                        quantity = 10
                    else:
                        quantity = 1
                    mylist.append(
                            {
                                "potion_type": [rgbd[0], rgbd[1], rgbd[2], rgbd[3]],
                                "quantity": quantity,
                            }
                    )
                    # get updated stats
                    g -= 50 * quantity
                    r -= 50 * quantity
            if b >= 100 or (potionhistory % 4 == 1 and b >= 100):
                    bluergbd = connection.execute(sqlalchemy.text("SELECT red, green, blue, dark FROM mypotiontypes WHERE name = 'bluey_mooey'"))
                    rgbd = bluergbd.fetchone()
                    if b >= 500:
                        quantity = 10
                    else:
                        quantity = 1
                    mylist.append(
                            {
                                "potion_type": [rgbd[0], rgbd[1], rgbd[2], rgbd[3]],
                                "quantity": quantity,
                            }
                        )
                    b -= 100 * quantity
            if r >= 100 or (potionhistory % 4 == 0 and r >= 100):
                    redrgbd = connection.execute(sqlalchemy.text("SELECT red, green, blue, dark FROM mypotiontypes WHERE name = 'RARA_RED'"))
                    rgbd = redrgbd.fetchone()
                    if r >= 500:
                        quantity = 10
                    else:
                        quantity = 1
                    mylist.append(
                        {
                            "potion_type": [rgbd[0], rgbd[1], rgbd[2], rgbd[3]],
                            "quantity": quantity,
                        }
                    )
                    r -= 100 * quantity
            if g >= 100 or (potionhistory % 4 == 3 and g >= 100):
                    greenrgbd = connection.execute(sqlalchemy.text("SELECT red, green, blue, dark FROM mypotiontypes WHERE name = 'GOOGOOGREEN'"))
                    rgbd = greenrgbd.fetchone()
                    if g >= 500:
                        quantity = 10
                    else:
                        quantity = 1
                    mylist.append(
                            {
                                "potion_type": [rgbd[0], rgbd[1], rgbd[2], rgbd[3]],
                                "quantity": quantity,
                            }
                        )
                    g -= 100 * quantity
            print("remaining colored ml: blue: " + str(b) + " green: " + str(g) + " red: " + str(r))
            return mylist

if __name__ == "__main__":
    print(get_bottle_plan())