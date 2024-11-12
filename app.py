
import json
import os
import requests
import sys
from datetime import datetime
from flask import Flask, jsonify, render_template, url_for, request, redirect, flash
from dotenv import load_dotenv

from helpers import is_valid_ip, last_modified


load_dotenv()

BASE_URL = os.getenv('RP_URL')
RP_TOKEN = os.getenv('RP_TOKEN')

if not BASE_URL or not RP_TOKEN:
    print("Environment variables are not set. Ensure .env file is present")
    sys.exit()

HEADERS = {
    'Authorization': f'Custom {RP_TOKEN}',
    'Content-Type': 'application/json'
}
# Set parameters for GET requests ex. max limit for records
PARAMS = {
    'limit': 3000
}
# File where devices are downloaded into with RP refresh
DEVICES_FILE = 'devices.json'


# Create the Flask app
app = Flask(__name__)
app.config.from_object('config.DevelopmentConfig')


@app.route('/')
def index():
    """ Render Landing Page """

    updated = last_modified(DEVICES_FILE)
    return render_template('index.html', updated=updated)


@app.route('/confirm_delete', methods=['POST'])
def confirm_delete():
    """ Render Confirmation Pager after IPs are submitted """

    if request.method == "POST":
        ips = request.form.get("delete_ips").split(",")
        if ips[0] == "":
            flash("Enter IP of devices separated by comas.")
            return redirect(url_for('index'))

        if not os.path.exists(DEVICES_FILE):
            flash("Devices are not loaded. Please refresh.")
            return redirect(url_for('index'))

        with open(DEVICES_FILE, 'r') as json_file:
            data = json.load(json_file)

        devices = []
        sl_filter = ""
        not_found = []
        payloads_to_disable = {}
        for ip in ips:
            strip_ip = (ip.strip().split('/')[0])

            if not is_valid_ip(strip_ip):
                continue

            # Check if 'data' key exists and loop through the list
            if 'data' in data:
                found = False
                for entry in data['data']:
                    if entry.get('Address') == strip_ip:
                        device_dict = {
                            "device_id": entry.get('ID'),
                            "device_ip": strip_ip,
                            "device_name": entry.get('Name'),
                            "device_backup_status": entry.get('BackupStatus'),
                            "device_last_backup": entry.get('LastSuccessfulBackup')
                        }
                        devices.append(device_dict)
                        sl_filter += f"{strip_ip}$,"

                        payload_to_disable = {
                            "Name": entry.get('Name'),
                            "Disabled": True,
                            "PluginKey": entry.get('PluginKey'),
                            "PluginFields": entry.get('PluginFields'),
                            "Address": entry.get('Address'),
                            "Protocol": entry.get('Protocol'),
                            "Monitor": entry.get('Monitor')
                            }
                        payloads_to_disable[entry.get('ID')] = payload_to_disable
                        break
                else:
                    not_found.append(strip_ip)
                    sl_filter += f"{strip_ip}$,"
            else:
                print('No "data" key in the JSON file.')

    with open('payload_to_disable.json', 'w') as json_file:
        json.dump(payloads_to_disable, json_file, indent=4)

    return render_template('confirm_delete.html', devices=devices, sl_filter=sl_filter, not_found=not_found)



@app.route('/delete_devices', methods=['POST'])
def delete_devices():
    """ Logic to disable and delete devices"""

    # Retrieve the device IDs from the form data.
    device_ids = request.form.getlist('device_ids')

    with open('payload_to_disable.json', 'r') as json_file:
        data = json.load(json_file)

    for id in device_ids:
        endpoint = "/api/v2/devices"
        headers = HEADERS
        payload = data[id]

        ##### Disable device PUT ID + padload
        # print(f"PUT: {BASE_URL}{endpoint}/{id}")
        # print(payload)
        put_response = requests.put(f"{BASE_URL}{endpoint}/{id}", headers=headers, json=payload)
        if put_response.status_code == 200:
            print('Success:', put_response.json())
        else:
            print('Error:', put_response.status_code, put_response.text)


        ##### Delete device DELETE ID
        # print(f"DEL: {BASE_URL}{endpoint}/{id}")
        del_response = requests.delete(f"{BASE_URL}{endpoint}/{id}", headers=headers)
        if del_response.status_code == 204:
            print(f'Deleted Successfully {id}')
        else:
            print('Error:', del_response.status_code, del_response.text)

        
    flash(f"{len(device_ids)} devices removed successfully.")
    return redirect(url_for('index'))



@app.route('/refresh_devices', methods=['POST'])
def refresh_devices():
    """ Logic to GET devices from RP and store to json localy """
    if request.method == "POST":
        endpoint = "/api/v2/devices"
        headers = HEADERS
        params = PARAMS
        print("Refressh")
        response = requests.get(f"{BASE_URL}{endpoint}", headers=headers, params=params)

        if response.status_code == 200:
            with open(DEVICES_FILE, 'w') as json_file:
                json.dump(response.json(), json_file, indent=4)
                flash("Refresh successful.")
                return redirect(url_for('index'))
        else:
                flash("Refresh error", response.status_code, response.text)
                return redirect(url_for('index'))


# Run the app
if __name__ == '__main__':
    app.run()
