#!/usr/bin/python
import sys
import os
import subprocess

# variables
base_dir = os.path.abspath(os.path.dirname(__file__))
service_template = base_dir+"/template_service.sh"
pam_template = base_dir+"/template_pam"
service_location = "/etc/init.d/otpspot"
service_filename = "otpspot"

# run a command and return the output
def run_command(command):
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        output = ''
        for line in process.stdout.readlines():
                output = output+line
        return output.rstrip()

# install all the dependencies
def install_deps():
	print "Preparing dependencies..."
	print "Installing pamtester..."
	run_command("apt-get install pamtester")
	print "Installing flask..."
	run_command("apt-get install python-flask")

# installation routine
def install():
	install_deps()
	# prepare the service template
	with open(service_template, 'r') as file:
		template = file.read()
	template = template.replace("#base_dir#",base_dir)
	# write the service script
	print "Installing the service..."
	with open(service_location,'w') as file:
		file.write(template)
	file.close()
	# make it executable
	run_command("chmod 755 "+service_location)
	# make it starting on boot
	run_command("update-rc.d "+service_filename+" defaults")
	# creating the pam service
	print "Creating the pam service..."
	run_command("cp "+pam_template+" /etc/pam.d/"+service_filename)
	# starting the service
	run_command("/etc/init.d/"+service_filename+" start")
	# provide additional instructions
	print "To finalize the configuration, do the following:"
	print "\t- Download, compile and install Google Authenticator from https://github.com/google/google-authenticator"
	print "\t- Create a user (e.g. adduser otpspot) and set it a valid password"
	print "\t- Become that user (e.g. su otpspot)"
	print "\t- Run google-authenticator"
	print "\t- On your phone, install Google Authenticator/Authy from the app store"
	print "\t- Scan the bar code so to allow Google Authenticator on your phone to generate valid OTP"
	print "\t- Edit the configuration file config.py and restart the service"

# uninstall routine
def uninstall():
        # stop the service
	print "Stopping the service..."
        run_command("/etc/init.d/"+service_filename+" stop")
	# remove the script
	print "Uninstalling the service..."
	run_command("update-rc.d -f otpspot remove")
	run_command("rm -f "+service_location)
        # remove the pam service
        print "Uninstalling the pam service..."
        run_command("rm -f /etc/pam.d/"+service_filename)

# ensure it is run as root
if os.geteuid() != 0:
        exit("ERROR: You need to have root privileges to run this script.\nPlease try again, this time using 'sudo'. Exiting.")
# run the installation
print "[OTPspot installation script]\n"
if len(sys.argv) == 2 and sys.argv[1] == "-u": uninstall()
else: install()


