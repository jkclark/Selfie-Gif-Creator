#!/bin/bash
# This script creates a zip file containing the Lambda function code and
# dependencies, and updates the preprocess Lambda function to use the latest
# version of the zip file.
#
# Typically, this script shouldn't be run manually. Deployments to Lambda should
# be done automatically via GitHub Actions. However, it is useful for quickly
# iterating Lambda-specific code, since this script is much faster than the
# GitHub Actions workflow.
#
# Args:
# $1: AWS account ID
# $2: AWS region

# Move to site-packages and zip dependencies
cd ./.venv/lib/python3.10/site-packages && zip -r ../../../../deployment.zip .

# Move back to project root
cd ../../../../

# Zip source code
zip -gr deployment.zip src/*

# Upload to Lambda
aws lambda update-function-code --function-name  SMMPreprocessImage --zip-file fileb://deployment.zip
