from netmiko import ConnectHandler
from connectionInfo import save_credentials, get_credentials, get_ips, save_ips
from pathlib import Path
import os
import argparse
import dns.resolver
import json
import logging
import re
from datetime import datetime, timedelta


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--logging", help="Enable logging. Logs are deleted after 30 days.", action="store_true")
    parser.add_argument("--resetCredentials", help="Reset your saved username and password", action="store_true")
    parser.add_argument("--resetIPs", help="Reset your saved host and next hop IP addresses", action="store_true")
    parser.add_argument("--keepRoutes", help="Keep your previously made static routes from this script, even if no longer in DNS records. JSON file is still overwritten. Do not use if changing destination IP", action="store_true")
    args = parser.parse_args()

    if args.logging:
    #initiate log file
        LOGS_PATH = Path(__file__).with_name("logs")
        LOGS_PATH.mkdir(exist_ok=True)
        todaysDate = datetime.now()
        todaysLog = f"{LOGS_PATH}/log_{todaysDate.strftime('%Y%m%d')}.log"
        logging.basicConfig(filename=todaysLog, format='%(asctime)s %(levelname)s: %(message)s')
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)

        #delete logs from over 30 days ago if found
        cutoffDate = todaysDate - timedelta(days=30)
        for log_file in LOGS_PATH.glob("log_*.log"):
            try:
                if re.fullmatch(r"^log_[0-9]{8}\.log", log_file.name):
                    if log_file.name.strip("log_.") < cutoffDate.strftime('%Y%m%d'):
                        print(f"Removing old log file: {log_file}")
                        logger.info(f"Removing old log file: {log_file}")
                        log_file.unlink()
                else:
                    raise Exception(f"Error: Log file {log_file} does not match naming convention log_YYmmdd.log")
            except Exception as err:
                print(err)
                logger.error(err)

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
    connectedToSwitch = False
    try:
        configChanging = False
        dnsresults = []
        configSet = []

        #Get IPs for FQDN, and append each IP to results array
        answers = dns.resolver.resolve(ips_dict["fqdn"], "A", lifetime=10)
        for answer in answers:
            dnsresults.append(f"{answer}") #need to convert it to string in order to convert to json
            print(f"Found address: {answer}")
            if args.logging: logger.info(f"Found address: {answer}")

        #if json file exists or next hop IP changed, remove outdated routes
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
        
        #Connect to switch, send commands, save
        if configChanging:
            print("Connecting...")
            if args.logging: logger.info("Connecting...")
            net_connect = ConnectHandler(**SWITCH)
            print("Connected")
            if args.logging: logger.info("Connected")
            connectedToSwitch = True
            print("Sending commands")
            if args.logging: logger.info("Sending commands")
            cliOutput = net_connect.send_config_set(configSet)
            print(cliOutput)
            if args.logging: logger.info(cliOutput)
            cliOutput = cliOutput.lower()
            if ("invalid" in cliOutput) or ("incomplete" in cliOutput) or ("ambiguous" in cliOutput) or ("failed" in cliOutput):
                print("Switch error. Not saving. Please check your running config")
                if args.logging: logger.warning("Switch error. Not saving. Please check your running config")
                raise RuntimeError("Switch reported a configuration error.")
            else:
                print("Writing memory...")
                if args.logging: logger.info("Writing memory...")
                cliOutput = net_connect.send_command('write memory')
                print(cliOutput)
                if args.logging: logger.info(cliOutput)
        else:
            print("No configuration changes made.")
            if args.logging: logger.info("No configuration changes made.")
        
        #save IPs to json file
        recordsDict = {
            "destination": ips_dict["destination"],
            "records": dnsresults
        }
        recordsJson = json.dumps(recordsDict, indent=4)
        with open(JSON_PATH, "w") as json_f:
            json_f.write(recordsJson)
    except Exception as err:
        print(err)
        if args.logging: logger.error(err)
    finally:
        if (net_connect is not None) and connectedToSwitch:
            print("Disconnecting...")
            if args.logging: logger.info("Disconnecting...")
            net_connect.disconnect()
            print("Disconnected")
            if args.logging: logger.info("Disconnected")

if __name__ == "__main__":
    main()