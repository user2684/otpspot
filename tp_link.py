#!/usr/bin/python
import sys
import re
import time
import requests
import base64
import copy

import config

# variables
url = "http://"+config.router["ip"]+"/cgi?"
cookies = {"Authorization":"Basic "+base64.b64encode(config.router["username"]+":"+config.router["password"])}
headers = {
        "Origin":"http://"+config.router["ip"],
        "Referer":"http://"+config.router["ip"]+"/",
        "User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.87 Safari/537.36"
}

# parse a result set and return an array of entry
def parse(data,re_line,re_entry):
        result = []
        lines = data.split("\n")
        for line in lines:
                # match the entry start
                m1 = re.match(re_line,line)
                # store the id
                if m1: id = m1.group(1)
                # match the value
                m2 = re.match(re_entry,line)
                if m2 and id is not None:
                        key = m2.group(1)
                        # for managed entries
                        if key.startswith("_") and key.endswith("_"):
                                split = key.split("_")
                                value = {}
                                # long entry
                                if len(split) == 5:
                                        value["description"] = split[1]
                                        value["mac"] = split[2]
                                        value["expire"] = int(split[3])
                                        value["id"] = str(id)
                                # short entry
                                elif len(split) == 3:
                                        value["mac"] = split[1]
                                        value["id"] = str(id)
                                result.append(value)
                        id = None
        return result

# parse firewall rules
def parse_firewall_rules(data):
        return parse(data,"\[(\d+),\d+,\d+,\d+,\d+,\d+\]\d+","ruleName=(.+)")

# parse hosts
def parse_hosts(data):
        return parse(data,"\[(\d+),\d+,\d+,\d+,\d+,\d+\]\d+","entryName=(.+)")

# parse wireless entries
def parse_wireless_macs(data):
        return parse(data,"\[\d+,\d+,(\d+),\d+,\d+,\d+\]\d+","X_TPLINK_Description=(.+)")
# commands
commands = {
        "wireless_list" : {
                "request_id": "5",
                "data" : """[LAN_WLAN_MACTABLEENTRY#0,0,0,0,0,0#1,1,0,0,0,0]0,3\r
                X_TPLINK_Enabled\r
                X_TPLINK_MACAddress\r
                X_TPLINK_Description\r
                """,
                "parse": parse_wireless_macs
        },
        "wireless_add" : {
                "request_id": "3",
                "data": """[LAN_WLAN_MACTABLEENTRY#0,0,0,0,0,0#1,1,0,0,0,0]0,3\r
                X_TPLINK_Enabled=1\r
                X_TPLINK_Description=__1__\r
                X_TPLINK_MACAddress=__2__\r
                """
        },
        "wireless_delete": {
                "request_id": "4",
                "data": """[LAN_WLAN_MACTABLEENTRY#1,1,__1__,0,0,0#0,0,0,0,0,0]0,0\r
                """
        },
        "host_add": {
                "request_id": "3",
                "data": """[INTERNAL_HOST#0,0,0,0,0,0#0,0,0,0,0,0]0,3\r
                type=1\r
                entryName=__1__\r
                mac=__2__\r
                """
        },
        "host_delete": {
                "request_id": "4",
                "data": """[INTERNAL_HOST#__1__,0,0,0,0,0#0,0,0,0,0,0]0,0\r
                """
        },
        "host_list": {
                "request_id": "5",
                "data": """[INTERNAL_HOST#0,0,0,0,0,0#0,0,0,0,0,0]0,0\r
                """,
                "parse": parse_hosts
        },
        "firewall_add": {
                "request_id": "3",
                "data": """[RULE#0,0,0,0,0,0#0,0,0,0,0,0]0,8\r
                ruleName=__1__\r
                internalHostRef=__2__\r
                externalHostRef=\r
                scheduleRef=\r
                action=0\r
                enable=1\r
                direction=1\r
                protocol=3\r
                """
        },
        "firewall_delete": {
                "request_id": "4",
                "data": """[RULE#__1__,0,0,0,0,0#0,0,0,0,0,0]0,0\r
                """
        },
        "firewall_list": {
                "request_id": "5&1",
                "data" :"""[RULE#0,0,0,0,0,0#0,0,0,0,0,0]0,0\r
                [FIREWALL#0,0,0,0,0,0#0,0,0,0,0,0]1,2\r
                enable\r
                defaultAction\r
                """,
                "parse": parse_firewall_rules
        },
}

if config.router["debug"]:
        try:
                import http.client as http_client
        except ImportError:
                import httplib as http_client
        http_client.HTTPConnection.debuglevel = 1

# run a command
def run_command(command_name,args):
        # ensure a valid command is provided
        if command_name not in commands:
                print "Invalid command "+command_name
                sys.exit(1)
        command = copy.deepcopy(commands[command_name])
        # replace the placeholders in the data
        for i in range(len(args)):
                c = i+1
                command["data"] = command["data"].replace("__"+str(c)+"__",str(args[i]))
        # send the request
        data = send(command)
        # ensure there is no error
        if "[error]0" not in data:
                print "Error running "+command_name+": "+data
		return 
        # parse the output if needed and return the data
        if "parse" in command: return command["parse"](data)
        else: return data

# send a command
def send(command):
        command["data"] = command["data"].replace("\t","")
        command["data"] = command["data"].replace(" ","")
        r = requests.post(url+command["request_id"],data=command["data"],cookies=cookies,headers=headers)
        return r.text

# print usage
def usage():
        print "Usage: tp_link.py add <description> <mac_address> <expire_days>"
        print "       tp_link.py delete <description>"
        sys.exit(1)

# add a new entry
def add(description,mac,expire_days):
	# prepare data
	mac = mac.upper()
	mac_label = "_"+mac.replace(":","")+"_"
        description = re.sub(r'[^a-zA-Z0-9]',r'',description)
	expire = str(int(time.time())+int(expire_days)*3600*24) if int(expire_days) > 0 else "0"
        label = "_"+description+"_"+mac.replace(":","")+"_"+expire+"_"
	# check if the same host is already there
	entries = run_command("wireless_list",[])
        for i in range(len(entries)):
                entry = entries[i]
                if entry["description"] == description or entry["mac"] == mac.replace(":",""):
			return "Device already registered"
	# add the entries
	run_command("wireless_add",[label,mac])
	if config.router["add_firewall_rule"]:
		run_command("host_add",[mac_label,mac])
		run_command("firewall_add",[mac_label,mac_label])
	return "ok"

# delete an entry
def delete(description):
	# prepare the data
	description = re.sub(r'[^a-zA-Z0-9]',r'',description)
	# retrive the entry
	found = None
	entries = run_command("wireless_list",[])
	for i in range(len(entries)):
		entry = entries[i]
		if entry["description"] == description: found = entry
	if found is None:
		return "Unable to find "+description
	# delete the wireless entry
	run_command("wireless_delete",[found["id"]])
	# search and delete the firewall entry
	entries = run_command("firewall_list",[])
        for i in range(len(entries)):
                entry = entries[i]
		if entry["mac"] == found["mac"]:
			run_command("firewall_delete",[entry["id"]])
			break
        # search and delete the host entry
        entries = run_command("host_list",[])
        for i in range(len(entries)):
                entry = entries[i]
                if entry["mac"] == found["mac"]:
                        run_command("host_delete",[entry["id"]])
                        break
	return "ok"

# delete expired entries
def expire():
	now = int(time.time())
        entries = run_command("wireless_list",[])
	count = 0
        for i in range(len(entries)):
                entry = entries[i]
		if entry["expire"] == 0: continue
		if entry["expire"] < now:
			delete(entry["description"])
			count = count + 1
	return  "Expired "+count+" entries"

# run the main app
if __name__ == '__main__':
	# check the number of arguments
	if len(sys.argv) == 1: usage()
	command = sys.argv[1]

	# run the requested command
	if command == "add":
		if len(sys.argv) != 5: usage()
		print add(sys.argv[2],sys.argv[3],sys.argv[4])
	elif command == "delete":
	        if len(sys.argv) != 3: usage()
	        print delete(sys.argv[2])
	elif command == "expire":
		print expire()
