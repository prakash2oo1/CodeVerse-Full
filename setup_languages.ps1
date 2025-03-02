# Install Chocolatey if not already installed
if (!(Get-Command choco -ErrorAction SilentlyContinue)) {
    Set-ExecutionPolicy Bypass -Scope Process -Force
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
    iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))
}

# Install required languages and tools
choco install -y python3
choco install -y nodejs
choco install -y openjdk
choco install -y mingw
choco install -y ruby
choco install -y php

# Refresh environment variables
refreshenv

# Verify installations
Write-Host "Verifying installations..."
python --version
node --version
javac -version
g++ --version
gcc --version
ruby --version
php --version 