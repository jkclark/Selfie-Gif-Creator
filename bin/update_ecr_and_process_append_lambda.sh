#!/bin/bash
# This script builds the Docker image, deploys it to Amazon ECR, and updates
# the prepare-and-append Lambda function to use the latest version of the image.
#
# Typically, this script shouldn't be run manually. Deployments to ECR and
# Lambda should be done automatically via GitHub Actions. However, it is useful
# for quickly iterating Lambda-specific code, since this script is much faster
# than the GitHub Actions workflow.
#
# Args:
# $1: AWS account ID
# $2: AWS region

# Build
docker build --platform linux/amd64 -t selfie-movie-maker:latest .

# Authenticate the Docker CLI to Amazon ECR registry
docker login -u AWS -p $(aws ecr get-login-password --region $2) $1.dkr.ecr.$2.amazonaws.com

# Tag local image into Amazon ECR repository as the latest version
docker tag selfie-movie-maker:latest $1.dkr.ecr.$2.amazonaws.com/selfie-movie-maker:latest

# Deploy local image to Amazon ECR repository
docker push $1.dkr.ecr.$2.amazonaws.com/selfie-movie-maker:latest

# Update Lambda function
aws lambda update-function-code --function-name SelfieMovierMakerUpdateDocker --image-uri $1.dkr.ecr.$2.amazonaws.com/selfie-movie-maker:latest
