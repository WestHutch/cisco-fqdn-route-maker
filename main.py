from netmiko import ConnectHandler
from connectionInfo import save_credentials, get_credentials, get_ips, save_ips
import argparse
import dns.resolver


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

    net_connect = ConnectHandler(**SWITCH)
    answers = dns.resolver.resolve(f"{ips_dict["fqdn"]}", "A")
    for answer in answers:
        net_connect.send_config_set([f'ip route {answer} 255.255.255.255 {ips_dict["destination"]}'])
        print(f'Route created from {answer} to {ips_dict["destination"]}')
    print("Saving config...")
    net_connect.send_command('write memory')
    print("Config saved. Disconnecting...")
    net_connect.disconnect()
    print("Disconnected")

    #still need to save these to json

    #if json exists...
        #for each old ip, see if its in the new list of answers
            #no? remove the route
            #yes? nothing
        #for each new ip, see if its in the old list
            #no? add a new route for it FUNCTION
            #yes? nothing
    #else...
        #for each new ip, make route FUNCTION
    #overwrite old json w new
    

if __name__ == "__main__":
    main()