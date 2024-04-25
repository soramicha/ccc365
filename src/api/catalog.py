from sqlite3 import IntegrityError
from fastapi import APIRouter
import sqlalchemy
from src import database as db

router = APIRouter()

@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    try:
        with db.engine.begin() as connection:
            red = connection.execute(sqlalchemy.text("SELECT potions, name, cost, red, green, blue, dark FROM mypotiontypes WHERE name = 'RARA_RED'"))
            blue = connection.execute(sqlalchemy.text("SELECT potions, name, cost, red, green, blue, dark FROM mypotiontypes WHERE name = 'bluey_mooey'"))    
            green = connection.execute(sqlalchemy.text("SELECT potions, name, cost, red, green, blue, dark FROM mypotiontypes WHERE name = 'GOOGOOGREEN'"))
            purple = connection.execute(sqlalchemy.text("SELECT potions, name, cost, red, green, blue, dark FROM mypotiontypes WHERE name = 'burple'"))
    except IntegrityError:
        return "INTEGRITY ERROR!"
    """
    Each unique item combination must have only a single price.
    """
    
    # change this
    mylist = []
    blue = blue.fetchone()
    if blue[0] > 0:
        mylist.append({
                    "sku": blue[1],
                    "name": blue[1],
                    "quantity": 1,
                    "price": blue[2],
                    "potion_type": [blue[3], blue[4], blue[5], blue[6]],
                }
            )
    red = red.fetchone()
    if red[0] > 0:
        mylist.append(
                {
                    "sku": red[1],
                    "name": red[1],
                    "quantity": 1,
                    "price": red[2],
                    "potion_type": [red[3], red[4], red[5], red[6]],
                }
        )
    green = green.fetchone()
    if green[0] > 0:
        mylist.append(
                {
                    "sku": green[1],
                    "name": green[1],
                    "quantity": 1,
                    "price": green[2],
                    "potion_type": [green[3], green[4], green[5], green[6]],
                }
        )
    purple= purple.fetchone()
    if purple[0] > 0:
        mylist.append(
                {
                    "sku": purple[1],
                    "name": purple[1],
                    "quantity": 1,
                    "price": purple[2],
                    "potion_type": [purple[3], purple[4], purple[5], purple[6]],
                }
        )
    return mylist