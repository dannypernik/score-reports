"""
the goal of this file is to read the json score report, and update the connected
google sheet
"""
import os.path
import json
from google.oauth2.service_account import Credentials  # Import this to use the credentials from a JSON file
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/drive.file"]  # See, edit, create, and delete only the specific Google Drive files you use with this app.

# The ID and range of a sample spreadsheet.
# SAMPLE_SPREADSHEET_ID = "1ajmfNzTbyNB6D-js1fod9nSMzSrVy8Mwtn89uelhzyA"  # Practice SAT sample data

def extract_values_from_json(json_data):
    reading_writing_modules = {}
    math_modules = {}
    
    # Extract= Reading & Writing data
    for module, questions in json_data['answers']['reading_writing']['module'].items():
        module_values = []
        for q_num, data in questions.items():
            module_values.append([f'{module}.{q_num}', data['your_answer'].split(';')[0]])
        reading_writing_modules[module] = module_values
    
    # get Math data
    for module, questions in json_data['answers']['math']['module'].items():
        module_values = []
        for q_num, data in questions.items():
            module_values.append([f'{module}.{q_num}', data['your_answer']])
        math_modules[module] = module_values
    
    return reading_writing_modules, math_modules

def batch_update_values(spreadsheet_id, range_name, value_input_option, _values):
    # Load the credentials from the service account file
    creds = Credentials.from_service_account_file('credentials.json', scopes=SCOPES) ##credential is failing right now
    try:
        service = build("sheets", "v4", credentials=creds)

        data = [
            {"range": range_name, "values": _values},
        ]
        body = {"valueInputOption": value_input_option, "data": data}
        result = (
            service.spreadsheets()
            .values()
            .batchUpdate(spreadsheetId=spreadsheet_id, body=body)
            .execute()
        )
        print(f"{result.get('totalUpdatedCells')} cells updated.")
        return result
    except HttpError as error:
        print(f"An error occurred: {error}")
        return error

def main():
    with open('example_test_score.json') as f:
        data = json.load(f)
    
    reading_writing_modules, math_modules = extract_values_from_json(data)
    
    # Define the ranges for each module in the Google Sheet
    reading_writing_ranges = {
        "1": "C5:C31",  # Module 1 range
        "2": "G5:G31",  # Module 2 range
        "3": "K5:K31"   # Module 3 range
    }
    
    math_ranges = {
        "1": "C36:C57",  # Module 1 range
        "2": "G36:G57",  # Module 2 range
        "3": "K36:K57"   # Module 3 range
    }
    
    # Update Reading & Writing modules
    for module, values in reading_writing_modules.items():
        if values:
            batch_update_values(
                "1BgQxJF1op104P6E4MnbHJn7X1kMbIEFar-G46E2yhtk",  # Spreadsheet ID
                reading_writing_ranges[module],  # Range for the specific module
                "USER_ENTERED",
                values,
            )
    
    # Update Math modules
    for module, values in math_modules.items():
        if values:
            batch_update_values(
                "1BgQxJF1op104P6E4MnbHJn7X1kMbIEFar-G46E2yhtk",  # Spreadsheet ID
                math_ranges[module],  # Range for the specific module
                "USER_ENTERED",
                values,
            )

if __name__ == "__main__":
    main()
