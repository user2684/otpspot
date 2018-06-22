#!/usr/bin/python

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
	"password": "password",
	# the name of the pam service to be used for verifying the authentication
	"pam_service": "otpspot",
	# if true the OTP is verified, if false any OTP will be accepted
	"enabled": True,
}

# HTML template locale
language = {
	'title': 'Wireless Guest Login',
	'welcome_message': 'Please provide the code provided by the host below',
	'otp_placeholder': 'Access Code',
	'register_button': 'Register',
	'registering_message': 'Registering...',
	'registered_successfully': 'Registered',
	'error_banner': 'ERROR',
	'error_invalid_parameter': 'Missing required parameter',
	'error_invalid_otp': 'Invalid code provided',	
}
