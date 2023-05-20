#!/usr/bin/python
from flask import Flask, request, send_from_directory, render_template
import os
import subprocess
import datetime
import os.path
import logging

# version
version = "2.1"

# variables
base_dir = os.path.abspath(os.path.dirname(__file__))
web_folder = base_dir+"/web"
use_reloader = False

# load configuration file
if os.path.isfile(base_dir+'/config_custom.py'):
    import config_custom
    config = config_custom
else:
    import config

# define the web application
app = Flask(__name__, template_folder=web_folder)
logging.basicConfig(filename=base_dir+'/otpspot.log', level=logging.DEBUG)

# render index if no page name is provided


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def root(path):
    return render_template("index.html", title=config.language["title"], welcome_message=config.language["welcome_message"], otp_placeholder=config.language["otp_placeholder"], register_button=config.language["register_button"], registering_message=config.language["registering_message"], registered_successfully=config.language["registered_successfully"], error_banner=config.language["error_banner"], error_invalid_parameter=config.language["error_invalid_parameter"], error_invalid_otp=config.language["error_invalid_otp"])

# return favicon
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(web_folder, "favicon.ico")

# static folder (web)
@app.route('/web/<path:filename>')
def static_page(filename):
    return send_from_directory(web_folder, filename)

# register a new client
@app.route('/register')
def register():
    otp = mac = ip = tok = gatewayname = None
    if "otp" in request.args:
        otp = request.args.get("otp")
    if "mac" in request.args:
        mac = request.args.get("mac")
    if "ip" in request.args:
        ip = request.args.get("ip")
    if "tok" in request.args:
        tok = request.args.get("tok")
    if "gatewayname" in request.args:
        gatewayname = request.args.get("gatewayname")
    if otp is None or mac is None or ip is None or tok is None or gatewayname is None:
        return "1"
    otp_valid = verify_otp(otp)
    logging.info('['+datetime.datetime.now().isoformat()+'] '+str(gatewayname) +
                 ' '+str(ip)+' '+str(mac)+' '+str(tok)+': '+str(otp_valid))
    if config.otp["enabled"] and not otp_valid:
        return "2"
    return "0"

# run the web server
def run():
    app.run(debug=True, use_reloader=use_reloader,
            host='0.0.0.0', port=config.web["port"])

# run a command and return the output
def run_command(command):
    process = subprocess.Popen(
        command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output = b''
    for line in process.stdout.readlines():
        output = output+line
    return output.rstrip()

# verify otp code
def verify_otp(code):
    command = "echo "+config.otp["password"]+code+" |sudo pamtester "+config.otp["pam_service"] + \
        " "+config.otp["username"] + \
        " authenticate 2>&1|grep -c 'successfully authenticated'"
    found = int(run_command(command))
    if found == 1:
        return True
    return False


# run the main app
if __name__ == '__main__':
    logging.info("Welcome to OTPspot v"+version)
    run()
