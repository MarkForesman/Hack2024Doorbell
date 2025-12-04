# sudo docker run --privileged --device /dev/video0 --device /dev/vchiq --env LD_LIBRARY_PATH=/opt/vc/lib -v /run/udev:/run/udev:ro testapp

FROM debian:bullseye

RUN apt update && apt install -y --no-install-recommends ca-certificates gnupg wget curl

RUN curl -fsSL https://archive.raspberrypi.com/debian/raspberrypi.gpg.key | gpg --dearmor -o /usr/share/keyrings/raspberrypi-archive-keyring.gpg \
  && echo "deb [signed-by=/usr/share/keyrings/raspberrypi-archive-keyring.gpg] http://archive.raspberrypi.com/debian/ bullseye main" > /etc/apt/sources.list.d/raspi.list

RUN apt update && apt -y upgrade

RUN apt update && apt install -y --no-install-recommends \
         python3-pip \
         python3-picamera2 \
         python3-dev \
         libffi-dev gcc \
         iputils-ping \
         avahi-daemon \
         libnss-mdns \
     && apt-get clean \
     && apt-get autoremove \
     && rm -rf /var/cache/apt/archives/* \
     && rm -rf /var/lib/apt/lists/*
     
ENV PYTHONUNBUFFERED=1
# ------------------------------------------------------------------------------------------------
# Build and run application
# ------------------------------------------------------------------------------------------------
# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt /app/

# Install Python dependencies
# TODO: fix issue with "--break-system-packages" flag
RUN pip install --upgrade pip setuptools
RUN pip install --no-cache-dir -r requirements.txt

ENV ORCHESTRATOR_HOST=10.0.2.13
# Copy the Python files
COPY  . /app/

# Make the startup script executable
RUN chmod +x /app/resolve_hostname.sh

# Set the entry point
CMD ["/app/resolve_hostname.sh"]
