#!/bin/bash
# This script builds the Docker image, deploys it to Amazon ECR, and updates
# the Lambda function to use the latest version of the image.
#
# NOTE: Typically, this script shouldn't be run manually. Deployments to ECR and
# Lambda should be done automatically via GitHub Actions.
#
# Args:
# $1: AWS account ID

# Build
docker build \
--platform linux/amd64 \
-t selfie-movie-maker:latest \
.

# Authenticate the Docker CLI to Amazon ECR registry
aws ecr get-login-password --region eu-west-3 | docker login --username AWS --password-stdin $1.dkr.ecr.eu-west-3.amazonaws.com

# Tag local image into Amazon ECR repository as the latest version
docker tag selfie-movie-maker:latest $1.dkr.ecr.eu-west-3.amazonaws.com/selfie-movie-maker:latest

# Deploy local image to Amazon ECR repository
docker push $1.dkr.ecr.eu-west-3.amazonaws.com/selfie-movie-maker:latest

# Update Lambda function
aws lambda update-function-code --function-name SelfieMovierMakerUpdateDocker --image-uri $1.dkr.ecr.eu-west-3.amazonaws.com/selfie-movie-maker:latest
