Introduction
===========

Run a captive portal on your OTPSpot server (any linux box) to allow your guests to register before accessing your Wifi at home. Users will be requested for an OTP code that you can generate on your phone. Get rid of the typical captive portal static username and password without the need for a radius server.

OTPspot (since version 2.0) is fully compatible with nodogsplash and can run as a FAS service. In this configuration, nodogsplash will take care of the networking whereas OTPspot will just authenticate the users.

How it works
---------------------

Once a user connects to the guest wireless network, nodogsplash will make te device detecting additional credentails are required and present the user with the OTPspot web-based and responsive captive portal where an access code is requested for the authentication. 

This code is generated by the Google Authenticator/Authy app running on the host's phone and aligned with a service running on the OTPSpot server used to validate the authentication. This requires the google-authenticator service running on the OTPSpot server and a custom pam service which is provided by OTPspot and installed automatically.

Once a valid OTP is provided the portal will notify nodogsplash the user has successfully authenticated and Internet access will be then granted. 

Installation
===========

nodogsplash
---------------------

To install and configure nodogsplash on a Openwrt-based router:
- Refresh the list of packages with: `opkg update`
- Install nodogsplash with: `opkg install nodogsplash`
- If you want your guests to connect to a dedicated guest wireless network:
	- Add a new, open wifi network in Network->Wireless
	- Add an interface with a static IP address in Network->Interfaces
	- Map the interface to the newly created wifi network 
	- Enable the DHCP service for this interface
- Edit nodogsplash configuration file in `/etc/config/nodogsplash`
	- To run on the newly created wifi interface only add: `option gatewayinterface 'wlan0-1'`
	- To allow connections from preauthenticated users to the captive portal running on the OTPSpot server add: `list preauthenticated_users 'allow tcp port 8000 to <OTPSpot_server_ip>'`
- Edit nodogsplash captive portal by editing /etc/nodogsplash/htdocs/splash.html:
	- To redirect users to the OTPspot captive portal add within the `<head>` section the following: `<meta http-equiv="refresh" content="0;URL='http://<OTPSpot_server_ip>:8000/index.html?authaction=$authaction&amp;tok=$tok&amp;redir=$redir&amp;mac=$clientmac&amp;ip=$clientip&amp;gatewayname=$gatewayname'" />`

OTPspot
---------------------

- Create on the OTPSpot server a directory of your choice and transfer all the files of the package
- As root, run the `install.py` script. This will install all the required dependencies, the init and the pam services.
- Download, compile and install Google Authenticator from https://github.com/google/google-authenticator
- Create a user (e.g. `adduser otpspot`) and set it a valid password
- Become that user (e.g. `su otpspot`)
- Run `google-authenticator -t` (`-t` = TOTP)
- On your phone, install Google Authenticator or Authy from the app store
- Scan the bar code on the screen to allow Google Authenticator on your phone to generate valid OTP codes. The same can be installed on multiple phones
- Edit the configuration file config.py and restart the service

Configuration
===========
- Edit the `config.py` file:
	- Customize if needed the port the captive portal runs on
	- Customize the username and password for the user on the system associated with the Google Authenticator service
	- Customize if needed the HTML template based on your language

Docker
===========
## How to Run It ##
* Build the Docker image using `docker build -f docker/Dockerfile -t otpspot .`
* On your phone, install Google Authenticator or Authy from the app store
* Create a local directory called `config` and map it into `/config` inside the container
* Run the image in interactive mode with `docker run --rm -ti -v $(pwd)/config:/config otpspot`. Since no Google Authenticator configuration file will be found, a new one will be created
* Scan the bar code on the screen to allow Google Authenticator on your phone to generate valid OTP codes. The same can be installed on multiple phones. Go through Google Authenticator configuration wizard; once it is finished, the container will exit
* Run the container again by mapping port 8000 with `docker run -p 8000:8000 -v $(pwd)/config:/config otpspot`; this time Google Authenticator configuration file will be found and OTPspot will be started
* You can optionally place a `config.py` file inside the `/config` directory to override any configuration setting (e.g. for the localisation of the captive portal)
* Configure nodogsplash to point to the captive portal running port 8000

Changelog
===========
- v2.1:
	- Migrated to Python 3
	- Incorporated docker build files for Debian 11 (bullseye)
- v2.0:
	- Added support for nodogsplash
	- Removed support for hostapd and tp-link router
	- Added support to customize the portal's language
	- Added support for logging on file
- v1.0:
	- Support for hostapd running on the raspberry
	- Support for creating MAC expections on a tp-link router
