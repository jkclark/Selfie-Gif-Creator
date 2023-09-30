#!/bin/sh
# This script is used to install FFmpeg on the AWS Lambda Python image.
# It is called as part of the build process (see Dockerfile).
# NOTE: ffmpeg.tar.xz must already be present.

cd /usr/local/bin
mkdir ffmpeg
cd ffmpeg

# Unzip the binaries
yum install xz -y
yum install tar -y
tar -xf /usr/local/bin/ffmpeg.tar.xz 

# Create symlink for global use
ln -s /usr/local/bin/ffmpeg/ffmpeg-6.0-amd64-static/ffmpeg /usr/bin/ffmpeg
