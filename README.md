# Selfie Movie Maker

### Overview

I take a selfie of myself every day at 8:30pm. I write the date on each one and compile them into a movie so that I can see my life as a series of images. This app automates everything after taking the photo.

### Architecture

This application relies on Docker to make sure that the execution environment is consistent. The Docker image used is built from an AWS Lambda Python base image. When code is changed, a new image is uploaded to AWS ECR, and then the Lambda function is updated using the new image.

There are two S3 buckets configured for this project. One is an input bucket, and the other is an output (called "aux" in this project) bucket. The Lambda function is set up to react to any upload event to the input S3 bucket. When a new photo is uploaded to the S3 bucket, the Lambda function is invoked. It downloads the new photo and the existing movie, updates the movie with the new photo, and uploads the new movie to the output bucket.

### Local setup

There shouldn't be too much "local" setup, since there is a Github Codespace set up for this project.

### Run locally

1. Build the Docker image: `docker build --platform linux/amd64 -t smm-dev:latest .`
2. Append an image to a movie: `./bin/run_local.sh {PATH_TO_INPUT_IMAGE} {PATH_TO_INPUT_MOVIE} {PATH_TO_OUTPUT_MOVIE}`

### Other notes

- `ffmpeg.tar.xz` is downloaded from https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz
