from netmiko import ConnectHandler
from connectionInfo import save_credentials, get_credentials, get_ips, save_ips
from pathlib import Path
import os
import argparse
import dns.resolver
import json


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--resetCredentials", help="Reset your saved username and password", action="store_true")
    parser.add_argument("--resetIPs", help="Reset your saved host and destination IP addresses. DO NOT USE WITH keepRoutes", action="store_true")
    parser.add_argument("--keepRoutes", help="Keep your previously made static routes from this script, even if no longer in DNS record, JSON file is still overwritten. DO NOT USE WITH resetIPs", action="store_true")
    args = parser.parse_args()

    if args.resetCredentials:
        credential_dict = save_credentials()
    else:
        credential_dict = get_credentials()

    while credential_dict is None:
        credential_dict = save_credentials()

    if args.resetIPs:
        ips_dict = save_ips()
    else:
        ips_dict = get_ips()
    
    while ips_dict is None:
        ips_dict = save_ips()
        
    SWITCH = {
        'device_type': 'cisco_ios',
        'host': ips_dict["host"],
        'username': credential_dict["username"],
        'password': credential_dict["password"]
    }

    net_connect = None
    try:
        #connect to switch and get IPs for FQDN
        print("Connecting...")
        net_connect = ConnectHandler(**SWITCH)
        print("Connected")
        configChanging = False
        answers = dns.resolver.resolve(ips_dict["fqdn"], "A", lifetime=10)
        dnsresults = []
        configSet = []

        #for each IP from FQDN, append that IP to results array
        for answer in answers:
            dnsresults.append(f"{answer}") #need to convert it to string in order to convert to json

        #if json file exists or destination IP changed, remove outdated routes
        JSON_PATH = Path(__file__).with_name("saved_records.json")
        if os.path.isfile(JSON_PATH):
            with open(JSON_PATH, "r") as json_f:
                data = json.load(json_f)
                destination_changed = data["destination"] != ips_dict["destination"]
                for stored_ip in data["records"]:
                    if destination_changed or (stored_ip not in dnsresults):
                        if not args.keepRoutes:
                            configSet.append(f'no ip route {stored_ip} 255.255.255.255 {data["destination"]}')
                            configChanging = True
                #for each new IP from FQDN, add a route if not previously added
                for dnsresult in dnsresults:
                    if (dnsresult not in data["records"]) or destination_changed:
                        configSet.append(f'ip route {dnsresult} 255.255.255.255 {ips_dict["destination"]}')
                        configChanging = True
        else:
            #for each new IP from FQDN, add a route
            for dnsresult in dnsresults:
                configSet.append(f'ip route {dnsresult} 255.255.255.255 {ips_dict["destination"]}')
                configChanging = True
        
        
        #Send commands, save
        if configChanging:
            print("Sending commands")
            cliOutput = net_connect.send_config_set(configSet)
            print(cliOutput)
            cliOutput = cliOutput.lower()
            if ("invalid" in cliOutput) or ("incomplete" in cliOutput) or ("ambiguous" in cliOutput) or ("failed" in cliOutput):
                print("Switch error. Not saving")
                raise RuntimeError("Switch reported a configuration error.")
            else:
                print("Writing memory...")
                net_connect.send_command('write memory')
                print("Config saved.")
        else:
            print("No configuration changes made.")
        
        #save IPs to json file
        recordsDict = {
            "destination": ips_dict["destination"],
            "records": dnsresults
        }
        recordsJson = json.dumps(recordsDict, indent=4)
        with open(JSON_PATH, "w") as json_f:
            json_f.write(recordsJson)
    finally:
        if net_connect is not None:
            print("Disconnecting...")
            net_connect.disconnect()
            print("Disconnected")

if __name__ == "__main__":
    main()