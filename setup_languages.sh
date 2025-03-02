#!/bin/bash

# Update package list
sudo apt-get update

# Install Python
sudo apt-get install -y python3 python3-pip

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install Java
sudo apt-get install -y default-jdk

# Install C/C++
sudo apt-get install -y build-essential

# Install Ruby
sudo apt-get install -y ruby-full

# Install PHP
sudo apt-get install -y php

# Verify installations
echo "Checking installations..."
python3 --version
node --version
javac -version
g++ --version
gcc --version
ruby --version
php --version 