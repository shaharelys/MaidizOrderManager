# Import necessary modules and sub-programs
import CONSTS
import db_manager
import contacts_manager
import trip_manager
from order_manager import site_connection, close_connection, process_package
from contacts_manager import create_contact
from googleapiclient.discovery import build
import ctypes
import platform
from messages_manager import send_whatsapp_message
from datetime import time, datetime
import threading
from trip_manager import manage_trip
from datetime import datetime
import time

# Shared data structure for communication between main thread and input thread
trip_data = {
    "last_order_time": None,
    "number_of_delivery_persons": None,
}


def prevent_sleep():
    if platform.system() == 'Windows':
        ES_CONTINUOUS = 0x80000000
        ES_SYSTEM_REQUIRED = 0x00000001
        ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS | ES_SYSTEM_REQUIRED)


def manage_package(service, contact_dict, customers_dict):

    # Create structure and and check for new orders on the website
    package = process_package()

    if package is None:
        print("Error: Received invalid package. Unable to process and manage the order.")
        return

    for order_data in package:
        # Check if the order should be accepted and update its status
        # order_data['status'] = determine_order_status_and_update(order_data)
        """above is to be deleted - moved to order_manager"""

        name, number, flag = order_data['customer_name'], order_data['customer_phone'], False

        # Check if contact exists and create it if it doesn't
        if number not in contact_dict:
            flag = True
            print(f"Creating contact with the number - {number}, and the name - {name}..")
            create_contact(name, number, service, contact_dict)

        # Check if customer exists on the database
        if number in customers_dict:
            if flag:
                print(f"Error, the number {number} is already on your db, but was'nt on your account.")

            # Update customer details in the database
            db_manager.update_customer_details(order_data, customers_dict)

        else:
            # Create a new customer in the database
            print("Adding new customer to the database..")
            customers_dict = db_manager.create_new_customer(order_data, customers_dict)

        # TODO: Add the new order to the customer's orders on the db
        # db_manager.add_order_to_customer_orders(new_order)

        sids = send_whatsapp_message(order_data)

    return package, contact_dict, customers_dict


def ask_about_next_trip():
    # TODO: Make this a popup
    while True:
        # Ask the admin for the last time to include orders (in format "HH:MM")
        last_order_time_str = input("Enter the last time to include orders (HH:MM):")

        # Convert the input time string to a datetime object
        last_order_time = datetime.strptime(last_order_time_str, "%H:%M").time()

        # Ask the admin how many delivery persons are available
        number_of_delivery_persons: int = int(input("Enter the number of available delivery persons: "))

        # Update the trip data
        trip_data["last_order_time"] = last_order_time
        trip_data["number_of_delivery_persons"] = number_of_delivery_persons

        # Sleep for some time before asking again (e.g., 10 minutes)
        # TODO: Change this to the time the trip departs
        waiting_time_until_next_ask = 60*300
        print(f"Input has been accepted.\nWaiting {waiting_time_until_next_ask/60} minutes until next ask..")
        time.sleep(waiting_time_until_next_ask)


def main():
    # Set up any necessary configurations, like API keys or login credentials

    # Obtain the credentials and build the People API service
    creds = contacts_manager.get_credentials()
    service = build('people', 'v1', credentials=creds)

    # Load data from db and People API
    print("Loading data from database and People API..")
    customers_dict = db_manager.load_customers_from_sheet()
    contact_dict = contacts_manager.get_contacts(service)

    # Connect to orders site
    site_connection()

    print("Program started successfully!")

    # Start the input thread
    input_thread = threading.Thread(target=ask_about_next_trip, daemon=True)
    input_thread.start()

    upcoming_orders = []

    try:
        while True:
            # Process and manage the order data
            package, contact_dict, customers_dict = manage_package(service, contact_dict, customers_dict)

            for order_data in package:
                # Add the order data to the upcoming_orders list
                upcoming_orders.append(order_data)

                # Check if the last order time has been reached or exceeded
                if trip_data["last_order_time"] is not None and datetime.datetime.now().time() >= trip_data["last_order_time"]:
                    manage_trip(trip_data["number_of_delivery_persons"], customers_dict, upcoming_orders)

                    # TODO: sync this with the "wanted at" and the bool "asap" elements in the order
                    # Reset the upcoming_orders list
                    upcoming_orders = []

    except KeyboardInterrupt:
        print("Exiting the loop...")
    finally:
        close_connection()


if __name__ == "__main__":
    prevent_sleep()
    main()

