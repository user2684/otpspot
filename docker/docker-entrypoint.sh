#!/bin/bash
set -e

PYTHON="python3"

# make sure these variables are set the same as `Dockerfile`
CONFIG_MOUNT="/config"
OTPSPOT_DIR="/otpspot"

# execute through entrypoint
if [ "$1" = 'otpspot' ]; then

  # load/create google authenticator configuration file
  if [ -f $CONFIG_MOUNT/.google_authenticator ]; then
    echo -e "[\e[33motpspot\e[0m] Loading Google Authenticator configuration file..."
    cp -f $CONFIG_MOUNT/.google_authenticator /root
    chown root.root /root/.google_authenticator
    chmod 400 /root/.google_authenticator
  else
    echo -e "[\e[33motpspot\e[0m] Google Authenticator configuration file not found, running configuration wizard..."
    google-authenticator -t -l OTPSpot
    cp /root/.google_authenticator $CONFIG_MOUNT/.google_authenticator
    echo -e "[\e[33motpspot\e[0m] Google Authenticator configuration file saved, restart the container to run otpspot"
    exit 1
  fi

  # load otpspot configuration file
  if [ -f $CONFIG_MOUNT/config.py ]; then
    echo -e "[\e[33motpspot\e[0m] Loading otpspot configuration file..."
    cp -f $CONFIG_MOUNT/config.py $OTPSPOT_DIR
  else
    cp -f $OTPSPOT_DIR/config.py $CONFIG_MOUNT
  fi

  # root password needs to be set, used by pamtester for checking the validity of the otp
  echo -e "[\e[33motpspot\e[0m] Setting root password..."
  echo -e "password\npassword"|passwd root
  # User root will be used for checking the validity of the otp
  sed -i 's/"username": "hotspot"/"username": "root"/' $OTPSPOT_DIR/config.py \
  # log to startard output
  sed -i "s/filename=base_dir+'\/otpspot.log',//" $OTPSPOT_DIR/otpspot.py

  echo -e "[\e[33motpspot\e[0m] Starting otpspot..."
  exec $PYTHON $OTPSPOT_DIR/otpspot.py
fi

# execute the provided command
exec "$@"
