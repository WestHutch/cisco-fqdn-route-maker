import keyring
import os
import getpass
from dotenv import load_dotenv, set_key, dotenv_values
from pathlib import Path

ENV_PATH = Path(__file__).with_name(".env")
SERVICE = "cisco-fqdn-forwarder"

def get_credentials():
    load_dotenv(ENV_PATH)
    host = os.getenv('HOST')
    username = keyring.get_password(SERVICE, "SWITCH_USERNAME")
    password = keyring.get_password(SERVICE, "SWITCH_PASSWORD")

    if not all([host, username, password]):
        return None

    return({
        "host": host,
        "username": username, 
        "password": password
    })

def save_credentials():
    host = input("Enter the switch IP: ").strip()
    username = input("Enter the switch username: ").strip()
    password = getpass.getpass("Enter the switch password: ")
    set_key(str(ENV_PATH), "HOST", host)
    keyring.set_password(SERVICE, "SWITCH_USERNAME", username)
    keyring.set_password(SERVICE, "SWITCH_PASSWORD", password)

    if not host or not username or not password:
        raise ValueError("Host, username, and password are required.")

    return({
        "host": host,
        "username": username, 
        "password": password
    })

