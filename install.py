#!/usr/bin/python
import sys
import os

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
	print Installing pamtester..."
	run_command("apt-get install pamtester")
	print "Installing flask..."
	run_command("apt-get install python-flask")
	print "Installing hostapd..."
	run_command("apt-get install hostapd")

# installation routine
def install():
	install_deps()
	print "Installing the program..."
	# prepare the service template
	with open(service_template, 'r') as file:
		template = file.read()
	template = template.replace("#base_dir#",base_dir)
	# write the service script
	print "Creating the service script..."
	with open(service_location,'w') as file:
		file.write(template)
	file.close()
	# make it executable
	run_command("chmod 755 "+service_location)
	# creating the pam service
	print "Creating the pam service..."
	run_command("cp "+pam_template+" /etc/pam.d")
	# provide additional instructions
	print "To finalize the configuration, do the following":
	print "\t- Download, compile and install Google Authenticator from https://github.com/google/google-authenticator"
	print "\t- Create a user (e.g. otpspot) and set it a valid password"
	print "\t- Become that user (e.g. su otpspot)"
	print "\t- Run google-authenticator"
	print "\t- On your phone, install Google Authenticator from the app store"
	print "\t- Scan the bar code so to allow Google Authenticator on your phone to generate valid OTP"
	print "\t- If you wish to run the portal only when the Wifi USB dongle is plugged, add in the wlan0 section of /etc/network/interfaces:"
	print "\t\tpost-up /etc/init.d/otpspot start"
	print "\t\tpost-down /etc/init.d/otpspot stop"
	print "\t- If you wish to have the portal always running, run as root: update-rc.d otpspot defaults"
	print "\t- Rename the config-example.py file in config.py and edit it"
	print "\t- Set the INTERFACE, PORT and IP variables on top of /etc/init.t/otpspot"

# uninstall routine
def uninstall():
	print "Uninstalling the program..."
        # stop the service
	print "Stopping the service..."
        run_command("service "+service_filename+" stop")
	# remove the script
	print "Uninstalling the service..."
	run_command("rm -f "+service_location)
        # remove the pam service
        print "Uninstalling the pam service..."
        run_command("rm -f /etc/pam.d/"+service_filename)

# ensure it is run as root
if os.geteuid() != 0:
        exit("ERROR: You need to have root privileges to run this script.\nPlease try again, this time using 'sudo'. Exiting.")
# run the installation
if len(sys.argv) == 2 and sys.argv[1] == "-u": uninstall()
else: install()


