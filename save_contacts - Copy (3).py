import gspread
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
import schedule
import time
import os
from google.auth.transport.requests import Request
import pickle
from multiprocessing import Process, Lock

lock = Lock()

def save_contact_function():
    print('Running save_contact_function')
    with lock:
        # Define last_row_processed inside the function
        global last_row_processed, customer_data

        # Google Sheets authentication
        sheet_scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        sheet_creds = ServiceAccountCredentials.from_json_keyfile_name('G:/My Drive/Google API/maidiz-main-379913-7c71420f4945.json', sheet_scope)
        sheet_client = gspread.authorize(sheet_creds)
        sheet = sheet_client.open("CibusCustomers").sheet1
        print("Connected with the Google sheet, CibusCustomers...")

        # Use the credentials to call the People API
        service = build('people', 'v1', credentials=creds)
        print("People API has been called...")

        # Create a dictionary of contacts {key = number: val = name}
        def get_contacts():
            connections = service.people().connections().list(
                resourceName='people/me',
                pageSize=2000,
                personFields='names,phoneNumbers').execute()
            contacts_dict = {}
            for person in connections.get('connections', []):
                names = person.get('names', [])
                phones = person.get('phoneNumbers', [])
                if names and phones:
                    name = names[0].get('displayName')
                    number = phones[0].get('canonicalForm', '')
                    if number:
                        contacts_dict[number] = name
            return contacts_dict

        # Check if a contact is in the dictionary
        def contact_exists(number, contact_dict):
            for key in contact_dict:
                if key == number:
                    return True
            return False

        # Create a new contact
        def create_contact(name, number):
            if contact_exists(number, contact_dict):
                print(f"The contact '{name}' with the number {number} is already exist on your account.")
                return

            person = {
                "names": [
                    {
                        "givenName": name,
                        "familyName": "מיידיז"
                    }
                ],
                "phoneNumbers": [
                    {
                        "value": number,
                        "type": "mobile"
                    }
                ]
            }

            result = service.people().createContact(body=person).execute()
            print(f"Contact created. name: {name}, number: {number} | {result['resourceName']}")

        # Get customer data from Google Sheets
        def get_customer_data():
            global last_row_processed, customer_data
            # Read rows from the last processed row
            all_data = sheet.get('A{}:D'.format(last_row_processed + 2))
            new_customer_data = {}

            if len(all_data) == 0:
                print("Nothing is new under the sun...")
                return new_customer_data

            for row in all_data:
                if len(row) >= 4:  # Ensure there are at least 4 columns in the row
                    name, number, company, address = row
                    customer_data[number] = [name, company, address]
                    new_customer_data[number] = [name, company, address]
                    last_row_processed += 1

            print('Customer data collected.')
            return new_customer_data

        # Iterating function
        def job():
            global last_row_processed
            new_customers = get_customer_data()
            for customer_number, customer_info in new_customers.items():
                name, company, address = customer_info

                # Set a default value for number
                number = str(customer_number)

                # Remove the first digit and add the '+972' prefix
                if number.startswith('5'):
                    number = '+972' + number
                elif number.startswith('05'):
                    number = '+972' + number[1:]

                # Create the contact
                create_contact(name=name, number=number)


        # Initialize global variables
        customer_data = {}
        contact_dict = get_contacts()

        # Schedule the job function to run every 30 seconds
        schedule.every(30).seconds.do(job)

        # Keep the scheduler running
        while True:
            schedule.run_pending()
            time.sleep(1)

        job()

# Create a db index
last_row_processed = 0

# Authorization process outside of the function

# API key and credentials
API_KEY = "AIzaSyBgzDHdb4SnGLc-FGWD-hrom98sI_c4fPU"
CLIENT_ID = "1035388992614-fcip9rjlurea35k0g7dvbtonrplv5bl0.apps.googleusercontent.com"
CLIENT_SECRET = "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"
SCOPE = "https://www.googleapis.com/auth/contacts"
print("API key and credentials collected.")

creds = None
if os.path.exists('token.pickle'):
    with open('token.pickle', 'rb') as token:
        creds = pickle.load(token)

if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        # Create a flow object to obtain user authorization
        flow = InstalledAppFlow.from_client_config(
            {
                "installed": {
                    "client_id": CLIENT_ID,
                    "client_secret": CLIENT_SECRET,
                    "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"],
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://accounts.google.com/o/oauth2/token",
                }
            },
            scopes=[SCOPE],
        )

        # Have the user authorize the application
        creds = flow.run_local_server()

        # Save the credentials to a file
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

        print("The user authorized the application.")

# Start the save_contact_process
save_contact_process = Process(target=save_contact_function, args=(lock,))