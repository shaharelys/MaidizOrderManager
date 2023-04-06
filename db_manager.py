import sqlite3
import os
from CONSTS import DB_NAME


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
            company TEXT,
            address TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            order_data TEXT,
            FOREIGN KEY (customer_id) REFERENCES customers (id)
        )
    """)

    conn.commit()
    conn.close()


def add_order(conn, customer_id, order_data):
    cur = conn.cursor()
    cur.execute("INSERT INTO orders (customer_id, order_data) VALUES (?, ?)", (customer_id, order_data))
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
    company = order_data['company_name']
    address = order_data['customer_address']
    email = order_data['customer_email']

    # Check if the phone number already exists in the database
    cur = conn.cursor()
    cur.execute("SELECT * FROM customers WHERE phone_number = ?", (number,))
    existing_customer = cur.fetchone()

    if existing_customer:
        update_existing = False

        # Try to match at least one additional field: email, address, or name
        if email and existing_customer['email'] == email:
            update_existing = True
        elif address and existing_customer['address'] == address:
            update_existing = True
        elif name and name.lower() in existing_customer['name'].lower():
            update_existing = True

        if update_existing:
            # Update the existing customer
            cur.execute("""
                UPDATE customers
                SET name = ?, company = ?, address = ?, email = ?
                WHERE phone_number = ?
            """, (name, company, address, email, number))
            conn.commit()
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

    return


# Call this function to set up the database initially
setup_database()
