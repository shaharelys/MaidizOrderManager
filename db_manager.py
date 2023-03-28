import gspread
import os
import re
import shutil
import time
from oauth2client.service_account import ServiceAccountCredentials
from multiprocessing import Lock

def write_with_delay(sheet, func, *args, delay=1):
    time.sleep(delay)
    return func(*args)

def update_db_function():
    print('Running update_db_function')

    lock = Lock()
    # Use creds to create a client to interact with the Google Drive API
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']

    creds = ServiceAccountCredentials.from_json_keyfile_name('G:/My Drive/Google API/maidiz-main-379913-7c71420f4945.json', scope)
    client = gspread.authorize(creds)

    # Find a workbook by name and open the first sheet
    sheet = client.open("CibusCustomers").sheet1

    # Extract and print all of the values
    list_of_hashes = sheet.get_all_records()

    # Create a dictionary from the rows in the sheet, where the keys are the customer numbers
    customers_dict = {}
    for row in list_of_hashes:
        customers_dict[str(0)+str(row['number'])] = [row['name'], row['company'], row['address']]

    # Input the path for Cibus files
    file_path = 'G:/My Drive/Cibus_Bons_Converted'
    checked_path = 'G:/My Drive/Cibus_Bons_Converted_Checked'

    while True:
        # Define variables
        text_files = [f for f in os.listdir(file_path) if f.endswith(f'.txt')]

        for file in text_files:
            txt_file_path = f'{file_path}/{file}'
            print(f"Processing file: {txt_file_path}")
            with open(txt_file_path, encoding='utf-8') as f:
                content = f.read()
                number = re.search(r"(\d{8}\d?\d?)", content).group(1)
                company = re.search(r"\d\n([\w\s]+[\w\.]+?) :חברה", content).group(1)
                address = re.search(r" :חברה\n(.*)\n", content).group(1)
                name = re.search(r'0(5\d\d{7}) (.*)\n(\d{8}\d?\d?)', content).group(2)

                with lock:
                    if number not in customers_dict:
                        # Add new customer to dictionary
                        customers_dict[str(number)] = [name, company, address]
                        print(f"Adding new customer to the database: {name}, {number}, {company}, {address}")
                        # Add new customer to Google Sheet
                        write_with_delay(sheet, sheet.append_row, [name, number, company, address])
                    else:
                        # Update customer details in dictionary
                        customers_dict[str(number)] = [name, company, address]
                        print(f"Updating customer details in the database: {name}, {number}, {company}, {address}")
                        # Update customer details in Google Sheet
                        cell = sheet.find(number)
                        write_with_delay(sheet, sheet.update_cell, cell.row, 1, name)
                        write_with_delay(sheet, sheet.update_cell, cell.row, 3, company)
                        write_with_delay(sheet, sheet.update_cell, cell.row, 4, address)

            # Move the processed file to the checked folder
            shutil.move(txt_file_path, f'{checked_path}/{file}')
            print(f"Moved file {file} to the checked folder")

        # Wait for 60 seconds before checking again
        print("Waiting for new files...")
        time.sleep(30)
