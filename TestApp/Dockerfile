# sudo docker run --privileged --device /dev/video0 --device /dev/vchiq --env LD_LIBRARY_PATH=/opt/vc/lib -v /run/udev:/run/udev:ro testapp

FROM debian:bullseye

RUN apt update && apt install -y --no-install-recommends gnupg

RUN echo "deb http://archive.raspberrypi.org/debian/ bullseye main" > /etc/apt/sources.list.d/raspi.list \
  && apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 82B129927FA3303E

RUN apt update && apt -y upgrade

RUN apt update && apt install -y --no-install-recommends \
         python3-pip \
         python3-picamera2 \
     && apt-get clean \
     && apt-get autoremove \
     && rm -rf /var/cache/apt/archives/* \
     && rm -rf /var/lib/apt/lists/*

# ------------------------------------------------------------------------------------------------
# Build and run application
# ------------------------------------------------------------------------------------------------
# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt /app/

# Install Python dependencies
# TODO: fix issue with "--break-system-packages" flag
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Python files
COPY  . /app/

# Set the entry point
CMD ["python3", "/app/test_3.py"]
