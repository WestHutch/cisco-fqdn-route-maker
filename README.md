## cisco-fqdn-route-maker
> A Python CLI tool that resolves an FQDN to its DNS A records and manages corresponding static routes on a Cisco switch. Automatically removes outdated routes and adds routes for newly resolved IP addresses.

## Requirements
* Python 3.9 or greater
* Cisco switch with SSH configured
* Working DNS resolution

## Setup

1. Download this repo, and extract the zip to a location of your choice.
2. In the CLI, navigate to this folder then setup a virtual environment with the following commands:

| Windows (Command Prompt)    | Mac/Linux |
| -------- | ------- |
| `py -m venv .venv`<br/>`.venv\Scripts\activate.bat`  | `python3 -m venv .venv`<br/>`source .venv/bin/activate`    |

3. Install the required packages.

```
pip install -r requirements.txt
```

4. Run the program.
> Note: some systems may use py, python, or python3 to execute Python scripts.

| Windows (Command Prompt)    | Mac/Linux |
| -------- | ------- |
| `py main.py`  | `python3 main.py`    |

## Quickstart

For subsequent uses, simply navigate to the project in the CLI and run the following:

| Windows (Command Prompt)    | Mac/Linux |
| -------- | ------- |
| `.venv\Scripts\activate.bat`<br/>`py main.py`  | `source .venv/bin/activate`<br/>`python3 main.py`    |

## Workflow

1. On the first run, you will be asked to enter the following:
  * username to connect to the switch with
  * password
  * host switch IP address
  * next hop IP address
  * FQDN

2. Connect to the host switch.

```
Connecting...
Connected
```

3. Resolve the FQDN to its DNS A records. These are stored in `saved_records.json`

```
Found address: 1.1.1.3
Found address: 1.1.1.4
```

4. Remove obsolete routes previously managed by the script, if applicable.

```
Sending commands
configure terminal
Enter configuration commands, one per line.  End with CNTL/Z.
MY-SWITCH(config)#no ip route 1.1.1.1 255.255.255.255 10.0.0.1
MY-SWITCH(config)#no ip route 1.1.1.2 255.255.255.255 10.0.0.1
```

5. Add routes for each IP address found, save the configuration, and disconnect.

```
MY-SWITCH(config)#ip route 1.1.1.3 255.255.255.255 10.0.0.1
MY-SWITCH(config)#ip route 1.1.1.4 255.255.255.255 10.0.0.1
MY-SWITCH(config)#end
MY-SWITCH#
Writing memory...
Config saved.
Disconnecting...
Disconnected
```

Note: If no changes have been made to the DNS records since your last run, the program will not make any changes to the switch.

## Arguments

| Argument    | Description |
| -------- | ------- |
| --logging or -l  | Enable logging. Logs are deleted after 30 days.    |
| --resetCredentials  | Reset your saved username and password    |
| --resetIPs | Reset your saved host and next hop IP addresses     |
| --keepRoutes    | Keep your previously made static routes from this script, even if no longer in DNS records. JSON file is still overwritten. Do not use if changing next hop IP    |


⚠️ Warning: Using `--keepRoutes` while changing the next hop IP with `--resetIPs` can lead to multiple static routes for the same source IPs.

## Failure
Upon any failure, the program will disconnect from the switch without saving its configuration. If no DNS records were found, the connection will immediately be terminated.
> ⚠️ Warning: If failure occurs after/during configuration, commands may still be sent to the running configuration.
