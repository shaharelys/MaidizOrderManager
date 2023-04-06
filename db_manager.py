import gspread
import os
import re
import shutil
import time
from oauth2client.service_account import ServiceAccountCredentials
from multiprocessing import Lock
import re
import requests
from config import MAPS_API_KEY
from trip_manager import get_coordinates_from_address

# TODO: change the code to work with a real db


def get_credentials():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]

    creds = ServiceAccountCredentials.from_json_keyfile_name(
        "G:/My Drive/Google API/maidiz-main-379913-7c71420f4945.json", scope
    )
    return creds


def get_google_sheet():
    creds = get_credentials()
    client = gspread.authorize(creds)
    sheet = client.open("CibusCustomers").sheet1
    return sheet


def load_customers_from_sheet():
    sheet = get_google_sheet()
    rows = sheet.get_all_records()
    customers = {}
    for row in rows:
        phone_number = str(0) + str(row["number"])
        customers[phone_number] = {
            "name": row["name"],
            "company": row["company"],
            "address": row["address"],
        }
    return customers


def write_with_delay(sheet, func, *args, delay=1):
    time.sleep(delay)
    return func(*args)


def get_sheet():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('G:/My Drive/Google API/maidiz-main-379913-7c71420f4945.json', scope)
    client = gspread.authorize(creds)
    sheet = client.open("CibusCustomers").sheet1
    return sheet


def clean_address(address):
    # TODO: fix this to wirk with this "רח׳ אורה 5, רמת גן, ישראל קומה 7 דירה 20 , רמת גן"
    # Regular expression pattern to find relevant address parts
    pattern = re.compile(r"([\w\d\s'-]+(?:\s[\w\d'-]+)?)(?:\s\d+)(?:\s[\w\d\s'-]+)")

    # Search for a match in the input string
    match = pattern.search(address)

    # If a match is found, return the cleaned address, else return the original string
    if match:
        return match.group().strip()
    else:
        return address


def update_customer_details(order_data, customers_dict, api_key=MAPS_API_KEY):
    number = order_data['customer_phone']
    name = order_data['customer_name']
    company = order_data['company_name']
    dirty_address = order_data['customer_address']
    # TODO: add these back after debugging
    # clean_addr = clean_address(dirty_address)
    # coordinates = get_coordinates(api_key, clean_addr)

    # Update the customer details in the in-memory dictionary
    customers_dict[str(number)] = [name, company, dirty_address]  #, clean_addr, coordinates]

    # Get the sheet
    sheet = get_sheet()

    # Update the customer details in the Google Sheet
    cell = sheet.find(number)
    write_with_delay(sheet, sheet.update_cell, cell.row, 1, name)
    write_with_delay(sheet, sheet.update_cell, cell.row, 3, company)
    write_with_delay(sheet, sheet.update_cell, cell.row, 4, dirty_address)
    # TODO: add back after debugging
    # write_with_delay(sheet, sheet.update_cell, cell.row, 5, clean_addr)
    # write_with_delay(sheet, sheet.update_cell, cell.row, 6, str(coordinates))

    print(f"Updated customer details in the database: {name}, {number}, {company}, {dirty_address}") #, {clean_addr}, {coordinates}")


def create_new_customer(order_data, customers_dict, api_key=MAPS_API_KEY):
    name = order_data['customer_name']
    number = order_data['customer_phone']
    company = order_data['company_name']
    dirty_address = order_data['customer_address']
    # TODO: ...
    # clean_addr = clean_address(dirty_address)
    # coordinates = get_coordinates_from_address(clean_addr, MAPS_API_KEY)

    # Add new customer to customers_dict
    customers_dict[number] = {'name': name, 'company': company, 'dirty_address': dirty_address} , #'clean_address': clean_addr, 'coordinates': coordinates}

    # Add new customer to Google Sheet
    sheet = get_google_sheet()
    sheet.append_row([name, number, company, dirty_address]) #, clean_addr, str(coordinates)])

    return customers_dict


def update_customer_details_old(order_data, customers_dict):
    number = order_data['customer_phone']
    name = order_data['customer_name']
    company = order_data['company_name']
    address = order_data['customer_address']

    # Update the customer details in the in-memory dictionary
    customers_dict[str(number)] = [name, company, address]

    # Get the sheet
    sheet = get_sheet()

    # Update the customer details in the Google Sheet
    cell = sheet.find(number)
    write_with_delay(sheet, sheet.update_cell, cell.row, 1, name)
    write_with_delay(sheet, sheet.update_cell, cell.row, 3, company)
    write_with_delay(sheet, sheet.update_cell, cell.row, 4, address)

    print(f"Updated customer details in the database: {name}, {number}, {company}, {address}")


def create_new_customer_old(order_data, customers_dict):
    name = order_data['customer_name']
    number = order_data['customer_phone']
    company = order_data['company_name']
    address = order_data['customer_address']

    # Add new customer to customers_dict
    customers_dict[number] = {'name': name, 'company': company, 'address': address}

    # Add new customer to Google Sheet
    sheet = get_google_sheet()
    sheet.append_row([name, number, company, address])

    return customers_dict
