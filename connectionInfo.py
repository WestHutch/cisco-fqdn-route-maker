import keyring
import os
import getpass
from dotenv import load_dotenv, set_key, dotenv_values
from pathlib import Path

ENV_PATH = Path(__file__).with_name(".env")
SERVICE = "cisco-fqdn-forwarder"

def get_credentials():    
    username = keyring.get_password(SERVICE, "SWITCH_USERNAME")
    password = keyring.get_password(SERVICE, "SWITCH_PASSWORD")

    if not all([username, password]):
        return None

    return({
        "username": username, 
        "password": password
    })


def get_ips():
    load_dotenv(ENV_PATH)
    host = os.getenv('HOST')
    destination = os.getenv('DESTINATION')

    if not all([host, destination]):
        return None
    
    return({
        "host": host,
        "destination": destination
    })


def save_credentials():
    username = input("Enter the switch username: ").strip()
    password = getpass.getpass("Enter the switch password: ")
    keyring.set_password(SERVICE, "SWITCH_USERNAME", username)
    keyring.set_password(SERVICE, "SWITCH_PASSWORD", password)

    if not username or not password:
        raise ValueError("Username and password are required.")

    return({
        "username": username, 
        "password": password
    })


def save_ips():
    host = input("Enter the host switch IP: ").strip()
    destination = input("Enter the destination IP: ").strip()
    set_key(str(ENV_PATH), "HOST", host)
    set_key(str(ENV_PATH), "DESTINATION", destination)
    
    if not host or not destination:
        raise ValueError("Host IP and destination IP are required.")

    return({
            "host": host,
            "destination": destination
    })