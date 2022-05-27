FROM alpine:edge
RUN echo "http://dl-cdn.alpinelinux.org/alpine/edge/testing" >> /etc/apk/repositories

# define variables

# make sure these variables are set the same as `docker-entrypoint.sh`
ENV CONFIG_MOUNT="/config"
ENV OTPSPOT_DIR="/otpspot"
ENV WEB_PORT=8000

RUN apk add --upgrade --no-cache sudo \
    pamtester \
    google-authenticator \
    py3-flask \
    libqrencode

# install otpspot
ADD web $OTPSPOT_DIR/web
ADD config.py $OTPSPOT_DIR
ADD index.html $OTPSPOT_DIR
ADD otpspot.py $OTPSPOT_DIR
ADD template_pam /etc/pam.d/otpspot

# Expose network services
EXPOSE $WEB_PORT

# Expose Volumes
VOLUME $CONFIG_MOUNT

# Install entrypoint
COPY docker/docker-entrypoint.sh /
ENTRYPOINT ["/bin/ash","/docker-entrypoint.sh"]

# Start otpspot
CMD ["otpspot"]
