#!/bin/bash

# Install Homebrew if not installed
if ! command -v brew &> /dev/null; then
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

# Install required languages and tools
brew install python
brew install node
brew install openjdk
brew install gcc
brew install ruby
brew install php

# Create symlinks for Java
sudo ln -sfn $(brew --prefix)/opt/openjdk/libexec/openjdk.jdk /Library/Java/JavaVirtualMachines/openjdk.jdk

# Verify installations
echo "Checking installations..."
python3 --version
node --version
javac -version
g++ --version
gcc --version
ruby --version
php --version 