import sqlite3
import json
from datetime import datetime, timedelta, date
from CONSTS import MOCK
from CONSTS import DB_NAME
from CONSTS import REFUNDED, REJECTED, WAITING, ACCEPTED, PENDING, QUEUED, PREPARING, DISPATCHED, FULFILLED
from CONSTS import BUFFER, ASAP_BUFFER
from CONSTS import DISH_TAGS
import ast
import matplotlib.pyplot as plt
import numpy as np


def fetch_orders_by_status(status):
    """
    Fetches orders from the database with the given status code.
    """
    # Connect to the SQLite database
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Fetch orders with the specified status code
    cursor.execute("SELECT * FROM orders WHERE order_status = ?", (status,))
    orders = cursor.fetchall()

    # Close the database connection
    cursor.close()
    conn.close()

    return orders


def fetch_order_by_id(order_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
    order = cursor.fetchone()
    conn.close()

    return order


def update_order_status(order_id, new_status):
    """
    Updates the status of an order in the database.
    """
    # Connect to the SQLite database
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Update the order status in the database
    cursor.execute("UPDATE orders SET order_status = ? WHERE id = ?", (new_status, order_id))
    print(f"order {order_id} status updated to {new_status}")
    # Commit the changes and close the database connection
    conn.commit()
    cursor.close()
    conn.close()


def asses_orders_status(status=ACCEPTED):
    """
    Filters orders based on the 'order_expected' and 'order_asap' fields, and set their  stage as PENDING or QUEUED
    """
    orders = fetch_orders_by_status(status)
    for o in orders:
        order_asap, order_expected = o[11], datetime.strptime(o[12], "%H:%M")
        current_time = datetime.now()
        buffered_time = current_time + timedelta(minutes=BUFFER)  # 105 minutes buffer
        asap_buffered_time = current_time + timedelta(minutes=ASAP_BUFFER)  # 160 minutes buffer

        order_expected_datetime = current_time.replace(hour=order_expected.hour, minute=order_expected.minute)

        if order_expected_datetime <= buffered_time:
            update_order_status(o[0], new_status=QUEUED)
        elif order_expected_datetime <= asap_buffered_time and order_asap:
            update_order_status(o[0], new_status=QUEUED)
        else:
            update_order_status(o[0], new_status=PENDING)


def asses_pending_orders_status(status=PENDING):
    """
    Filters orders based on the 'order_expected' and 'order_asap' fields, and set their  stage as PENDING or QUEUED
    """
    orders = fetch_orders_by_status(status)
    for o in orders:
        order_asap, order_expected = o[11], datetime.strptime(o[12], "%H:%M")
        current_time = datetime.now()
        buffered_time = current_time + timedelta(minutes=BUFFER)  # 105 minutes buffer
        asap_buffered_time = current_time + timedelta(minutes=ASAP_BUFFER)  # 160 minutes buffer

        order_expected_datetime = current_time.replace(hour=order_expected.hour, minute=order_expected.minute)

        if order_expected_datetime <= buffered_time:
            update_order_status(o[0], new_status=QUEUED)
        elif order_expected_datetime <= asap_buffered_time and order_asap:
            update_order_status(o[0], new_status=QUEUED)


def count_dishes_and_sides(status=QUEUED):
    orders = fetch_orders_by_status(status)
    content_list = []

    for o in orders:
        item = ast.literal_eval(o[9])
        content_list.extend(item)

    dish_and_side_count = {}

    for item in content_list:
        dish = item['dish']
        count = item['count']
        sides = item['sides']

        if dish not in dish_and_side_count:
            dish_and_side_count[dish] = {'count': count, 'tag': DISH_TAGS.get(dish, -1)}
        else:
            dish_and_side_count[dish]['count'] += count

        for side in sides:
            if side not in dish_and_side_count:
                dish_and_side_count[side] = {'count': count, 'tag': DISH_TAGS.get(side, -1)}
            else:
                dish_and_side_count[side]['count'] += count

    return dish_and_side_count


def print_orders_content_summary(status=QUEUED):
    counted = count_dishes_and_sides(status)

    for k, v in counted.items():
        print(f"{v}\t:\t{k}")


# test function
def testing_print(orders):
    for o in orders:
        print(#f"{[o[i] for i in range(len(o))]}\n"
              #f"Status: {o[-2]}\n"
              f"Expected: {o[-5]}\n"
              #f"ASAP: {'True' if o[-6] else 'False'}\n"
        )

    print('*'*200)


def heap_by_order_time(orders):
    times = []
    for o in orders:
        times.append(o[-5])

    # Convert the strings to datetime objects and extract the hours
    hours = [datetime.strptime(t, "%H:%M").hour for t in times]

    # Calculate the counts for each bin
    counts, _ = np.histogram(hours, bins=range(25))

    # Calculate the total number of orders
    total_orders = len(hours)

    # Create the histogram
    n, bins, patches = plt.hist(hours, bins=range(25), edgecolor='black', align='left', rwidth=0.8)

    # Annotate the bars with the percentage value
    for i in range(len(n)):
        percentage = (counts[i] / total_orders) * 100
        plt.annotate(f"{percentage:.1f}%", (bins[i] + 0.2, counts[i] + 0.5), fontsize=6)

    # Set the x-axis labels and limits
    plt.xticks(range(24))
    plt.xlim(-0.5, 23.5)

    # Set the titles and labels
    plt.title("Order Times Distribution")
    plt.xlabel("Hour of the Day")
    plt.ylabel("Number of Orders")

    # Show the plot
    plt.show()


# test function
def create_or_erase_db():
    """
    Erases or creates the database by deleting all records from the orders table.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            customer_phone TEXT,
            customer_email TEXT,
            customer_name TEXT,
            customer_address TEXT,
            customer_company TEXT,
            package_id INTEGER,
            order_id INTEGER,
            order_content TEXT,
            order_note TEXT,
            order_asap BOOLEAN,
            order_expected TEXT,
            order_amount REAL,
            order_source INTEGER,
            order_status INTEGER,
            timestamp TEXT,
            FOREIGN KEY (customer_id) REFERENCES customers (id)
        )
    """)

    cursor.execute("DELETE FROM orders")
    conn.commit()

    cursor.close()
    conn.close()


# test function
def insert_mock_orders(mock_orders):
    """
    Inserts mock orders into the database.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    for order in mock_orders:
        cursor.execute("""
            INSERT INTO orders (id, customer_id, customer_phone, customer_email, customer_name, customer_address,
            customer_company, package_id, order_id, order_content, order_note, order_asap, order_expected,
            order_amount, order_source, order_status, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (order['id'], order['customer_id'], order['customer_phone'], order['customer_email'], order['customer_name'],
             order['customer_address'], order['customer_company'], order['package_id'], order['order_id'], json.dumps(order['order_content']),
             order['order_note'], int(order['order_asap']), order['order_expected'], float(order['order_amount'].strip('$')),
             order['order_source'], order['order_status'], order['timestamp']))

    conn.commit()
    cursor.close()
    conn.close()


# test function
def fetch_all_orders():
    """
    Fetches orders from the database with the given status code.
    """
    # Connect to the SQLite database
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Fetch orders with the specified status code
    cursor.execute("SELECT * FROM orders")
    orders = cursor.fetchall()

    # Close the database connection
    cursor.close()
    conn.close()

    # Your existing code to fetch orders here
    print(f"Orders fetched: {len(orders)}")  # Add this line

    return orders


# Test the flow of moving orders from ACCEPTED to PENDING or QUEUED
if __name__ == "__main__":
    turn_rej_list = []
    # turn_ref_list = []

    for oid in turn_rej_list:
        update_order_status(order_id=oid, new_status=REJECTED)

    #for oid in turn_ref_list:
    #    update_order_status(order_id=oid, new_status = REFUNDED)


    if MOCK:
        # create_or_erase_db()
        # Insert mock orders into the test database
        # insert_mock_orders(mock_orders)
        pass

    # Fetch all orders
    # all_orders = fetch_all_orders()

    # print(f"Orders fetched: {len(all_orders)}")
    # print(f"Average order amount: {avg_order_amount:.2f}")

    # Fetch waiting orders
    # waiting_orders = fetch_orders_by_status(WAITING)

    # Fetch accepted orders
    # accepted_orders = fetch_orders_by_status(ACCEPTED)

    # Move orders to PENDING or QUEUED
    # asses_orders_status(accepted_orders)

    # Fetch updated orders from the database
    # pending_orders = fetch_orders_by_status(PENDING)
    # queued_orders = fetch_orders_by_status(QUEUED)

    if False:
        print("ALL ORDERS:\n")
        testing_print(orders=all_orders)

        print("WAITING ORDERS:\n")
        # testing_print(orders=waiting_orders)

        print("ACCEPTED ORDERS:\n")
        testing_print(orders=accepted_orders)

        print("PENDING ORDERS:\n")
        testing_print(orders=pending_orders)

    # print("QUEUED ORDERS:\n")
    # testing_print(orders=queued_orders)
    # heap_by_order_time(orders=queued_orders)
    # print_orders_content_summary()

