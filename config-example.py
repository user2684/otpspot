#!/usr/bin/python

# router related configuration
router = {
	# the plugin to use for communicating with the router
	"plugin": "tp-link:TD-W8970",
	# the IP address of the router
	"ip": "192.168.0.1",
	# username of the admin user
	"username": "admin",
	# password of the admin user
	"password": "password",
	# if true allow the device to connect to the main wireless by adding its MAC address as an exception
	"add_mac_filtering_rule": True,
	# if true create a firewall rule to allow the device connecting to the internet
	"add_firewall_rule": True,
	# enable debug mode
	"debug": False,
}

# web portal related configuration
web = {
	# listen on this port
	"port": 8000,
}

# otp verification related configuration
otp = {
	# the username of the user to test the OTP against
	"username": "hotspot",
	# the password of the user
	"password": "h0tsp0t123!",
	# the name of the pam service to be used for verifying the authentication
	"pam_service": "otpspot",
	# if true the OTP is verified, if false any OTP will be accepted
	"enabled": True,
}

# policy configuration
policy = {
        # the number of days after which the device will be removed
        "expire_days": 7,
}
