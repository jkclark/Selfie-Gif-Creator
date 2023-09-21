#!/bin/sh
cd /usr/local/bin
mkdir ffmpeg && cd ffmpeg

# Download static build of ffmpeg
# TODO: Can I ADD this instead of installing it here?
yum install wget -y
wget https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz

# Unzip the binaries
yum install xz -y
yum install tar -y
tar -xf ffmpeg-release-amd64-static.tar.xz 

# Create symlink for global use
ln -s /usr/local/bin/ffmpeg/ffmpeg-6.0-amd64-static/ffmpeg /usr/bin/ffmpeg
