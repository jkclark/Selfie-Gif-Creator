#!/bin/sh
# This script is used to install FFmpeg on the AWS Lambda Python image.
# It is called as part of the build process (see Dockerfile).

cd /usr/local/bin
mkdir ffmpeg && cd ffmpeg

# Download static build of ffmpeg
yum install wget -y
wget https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz

# Unzip the binaries
yum install xz -y
yum install tar -y
tar -xf ffmpeg-release-amd64-static.tar.xz 

# Create symlink for global use
ln -s /usr/local/bin/ffmpeg/ffmpeg-6.0-amd64-static/ffmpeg /usr/bin/ffmpeg
