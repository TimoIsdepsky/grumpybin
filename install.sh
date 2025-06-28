#!/bin/bash

set -e

SERVICE_FILE="/etc/systemd/system/grumpybin.service"

# Install docker if not installed
if ! command -v docker &> /dev/null; then
    echo "Docker not found. Installing Docker..."
    sudo apt-get update
    sudo apt-get install -y docker.io
    sudo systemctl start docker
    sudo systemctl enable docker
    echo "Docker installed and started successfully."
else
    echo "Docker is already installed."
fi

# set docker to run without sudo
if ! groups | grep -q "\bdocker\b"; then
    echo "Adding user to docker group..."
    sudo usermod -aG docker $USER
    echo "User added to docker group. Please log out and log back in for changes to take effect."
else
    echo "User is already in the docker group."
fi

# Install docker-compose if not installed
if ! command -v docker-compose &> /dev/null; then
    echo "Docker Compose not found. Installing Docker Compose..."
    sudo apt-get update
    sudo apt-get install -y docker-compose
    echo "Docker Compose installed successfully."
else
    echo "Docker Compose is already installed."
fi

# Install python3 if not installed
if ! command -v python3 &> /dev/null; then
    echo "Python3 not found. Installing Python3..."
    sudo apt-get update
    sudo apt-get install -y python3 python3-venv
    echo "Python3 installed successfully."
else
    echo "Python3 is already installed."
fi

# Install python3-pip if not installed
if ! command -v pip3 &> /dev/null; then
    echo "pip3 not found. Installing pip3..."
    sudo apt-get update
    sudo apt-get install -y python3-pip
    echo "pip3 installed successfully."
else
    echo "pip3 is already installed."
fi

# Install python3-venv if not installed
if ! python3 -m venv --help &> /dev/null; then
    echo "python3-venv not found. Installing python3-venv..."
    sudo apt-get update
    sudo apt-get install -y python3.12-venv
    echo "python3-venv installed successfully."
else
    echo "python3-venv is already installed."
fi

# install pyttsx3 dependencies
sudo apt install -y espeak ffmpeg libespeak1

# Create a virtual environment in /usr/local/bin/grumpybin if it doesn't exist
if [ ! -d "/usr/local/bin/grumpybin/venv" ]; then
    echo "Creating virtual environment in /usr/local/bin/grumpybin..."
    sudo mkdir -p /usr/local/bin/grumpybin/venv
    python3 -m venv /usr/local/bin/grumpybin/venv
    echo "Virtual environment created successfully."
else
    echo "Virtual environment already exists in /usr/local/bin/grumpybin."
fi

# Activate the virtual environment
source /usr/local/bin/grumpybin/venv/bin/activate

# Upgrade pip to the latest version
echo "Upgrading pip to the latest version..."
pip install --upgrade pip

# Install required python packages
echo "Installing required Python packages..."
pip install -r requirements.txt

# Create systemd service file if it doesn't exist
if [ ! -f "$SERVICE_FILE" ]; then
    echo "Creating systemd service file at $SERVICE_FILE..."
    sudo bash -c "cat > $SERVICE_FILE" <<EOL
[Unit]
Description=GrumpyBin Service
After=network.target
[Service]
ExecStart=/usr/local/bin/grumpybin/venv/bin/python /usr/local/bin/grumpybin/bin.py
WorkingDirectory=/usr/local/bin/grumpybin
Restart=always
User=root
Group=root
[Install]
WantedBy=multi-user.target
EOL
    echo "Systemd service file created successfully."
else
    echo "Systemd service file already exists at $SERVICE_FILE."
fi

# move needed python files to /usr/local/bin
sudo mkdir -p /usr/local/bin/grumpybin/
sudo cp ./lines /usr/local/bin/grumpybin/
sudo cp ./speech.py /usr/local/bin/grumpybin/
sudo cp ./bin.py /usr/local/bin/grumpybin/

# Start the docker containers
echo "Starting Docker containers..."
docker-compose up -d

# enable systemd service
sudo systemctl daemon-reload
sudo systemctl enable grumpybin.service
sudo systemctl start grumpybin.service
sudo systemctl status grumpybin.service
echo "GrumpyBin service installed and started successfully."

# (Optional) Follow logs
echo "To view the logs of the GrumpyBin service, use the following command:"
echo "sudo journalctl -u grumpybin.service -f"
