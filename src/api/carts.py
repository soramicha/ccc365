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
    search_page: str = "1",
    sort_col: search_sort_options = search_sort_options.timestamp,
    sort_order: search_sort_order = search_sort_order.desc,
):
    
    search_page = int(search_page)
    sql = "SELECT cart_id, customer, potion_id, gold, time, potion_name FROM search_orders "
    # both name and potion name are used
    if potion_sku != "" and customer_name != "":
        print("both potion name and customer name searched")
        sql += f"WHERE UPPER(potion_name) LIKE UPPER('{potion_sku}') AND UPPER(customer) LIKE UPPER('{customer_name}')"
    elif potion_sku != "":
        print("potion_sku searched")
        sql += f"WHERE UPPER(potion_name) LIKE UPPER('{potion_sku}')"
    elif customer_name != "":
        print("customer name searched")
        sql += f"WHERE UPPER(customer) LIKE UPPER('{customer_name}')"
    
    # sort through time
    if sort_col == search_sort_options.timestamp:
        sql += " ORDER BY time "
    # sort through customer name
    elif sort_col == search_sort_options.customer_name:
        sql += " ORDER BY customer "
    # sort through potion name
    elif sort_col == search_sort_options.item_sku:
        sql += " ORDER BY potion_name "
    # sort through gold
    elif sort_col == search_sort_options.line_item_total:
        sql += " ORDER BY gold "
        
    if sort_order == search_sort_order.asc:
        sql += " ASC"
    else:
        sql += "DESC"
    
    offset = 0
    if search_page != 1:
        offset = 5 * (search_page - 1)
    sql += " OFFSET " + str(offset) + " LIMIT 5"
    result = []
    Dict = {}
    print(sql)
    # execute the command
    with db.engine.begin() as connection:
        rows = connection.execute(sqlalchemy.text(sql))
        count = connection.execute(sqlalchemy.text("SELECT COUNT(potion_name) FROM search_orders"))
        count = count.fetchone()[0]
        for i in rows.fetchall():
            # FIX AMOUNT OF POTIONS LATER
            Dict = dict({"line_item_id": i[0], "item_sku": "1 " + i[5], "customer_name": i[1], "line_item_total": i[3], "timestamp": i[4]})
            result.append(Dict)
    print(result)
    
    prev = 1
    next = 1
    print(str(search_page) + " is the search page")
    # if it's on a page more than one and there are still more results
    if search_page >= 1 and search_page < (int(count/5) + 1):
        next = search_page + 1
        prev = search_page - 1
        if search_page == 1:
            print("doesn't show prev button")
            prev = 0
    # if it's at the max page
    elif search_page > 1 and search_page == (int(count/5) + 1):
        prev = search_page - 1
    print("count/5 is" + str(int(count/5) + 1) + "and search page is " + str(search_page))
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
        "previous": prev,
        "next": next,
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