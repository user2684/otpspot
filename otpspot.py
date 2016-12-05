#!/usr/bin/python
from flask import Flask,request,send_from_directory,render_template,current_app
import os
import subprocess

import config
import tp_link

# version
version = "1.0"

# variables
base_dir = os.path.abspath(os.path.dirname(__file__))
web_folder = base_dir+"/web"
use_reloader = False

# define the web application
app = Flask(__name__,template_folder=web_folder)

# define the plugin to use for the router
router = None
if config.router["plugin"] == "tp-link:TD-W8970": router = tp_link
if router is None:
        print "Unknown router plugin "+config.router["plugin"]
        sys.exit(1)

# render index if no page name is provided
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def root(path):
        return render_template("index.html")

# return favicon
@app.route('/favicon.ico')
def favicon():
        return send_from_directory(web_folder,"favicon.ico")

# static folder (web)
@app.route('/web/<path:filename>')
def static_page(filename):
        return send_from_directory(web_folder, filename)

# return the client mac address
@app.route('/get_mac_address')
def get_mac_address():
	arp = run_command("arp "+request.remote_addr+" |grep -v HWtype|awk '{print $3}'")
	return arp.upper()

# return the default expire days
@app.route('/get_expire_days')
def get_expire_days():
        return str(config.policy["expire_days"])

# register a new client
@app.route('/register')
def register():
	description = code = mac = expire_days = None
	if "description" in request.args: description = request.args.get("description")
	if "code" in request.args: code = request.args.get("code")
	if "mac" in request.args: mac = request.args.get("mac")
	if "expire_days" in request.args: expire_days = request.args.get("expire_days")
	if description is None or code is None or mac is None or expire_days is None: return "Missing a required parameter"
	if description == "" or code == "" or mac == "" or expire_days == "": return "Missing parameter"
	if config.otp["enabled"] and not verify_otp(code): return "Invalid Access Code"
	return router.add(description,mac,expire_days)

# run the web server
def run():
        app.run(debug=True, use_reloader=use_reloader, host='0.0.0.0',port=config.web["port"])

# run a command and return the output
def run_command(command):
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        output = ''
        for line in process.stdout.readlines():
                output = output+line
        return output.rstrip()

# verify otp code
def verify_otp(code):
	command = "echo "+config.otp["password"]+code+" |sudo pamtester "+config.otp["pam_service"]+" "+config.otp["username"]+" authenticate 2>&1|grep -c 'successfully authenticated'"
	found = int(run_command(command))
	if found == 1: return True
	return False

# run the main app
if __name__ == '__main__':
	print "Welcome to OTPspot v"+version
        run()
