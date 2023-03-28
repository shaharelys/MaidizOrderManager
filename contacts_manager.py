import gspread
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
import schedule
import time
import os
from google.auth.transport.requests import Request
import pickle


# Create a dictionary of contacts {key = number: val = name}
def get_contacts(service):
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


def add_country_code(number, country_code="+972"):
    if number.startswith(country_code) or number.startswith('+'):
        return number
    if number.startswith('0'):
        number = number[1:]
    number_with_country_code = country_code + number
    return number_with_country_code


# Check if a contact is in the dictionary
def contact_exists(number, contact_dict):
    for key in contact_dict:
        if key == number:
            return True
    return False


# Create a new contact
def create_contact_old(name, number, service, contact_dict):
    if contact_exists(number, contact_dict):
        print(f"Error, function, contact_exists(number, contact_dict) called for existing contact.\n"
              f"number\t:\t{number}")
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

    # Update the contact_dict with the new contact
    contact_dict[number] = name


def create_contact(name, number, service, contact_dict):

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

    # Update contact_dict
    contact_dict[number] = name


def get_credentials():
    # API key and credentials
    CLIENT_ID = "1035388992614-fcip9rjlurea35k0g7dvbtonrplv5bl0.apps.googleusercontent.com"
    CLIENT_SECRET = "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"
    SCOPE = "https://www.googleapis.com/auth/contacts"

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

    return creds


def build_people_service(creds):
    service = build('people', 'v1', credentials=creds)
    return service


# Call the functions
creds = get_credentials()
people_service = build_people_service(creds)
