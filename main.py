from netmiko import ConnectHandler
from credentials import save_credentials, get_credentials




def main():
    credential_dict = get_credentials()
    if credential_dict is None:
        credential_dict = save_credentials()
        
    SWITCH = {
        'device_type': 'cisco_ios',
        'host': credential_dict["host"],
        'username': credential_dict["username"],
        'password': credential_dict["password"]
    }

    print(SWITCH)

if __name__ == "__main__":
    main()