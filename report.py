import json
import csv

DEVICES_FILE = 'devices.json'

with open(DEVICES_FILE, 'r') as json_file:
    data = json.load(json_file)



# Open or create the CSV file
with open('rp_devices.csv', mode='w', newline='') as file:
    writer = csv.writer(file)

    # Write the headers
    writer.writerow(["ID", "Name", "IP"])

    # Loop through the data and write each row
    for device in data['data']:
        writer.writerow([device["ID"], device["Name"], device["Address"]])
print("Data has been written to devices.csv")