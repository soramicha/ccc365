from sqlite3 import IntegrityError
from fastapi import APIRouter
import sqlalchemy
from src import database as db

router = APIRouter()

@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    try:
        with db.engine.begin() as connection:
            red = connection.execute(sqlalchemy.text("SELECT red_potions FROM global_inventory"))
            green = connection.execute(sqlalchemy.text("SELECT num_green_potions FROM global_inventory"))
            blue = connection.execute(sqlalchemy.text("SELECT blue_potions FROM global_inventory"))
            purple = connection.execute(sqlalchemy.text("SELECT purple_potions FROM global_inventory"))
            redtype = connection.execute(sqlalchemy.text("SELECT * FROM mypotiontypes WHERE name = 'RARA_RED'"))
            bluetype = connection.execute(sqlalchemy.text("SELECT * FROM mypotiontypes WHERE name = 'bluey_mooey'"))
            greentype = connection.execute(sqlalchemy.text("SELECT * FROM mypotiontypes WHERE name = 'GOOGOOGREEN'"))
            purpletype = connection.execute(sqlalchemy.text("SELECT * FROM mypotiontypes WHERE name = 'burple'"))
    except IntegrityError:
        return "INTEGRITY ERROR!"
    """
    Each unique item combination must have only a single price.
    """
    
    # change this
    mylist = []
    bluenum = blue.fetchone()[0]
    info = bluetype.fetchone()
    if bluenum > 0:
        mylist.append({
                    "sku": info[1],
                    "name": info[1],
                    "quantity": bluenum,
                    "price": info[6],
                    "potion_type": [info[2], info[3], info[4], info[5]],
                }
            )
    rednum = red.fetchone()[0]
    info = redtype.fetchone()
    if rednum > 0:
        mylist.append(
                {
                    "sku": info[1],
                    "name": info[1],
                    "quantity": rednum,
                    "price": info[6],
                    "potion_type": [info[2], info[3], info[4], info[5]],
                }
        )
    greennum = green.fetchone()[0]
    info = greentype.fetchone()
    if greennum > 0:
        mylist.append(
                {
                    "sku": info[1],
                    "name": info[1],
                    "quantity": greennum,
                    "price": info[6],
                    "potion_type": [info[2], info[3], info[4], info[5]],
                }
        )
    purplenum = purple.fetchone()[0]
    info = purpletype.fetchone()
    if purplenum > 0:
        mylist.append(
                {
                    "sku": info[1],
                    "name": info[1],
                    "quantity": purplenum,
                    "price": info[6],
                    "potion_type": [info[2], info[3], info[4], info[5]],
                }
        )
    return mylist