import ipaddress
import os

from datetime import datetime


def is_valid_ip(ip_str: str) -> bool:
    try:
        # Try to convert the string to an IP address object (IPv4 or IPv6)
        ip = ipaddress.ip_address(ip_str)
        return True  # No exception means it's a valid IP
    except ValueError:
        return False  # Raised if `ip_str` is not a valid IP


def last_modified(file_path: str):
    if os.path.exists(file_path):

        # Get the last modified timestamp of the file
        file_last_modified_timestamp = os.path.getmtime(file_path)
        last_update_datetime = datetime.fromtimestamp(file_last_modified_timestamp)
        # Format the datetime for display
        return last_update_datetime.strftime("%Y-%m-%d %H:%M:%S")
    else:
        return False