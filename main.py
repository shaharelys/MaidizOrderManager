# Import necessary modules and sub-programs
from cibus_scraper import site_connection, process_order, close_connection
import contacts_manager
from contacts_manager import contact_exists, create_contact, add_country_code
from contacts_manager import people_service, get_contacts
from googleapiclient.discovery import build
# import db_manager
# import trip_manager
# import sms_notifications
import time
import ctypes
import platform


def prevent_sleep():
    if platform.system() == 'Windows':
        ES_CONTINUOUS = 0x80000000
        ES_SYSTEM_REQUIRED = 0x00000001
        ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS | ES_SYSTEM_REQUIRED)


def process_and_manage_order(order_data, service, contact_dict):

    # TODO: add a column in database for rejected orders due to smaller than minimum amount.

    if order_data is not None:
        # Check if customer exists in the database
        customer_exists = True  # customer_database_manager.check_customer_in_db(new_order['customer_phone'])

        if customer_exists:

            # Update customer details in the database
            # customer_database_manager.update_customer_details(new_order)

            # Check if contact exists and create if it doesn't
            name = order_data['customer_name']
            number = order_data['customer_phone']

            # Add country code to the number if necessary
            number = add_country_code(number)

            if contact_exists(number, contact_dict):
                print(f"As expected, the number {number} is already listed on your account under the contact - {name}.")

            else:
                print(f"Error, the number {number} is already listed on your db, but not on your account,\n"
                      f"Creating contact with the name - {name}..")
                create_contact(name, number, service, contact_dict)


        else:
            # Create a new customer in the database
            # customer_database_manager.create_new_customer(new_order)

            # Save the customer as a contact using the People API
            name = order_data['customer_name']
            number = order_data['customer_phone']

            if not contact_exists(number, contact_dict):
                create_contact(name, number, service, contact_dict)

        # Add the new order to the customer's orders
        # customer_database_manager.add_order_to_customer_orders(new_order)

        # Assign the order to a trip
        # trip_manager.assign_order_to_trip(new_order)

        # Send an order confirmation SMS to the customer
        # sms_notifications.send_order_confirmation_sms(new_order)
    else:
        print("Error: Received invalid order_data. Unable to process and manage the order.")


def main():
    # Set up any necessary configurations, like API keys or login credentials

    # Connect to orders site
    site_connection()

    # Obtain the credentials and build the People API service
    creds = contacts_manager.get_credentials()
    service = build('people', 'v1', credentials=creds)
    contact_dict = contacts_manager.get_contacts(service)

    try:
        while True:
            # Check for new orders on the website

            order_data = process_order()

            """
            # TESTING
            print("skipping process_order() for testing..")

            order_data = {
                'order_id': '12345',
                'customer_name': 'Alon Goldenberg',
                'customer_phone': '0506574059',
            }
            """

            # Process and manage the order data
            process_and_manage_order(order_data, service, contact_dict)

    except KeyboardInterrupt:
        print("Exiting the loop...")
    finally:
        close_connection()


if __name__ == "__main__":
    prevent_sleep()
    main()