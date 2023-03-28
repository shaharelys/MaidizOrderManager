from googleapiclient.discovery import build
from google.oauth2 import service_account

# Path to the JSON key file
key_path = 'G:/My Drive/Google API/maidiz-1st-project-afc7930d3cd3.json'

# Create credentials object
credentials = service_account.Credentials.from_service_account_file(
    key_path,
    scopes=['https://www.googleapis.com/auth/contacts']
)

# Build the service object
service = build('people', 'v1', credentials=credentials)

# Define the contact
person = {
    'names': [{
        'givenName': 'John',
        'familyName': 'Doe2'
    }],
    'emailAddresses': [{
        'value': 'johndoe@example.com'
    }]
}

# Create the contact
result = service.people().createContact(body=person).execute()

# Print the result
print(result)
