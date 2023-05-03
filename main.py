# Import necessary modules and sub-programs
import CONSTS
import database
import contacts_manager
import routs_builder
from order_manager import site_connection, close_connection, process_package
from order_manager import print_to_screen, print_package, back_home, ask_human
from contacts_manager import create_contact
from googleapiclient.discovery import build
import ctypes
import platform
from messages_manager import send_whatsapp_message
from datetime import time, datetime
import threading
from routs_builder import build_routs
from datetime import datetime
import time
from stickers_printer import manage_and_print_order_stickers
from stickers_printer import print_accepted_orders_stickers_and_push_status


def prevent_sleep():
    if platform.system() == 'Windows':
        ES_CONTINUOUS = 0x80000000
        ES_SYSTEM_REQUIRED = 0x00000001
        ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS | ES_SYSTEM_REQUIRED)


def manage_package(service, contact_dict):
    # Check for new orders on the website
    package = process_package()

    # control functionality
    if package is None:
        print("Error: Received invalid package. Unable to process and manage the order.")
        return

    package_total = 0

    # Collect package data
    for order_data in package:
        name, number, = order_data['customer_name'], order_data['customer_phone']

        # Check if contact exists and create it if it doesn't
        if number not in contact_dict:
            print(f"Creating new contact:\t{name}\t{number}\t...")
            create_contact(name, number, service, contact_dict)

        # Connect to the database and upsert the customer
        conn = database.get_db_connection()

        # Check if an order with the same source_order_id already exists
        if database.order_exists(conn, order_data['order_id']):
            print(f"Order with the same source_order_id ({order_data['order_id']}) already exists on the db.")
            return package, contact_dict

        try:
            customer_id = database.upsert_customer(conn, order_data)
            # Add the new order to the orders table on the db
            order_data['customer_id'] = customer_id
            database.add_order(conn, order_data)

        except ValueError as e:
            print(e)
        finally:
            conn.close()

        package_total += float(order_data['order_amount'].strip(' ₪'))
        # package_orders_ids.append(db_order_id)

    # Assess package
    if package_total < CONSTS.MINIMUM_ORDER_AMOUNT:
        ret = ask_human(package_total)

    if package_total >= CONSTS.MINIMUM_ORDER_AMOUNT or ret == CONSTS.ACCEPTED:
        for order_data in package:
            send_whatsapp_message(order_data)

        # Print functions below
        print_to_screen(package)
        print_package()

        # Get back to the orders page
        back_home()

    elif ret == CONSTS.REJECTED:
        # TODO
        pass

    return package, contact_dict


def main():
    # Set up any necessary configurations, like API keys or login credentials

    # Obtain the credentials and build the People API service
    creds = contacts_manager.get_credentials()
    service = build('people', 'v1', credentials=creds)

    # Load data from db and People API
    print("Loading data from database and People API..")
    contact_dict = contacts_manager.get_contacts(service)

    # Connect to orders site
    site_connection()

    print("Program started successfully!")

    try:
        while True:
            # Process and manage the order data
            package, contact_dict = manage_package(service, contact_dict)  # TODO: may need only "manage_package(service, contact_dict)"

            # Print stickers
            # print_accepted_orders_stickers_and_push_status()

    except KeyboardInterrupt:
        print("Exiting the loop...")
    finally:
        close_connection()


if __name__ == "__main__":
    prevent_sleep()
    main()

