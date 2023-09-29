#!/bin/bash
# This script is useful for testing the Lambda function (and application
# code) locally. It runs the Lambda function in a Docker container, copies
# the input image and movie from the local machine to the container, and
# sends a GET request to trigger the function. The output movie is then
# copied from the Docker container to the local machine.
#
# Args:
# $1: local input image path
# $2: local input movie path
# $3: local output movie path

# Set local variables
container_name=smm-dev-local

# Set environment variables
source ./.env

# Run Docker container in the background
docker run -d -p 9000:8080 --env-file ./.env --name $container_name smm-dev:latest

# Make input- and temp-image directories
docker exec $container_name mkdir -p ${INPUT_IMAGE_FOLDER_PATH} ${TEMP_IMAGE_FOLDER_PATH}

# Copy input image from local to Docker container
docker cp $1 $container_name:${INPUT_IMAGE_FOLDER_PATH}

# Copy input movie from local to Docker container
docker cp $2 $container_name:${MOVIE_PATH}

# Wait for Docker container to be ready
# From https://stackoverflow.com/a/33520390/3801865
until [ "`docker inspect -f {{.State.Running}} $container_name`"=="true" ]; do
    sleep 0.5;
done;

# Send GET request to trigger Lambda function
# NOTE: Even with the above sleep call, we sometimes see the following
#       error when making the GET request:
#       curl: (56) Recv failure: Connection reset by peer
curl "http://localhost:9000/2015-03-31/functions/function/invocations" -d '{}'

# Copy output movie from Docker container to local
docker cp $container_name:${MOVIE_PATH} $3

# Delete Docker container
docker rm -f $container_name
