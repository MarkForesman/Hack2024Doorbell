# Lightweight Python container for Orchestrator

FROM python:3.11-slim

RUN apt update && apt -y upgrade

RUN apt update && apt install -y --no-install-recommends \
         iputils-ping \
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
RUN pip install --upgrade pip setuptools
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Python files
COPY  . /app/

# Set the entry point
CMD ["python3", "/app/orchestrator_tcp.py"]
