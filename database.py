import sqlite3
import os
from CONSTS import DB_NAME
import json


def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    return conn


def setup_database():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            phone_number TEXT UNIQUE,
            email TEXT,
            company TEXT,
            address TEXT
        )
    """)

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

    conn.commit()
    conn.close()


def add_order(conn, order_data):
    """
    Adds a new order to the orders table in the database.

    Args:
        conn: A database connection object.
        order_data: A dictionary containing the order details.

    Returns:
        None
    """

    cur = conn.cursor()
    cur.execute("""
        INSERT INTO orders (
            customer_id, customer_phone, customer_email, customer_name, customer_address, customer_company,
            package_id, order_id, order_content, order_note, order_asap, order_expected,
            order_amount, order_source, order_status, timestamp
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        order_data['customer_id'],
        order_data['customer_phone'],
        order_data['customer_email'],
        order_data['customer_name'],
        order_data['customer_address'],
        order_data['customer_company'],
        order_data['package_id'],
        order_data['order_id'],
        json.dumps(order_data['order_content']),
        order_data['order_note'],
        order_data['order_asap'],
        order_data['order_expected'],
        order_data['order_amount'],
        order_data['order_source'],
        order_data['order_status'],
        order_data['timestamp']
    ))
    conn.commit()


def upsert_customer(conn, order_data):
    """
    Adds a new customer to the database if the customer's phone number is not already in the database.
    If the phone number is already in the database, updates the existing customer's name, company, address,
    and/or email if any of those fields have changed. If none of those fields have changed, raises a
    ValueError with an error message.

    Args:
        conn: A database connection object.
        order_data: A dictionary containing the customer's name, phone number, company, address, and email.

    Returns:
        None
    """
    name = order_data['customer_name']
    number = order_data['customer_phone']
    company = order_data['customer_company']
    address = order_data['customer_address']
    email = order_data['customer_email']

    # Check if the phone number already exists in the database
    cur = conn.cursor()
    cur.execute("SELECT * FROM customers WHERE phone_number = ?", (number,))
    existing_customer = cur.fetchone()

    if existing_customer:
        update_existing = False
        e_name, e_email, e_address = existing_customer[1], existing_customer[3], existing_customer[5]
        # Try to match at least one additional field: email, address, or name
        if email and e_email == email:
            update_existing = True
        elif address and e_address == address:
            update_existing = True
        elif name and name.lower() in e_name.lower():
            update_existing = True

        if update_existing:
            # Update the existing customer
            cur.execute("""
                UPDATE customers
                SET name = ?, company = ?, address = ?, email = ?
                WHERE phone_number = ?
            """, (name, company, address, email, number))
            conn.commit()

            # Get the customer_id of the updated customer
            customer_id = existing_customer[0]

        else:
            # If no match found, mark the phone number as void and raise an error
            void_number = None
            cur.execute("INSERT INTO customers (name, phone_number, company, address, email) VALUES (?, ?, ?, ?, ?)",
                        (name, void_number, company, address, email))
            conn.commit()
            raise ValueError(f"New customer's phone number conflicts with an existing customer: {number}")

    # Add new customer to the database
    else:
        cur.execute("INSERT INTO customers (name, phone_number, company, address, email) VALUES (?, ?, ?, ?, ?)",
                    (name, number, company, address, email))
        conn.commit()

        # Get the customer_id of the newly inserted customer
        cur.execute("SELECT id FROM customers WHERE phone_number = ?", (number,))
        customer_id = cur.fetchone()[0]

    return customer_id


def view_orders_data(conn):
    """
    Retrieves and prints all orders data from the orders table in the database.

    Args:
        conn: A database connection object.
    """
    cur = conn.cursor()
    cur.execute("SELECT * FROM orders")
    orders = cur.fetchall()

    for order in orders:
        print(f"Order ID:   \t\t{order[0]}\n"
              f"Customer ID:\t\t{order[1]}\n"
              f"Phone       \t\t{order[2]}\n"
              f"Email       \t\t{order[3] if order[3] else None}\n"
              f"Name        \t\t{order[4]}\n"
              f"Address     \t\t{order[5]}\n"
              f"Company     \t\t{order[6]}\n"
              f"Package     \t\t{order[7]}\n"
              f"Source order ID\t\t{order[8]}\n"
              f"Note        \t\t{order[10] if order[10] else None}\n"
              f"Asap        \t\t{order[11]}\n"
              f"Expected    \t\t{order[12]}\n"
              f"Amount      \t\t{order[13]}\n"
              f"Source      \t\t{'Cibus' if order[14] == 0 else 'ERROR'}\n"
              f"Status      \t\t{order[15]}\n"
              f"Timestamp   \t\t{order[16]}"
              )
        order_content = json.loads(order[9])  # Assuming that order_content is the 9th field in the table
        print("Order Content:", order_content)

        print("\n")


# Call this function to set up the database initially
setup_database()

if __name__ == "__main__":
    conn = get_db_connection()
    view_orders_data(conn=conn)
