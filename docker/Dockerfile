FROM debian:bullseye-slim

# define variables

# make sure these variables are set the same as `docker-entrypoint.sh`
ENV CONFIG_MOUNT="/config"
ENV OTPSPOT_DIR="/otpspot"
ENV WEB_PORT=8000

ENV GOOGLE_AUTHENTICATOR_VERSION=1.09
ENV GOOGLE_AUTHENTICATOR_HASH=ab1d7983413dc2f11de2efa903e5c326af8cb9ea37765dacb39949417f7cd037

# Install required packages with apt
RUN apt update \
  && apt -y upgrade \
  && apt install -y \
  curl \
  debootstrap \
  python3 \
  ca-certificates \
  build-essential \
  autoconf \
  automake \
  libtool \
  libpam0g-dev \
  libqrencode4 \
  pamtester \
  sudo \
  python3-flask \
  # install google-authenticator-libpam
  && curl -L https://github.com/google/google-authenticator-libpam/archive/$GOOGLE_AUTHENTICATOR_VERSION.tar.gz > $GOOGLE_AUTHENTICATOR_VERSION.tar.gz \
  && sha256sum $GOOGLE_AUTHENTICATOR_VERSION.tar.gz \
  && echo $GOOGLE_AUTHENTICATOR_HASH $GOOGLE_AUTHENTICATOR_VERSION.tar.gz | sha256sum -c - || exit 1 \
  && tar zxfv $GOOGLE_AUTHENTICATOR_VERSION.tar.gz \
  && rm -f $GOOGLE_AUTHENTICATOR_VERSION.tar.gz \
  && cd google-authenticator-libpam-$GOOGLE_AUTHENTICATOR_VERSION \
  && ./bootstrap.sh \
  && ./configure \
  && make \
  && make install \
  && make clean \
  && cd .. \
  && rm -rf google-authenticator-libpam-$GOOGLE_AUTHENTICATOR_VERSION \
  && mkdir -p /lib/security \
  && mv /usr/local/lib/security/* /lib/security \
  # remove not needed packages (used only to compile)
  && apt purge -y \
  curl \
  debootstrap \
  ca-certificates \
  build-essential \
  autoconf \
  automake \
  libtool\
  && apt autoremove -y \
  && apt autoclean -y \
  && rm -rf /var/lib/apt/lists/*


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
ENTRYPOINT ["bash","/docker-entrypoint.sh"]

# Start otpspot
CMD ["otpspot"]
