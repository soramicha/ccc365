from sqlite3 import IntegrityError
from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth
from enum import Enum
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/carts",
    tags=["cart"],
    dependencies=[Depends(auth.get_api_key)],
)

class search_sort_options(str, Enum):
    customer_name = "customer_name"
    item_sku = "item_sku"
    line_item_total = "line_item_total"
    timestamp = "timestamp"

class search_sort_order(str, Enum):
    asc = "asc"
    desc = "desc"   

@router.get("/search/", tags=["search"])
def search_orders(
    customer_name: str = "",
    potion_sku: str = "",
    search_page: str = "",
    sort_col: search_sort_options = search_sort_options.timestamp,
    sort_order: search_sort_order = search_sort_order.desc,
):
    
    result = []
    Dict = {}
    with db.engine.begin() as connection:
        if customer_name == "" and potion_sku == "":
            # ASC ORDER
            if sort_order == search_sort_order.asc:
                # TIME
                if sort_col == search_sort_options.timestamp:
                    print("sorting by time asc!")
                    rows = connection.execute(sqlalchemy.text("SELECT cart_id, customer, potion_id, gold, time, potion_name FROM search_orders ORDER BY time ASC"))
                elif sort_col == search_sort_options.line_item_total: # LINE_ITEM_TOTAL
                    print("sorting by line_item asc!")
                    rows = connection.execute(sqlalchemy.text("SELECT cart_id, customer, potion_id, gold, time, potion_name FROM search_orders ORDER BY gold ASC"))
                elif sort_col == search_sort_options.item_sku: # ITEM_SKU
                    print("sorting by item_sku asc!")
                    rows = connection.execute(sqlalchemy.text("SELECT cart_id, customer, potion_id, gold, time, potion_name FROM search_orders ORDER BY potion_name ASC"))
                elif sort_col == search_sort_options.customer_name: # NAME
                    print("sorting by name asc!")
                    rows = connection.execute(sqlalchemy.text("SELECT cart_id, customer, potion_id, gold, time, potion_name FROM search_orders ORDER BY customer ASC"))
                else: # CART_ID
                    print("sorting by cart_id asc!")
                    rows = connection.execute(sqlalchemy.text("SELECT cart_id, customer, potion_id, gold, time, potion_name FROM search_orders ORDER BY cart_id ASC"))
            
        # DESC ORDER 
            elif sort_order == search_sort_order.desc:
                # TIME
                if sort_col == search_sort_options.timestamp:
                    print("sorting by time desc!")
                    rows = connection.execute(sqlalchemy.text("SELECT cart_id, customer, potion_id, gold, time, potion_name FROM search_orders ORDER BY time DESC"))
                elif sort_col == search_sort_options.line_item_total: # LINE_ITEM_TOTAL
                    print("sorting by line_item desc!")
                    rows = connection.execute(sqlalchemy.text("SELECT cart_id, customer, potion_id, gold, time, potion_name FROM search_orders ORDER BY gold DESC"))
                elif sort_col == search_sort_options.item_sku: # ITEM_SKU
                    print("sorting by item_sku desc!")
                    rows = connection.execute(sqlalchemy.text("SELECT cart_id, customer, potion_id, gold, time, potion_name FROM search_orders ORDER BY potion_name DESC"))
                elif sort_col == search_sort_options.customer_name: # NAME
                    print("sorting by name desc!")
                    rows = connection.execute(sqlalchemy.text("SELECT cart_id, customer, potion_id, gold, time, potion_name FROM search_orders ORDER BY customer DESC"))
                else: # CART_ID
                    print("sorting by cart_id desc!")
                    rows = connection.execute(sqlalchemy.text("SELECT cart_id, customer, potion_id, gold, time, potion_name FROM search_orders ORDER BY cart_id DESC"))
        else:
            if potion_sku != "" and customer_name != "":
                rows = connection.execute(sqlalchemy.text("SELECT cart_id, customer, potion_id, gold, time, potion_name FROM search_orders WHERE UPPER(customer) LIKE UPPER(:name) AND UPPER(potion_name) LIKE UPPER(:p_name) ORDER BY potion_name, customer"), [{"name": customer_name, "p_name": potion_sku}])
            elif potion_sku != "":
                rows = connection.execute(sqlalchemy.text("SELECT cart_id, customer, potion_id, gold, time, potion_name FROM search_orders WHERE UPPER(potion_name) LIKE UPPER(:p_name) ORDER BY potion_name"), [{"p_name": potion_sku}])
            elif customer_name != "":
                rows = connection.execute(sqlalchemy.text("SELECT cart_id, customer, potion_id, gold, time, potion_name FROM search_orders WHERE UPPER(customer) LIKE UPPER(:name) ORDER BY customer"), [{"name": customer_name}])

        # get the starting id in cart_items
        for i in rows.fetchall():
            # FIX AMOUNT OF POTIONS LATER
            Dict = dict({"line_item_id": i[0], "item_sku": "1 " + i[5], "customer_name": i[1], "line_item_total": i[3], "timestamp": i[4]})
            result.append(Dict)
    print(result)
        
    """
    Search for cart line items by customer name and/or potion sku.

    Customer name and potion sku filter to orders that contain the 
    string (case insensitive). If the filters aren't provided, no
    filtering occurs on the respective search term.

    Search page is a cursor for pagination. The response to this
    search endpoint will return previous or next if there is a
    previous or next page of results available. The token passed
    in that search response can be passed in the next search request
    as search page to get that page of results.

    Sort col is which column to sort by and sort order is the direction
    of the search. They default to searching by timestamp of the order
    in descending order.

    The response itself contains a previous and next page token (if
    such pages exist) and the results as an array of line items. Each
    line item contains the line item id (must be unique), item sku, 
    customer name, line item total (in gold), and timestamp of the order.
    Your results must be paginated, the max results you can return at any
    time is 5 total line items.
    """

    return {
        "previous": "",
        "next": "",
        "results": result,
    }


class Customer(BaseModel):
    customer_name: str
    character_class: str
    level: int

@router.post("/visits/{visit_id}")
def post_visits(visit_id: int, customers: list[Customer]):
    """
    Which customers visited the shop today?
    """
    print(customers)

    return "OK"


@router.post("/")
def create_cart(new_cart: Customer):
    with db.engine.begin() as connection:
        try:
            connection.execute(sqlalchemy.text("INSERT INTO carts (customer_name) VALUES (:name)"), [{"name": new_cart.customer_name}])
        except IntegrityError:
            return "INTEGRITY ERROR!"
        else:
            cart_id = connection.execute(sqlalchemy.text("SELECT cart_id FROM carts WHERE customer_name = :name ORDER BY cart_id DESC LIMIT 1"), [{"name": new_cart.customer_name}])
    return {"cart_id": cart_id.fetchone()[0]}


class CartItem(BaseModel):
    quantity: int

@router.post("/{cart_id}/items/{item_sku}")
def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):
    with db.engine.begin() as connection:
        try:
            potion_id = connection.execute(sqlalchemy.text("SELECT id FROM mypotiontypes WHERE name = :name"), [{"name": item_sku}])
            potion_id = potion_id.fetchone()[0]
            connection.execute(sqlalchemy.text("INSERT INTO cart_items (customer_cart_id, potion_type_id, quantity) VALUES (:cart_id, :potion_id, :quantity)"), [{"cart_id": cart_id, "potion_id": potion_id, "quantity": cart_item.quantity}])
        except IntegrityError:
            return "INTEGRITY ERROR!"
    return "OK"


class CartCheckout(BaseModel):
    payment: str

@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):
    with db.engine.begin() as connection:
        try:
            # get the potion_type_id and quantity from cart_items table using the cart_id
            # retrieve the price of the potion from the mypotiontypes table
            row1 = connection.execute(sqlalchemy.text("SELECT potion_type_id, quantity FROM cart_items WHERE customer_cart_id = :cart_id"), [{"cart_id": cart_id}])
            r = row1.fetchone()
            potion_type_id = r[0]
            quantity = r[1]
            potion_name = connection.execute(sqlalchemy.text("SELECT name, cost FROM mypotiontypes WHERE id = :potion_type_id"), [{"potion_type_id": potion_type_id}])
            
            p = potion_name.fetchone()
            potion_name = p[0]
            cost = p[1]
            # purchasing one bottle at a time
            connection.execute(sqlalchemy.text("INSERT INTO ledger (gold, potions, ml, potion_type, description, cart_id) VALUES (:cost, -:potions, 0, :potion_type_id, 'sold potion', :cart_id)"), [{"cost": cost, "potion_type_id": potion_type_id, "potions": quantity, "cart_id": cart_id}])
            name = connection.execute(sqlalchemy.text("SELECT customer_name FROM carts WHERE cart_id = :id"), [{"id": cart_id}])
            connection.execute(sqlalchemy.text("INSERT INTO search_orders (customer, potion_id, gold, cart_id, potion_name) VALUES (:name ,:potion_type_id, :cost, :cart_id, :potion_name)"), [{"name": name.fetchone()[0], "cost": cost, "potion_type_id": potion_type_id, "cart_id": cart_id, "potion_name": potion_name}])
            connection.execute(sqlalchemy.text("UPDATE cart_items SET status = 'successful' WHERE customer_cart_id = :cart_id"), [{"cart_id": cart_id}])
            totalgold = cost * quantity
        except IntegrityError:
            return "INTEGRITY ERROR!"
        return {"total_potions_bought": quantity, "total_gold_paid": totalgold}