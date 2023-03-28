import re
import os
import csv

# input the path for Cibus files
file_path = 'G:/My Drive/Cibus_Bons_Converted'

# define variables
text_files = [f for f in os.listdir(file_path) if f.endswith(f'.txt')]
orders = {}

for file in text_files:
    txt_file_path = f'{file_path}/{file}'
    with open(txt_file_path, encoding='utf-8') as f:
        content = f.read()
        date = re.search(r"(\d\d\.\d\d\.\d\d)", content).group(1)
        req_time = re.search(r"(\d\d:\d\d)", content).group(1)
        pack_size = int(re.search(r"(\d\d?) מתוך", content).group(1))
        packID = re.search(r"(\d{7}\d?\d?) 'הדפסת", content).group(1)
        company = re.search(r"\d\n([\w\s]+[\w\.]+?) :חברה", content).group(1)
        address = re.search(r" :חברה\n(.*)\n", content).group(1)

        amounts = re.findall(r'\nכ הזמנה"סה\d₪ (\d\d\d?\d?\.\d)\n', content)
        if len(amounts) != pack_size:
            amounts = [0 for d in range(pack_size)]
        else:
            amounts = [float(a) for a in amounts]

        custom_data = re.findall(r'0(5\d\d{7}) (.*)\n(\d{8}\d?\d?)', content)
        if len(custom_data) != pack_size:
            custom_data = ['error' for d in range(pack_size)]
        else:
            phones = [str('972-')+str(item[0]) for item in custom_data]
            names = [item[1] for item in custom_data]
            orderIDs = [item[2] for item in custom_data]

        for i in range(len(orderIDs)):
            orders[orderIDs[i]] = [orderIDs[i], packID, pack_size, date, req_time, company, address,
                                   names[i], phones[i], amounts[i]]
            # print(f'{orderIDs[i]} : {orders[orderIDs[i]]}')

# open a CSV file for writing
with open(f'G:/My Drive/Cibus_Bons_Converted/orders{date}.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)

    # write header row
    writer.writerow(
        ['Order ID', 'Pack ID', 'Pack Size', 'Date', 'Req Time', 'Company', 'Address', 'Customer Name', 'Phone',
         'Amount [ILS]'])

    # write data rows
    for order in orders.values():
        writer.writerow(order)
