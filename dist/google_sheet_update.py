# This code access a google sheet that serves as a db.
# The sheet is of the form : name, number, company, address.
# It also has access to a live folder with txt files representing incoming orders.
# It updates the google sheet when an incoming order is of a new customer.

import gspread
from oauth2client.service_account import ServiceAccountCredentials

# use creds to create a client to interact with the Google Drive API
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

creds = ServiceAccountCredentials.from_json_keyfile_name('G:/My Drive/Google API/maidiz-main-379913-7c71420f4945.json', scope)
client = gspread.authorize(creds)

# Find a workbook by name and open the first sheet
sheet = client.open("CibusCustomers").sheet1

# Extract all records from the sheet and store them in a dictionary
records = sheet.get_all_records()
customers_dict = {}
for record in records:
    customers_dict[record['number']] = [record['name'], record['company'], record['address']]

# Example customer record to add/update
new_customer = {'name': 'John Doe', 'number': '555-1234', 'company': 'ACME', 'address': '123 Main St'}

# Check if customer already exists in the database by their phone number
if new_customer['number'] in customers_dict:
    # Update details in the dictionary
    customers_dict[new_customer['number']] = [new_customer['name'], new_customer['company'], new_customer['address']]
    # Update the corresponding row in the spreadsheet
    row_num = list(customers_dict.keys()).index(new_customer['number']) + 2
    sheet.update(f"A{row_num}:D{row_num}", [new_customer['name'], new_customer['number'], new_customer['company'], new_customer['address']])
else:
    # Customer does not exist, add them to the dictionary
    customers_dict[new_customer['number']] = [new_customer['name'], new_customer['company'], new_customer['address']]
    # Add a new row to the spreadsheet with the customer's details
    sheet.insert_row([new_customer['name'], new_customer['number'], new_customer['company'], new_customer['address']], index=2)

# Print the updated dictionary and spreadsheet data
records = sheet.get_all_records()
customers_dict = {}
for record in records:
    customers_dict[record['number']] = [record['name'], record['company'], record['address']]
print(customers_dict)
