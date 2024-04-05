from fastapi import APIRouter

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
        if result != 0:
            # put in catalog
            
def database_connection_url():
    dotenv.load_dotenv()

    return os.environ.get("POSTGRES_URI")

engine = create_engine(database_connection_url(), pool_pre_ping=True)

# changes made

router = APIRouter()

@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    """
    Each unique item combination must have only a single price.
    """

    return [
            {
                "sku": "RED_POTION_0",
                "name": "red potion",
                "quantity": 1,
                "price": 50,
                "potion_type": [100, 0, 0, 0],
            }
        ]