import re
import os
import csv
def get_date():
    date_input = input("For a daily report, enter a date of the form DD.MM.YY,\n"
                       "For a monthly report, enter a date of the form MM.YY,\n"
                       "Enter wanted date: ")
    return date_input
def check_date(input_date):
    date_parts = input_date.split('.')
    if len(date_parts) == 2:
        # MM.YY format
        if len(date_parts[0]) == 2 and len(date_parts[1]) == 2:
            try:
                month = int(date_parts[0])
                year = int(date_parts[1])
                if 1 <= month <= 12 and 0 <= year <= 99:
                    return True
            except ValueError:
                print(f'Error!\nYour wanted date, "{wanted_date}", does not follow input description.\nPlease try again.')
                exit(-1)

    elif len(date_parts) == 3:
        # DD.MM.YY format
        if len(date_parts[0]) == 2 and len(date_parts[1]) == 2 and len(date_parts[2]) == 2:
            try:
                day = int(date_parts[0])
                month = int(date_parts[1])
                year = int(date_parts[2])
                if 1 <= day <= 31 and 1 <= month <= 12 and 0 <= year <= 99:
                    return True
            except ValueError:
                print(f'Error!\nYour wanted date, "{wanted_date}", does not follow input description.\nPlease try again.')
                exit(-1)

    return False


wanted_date = get_date()
check_date(wanted_date)

# input the path for Cibus txt files
file_path = 'G:/My Drive/Cibus_Bons_Converted'

# define variables
text_files = [f for f in os.listdir(file_path) if (f.endswith('.txt') and not f.endswith(').txt')) ]
meals = {}

for file in text_files:
    txt_file_path = f'{file_path}/{file}'
    with open(txt_file_path, encoding='utf-8') as f:
        content = f.read()

        # check for wanted date
        date = re.search(r"(\d\d\.\d\d\.\d\d)", content).group(1)
        if len(wanted_date) == 5:
            if wanted_date != date[-5:]:
                continue
        elif len(wanted_date) == 8:
            if wanted_date != date:
                continue
        else:
            print(f'Error!\nYour wanted date, "{wanted_date}", does not follow input description.\nPlease try again.')
            exit(-1)

        matches1 = re.findall(r"(.*?)\|([\w\s\']+?)(\d+)\₪?\:?", content)
        matches2 = re.findall(r"(\d)\₪.*\n(.*?)\s\|\s(\D*)((\s\:\s\:))", content)

        for match1 in matches1:
            restaurant = match1[0].strip()
            name = match1[1].strip()
            quantity = int(match1[2])
            if name in meals:
                meals[name][1] += quantity
            else:
                meals[name] = [restaurant, quantity]
        for match2 in matches2:
            restaurant = match2[1].strip()
            name = match2[2].strip()
            quantity = int(match2[0])
            if name in meals:
                meals[name][1] += quantity
            else:
                meals[name] = [restaurant, quantity]

# Define the CSV file name and path
csv_file = f'G:/My Drive/Cibus_Bons_Converted/meals_{wanted_date.replace(".", "")}.csv'

# Open the CSV file in write mode
with open(csv_file, mode='w', newline='') as file:
    # Create a CSV writer object
    writer = csv.writer(file)

    # Write the header row
    writer.writerow(['Dish Name', 'Restaurant Name', 'Quantity'])

    # Write the data rows
    for dish, data in meals.items():
        print([dish, data[0], data[1]])
        writer.writerow([dish, data[0], data[1]])
