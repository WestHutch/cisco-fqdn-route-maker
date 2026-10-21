from netmiko import ConnectHandler
from connectionInfo import save_credentials, get_credentials, get_ips, save_ips
import argparse



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--resetCredentials", help="Reset your saved username and password", action="store_true")
    parser.add_argument("--resetIPs", help="Reset your saved host and destination IP addresses", action="store_true")
    args = parser.parse_args()

    if args.resetCredentials:
        credential_dict = save_credentials()

    if args.resetIPs:
        ips_dict = save_ips()

    credential_dict = get_credentials()
    if credential_dict is None:
        credential_dict = save_credentials()

    ips_dict = get_ips()
    if ips_dict is None:
        ips_dict = save_ips()
        
    SWITCH = {
        'device_type': 'cisco_ios',
        'host': ips_dict["host"],
        'username': credential_dict["username"],
        'password': credential_dict["password"]
    }

    print(SWITCH)

if __name__ == "__main__":
    main()