#!/bin/bash

# Build the Docker image
sudo docker build -t testapp .

# Tag the Docker image
sudo docker tag testapp acrdoorbell.azurecr.io/testapp2

# Push the Docker image to the Azure Container Registry
sudo docker push acrdoorbell.azurecr.io/testapp2
