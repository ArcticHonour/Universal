#!/bin/bash

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check if running as root, if so exit to prevent unintended actions
if [ "$(id -u)" -eq 0 ]; then
    echo "Do not run this script as root. Please run it as a regular user."
    exit 1
fi

# Update package list and install prerequisites if not already installed
if ! command_exists unzip || ! command_exists wget || ! command_exists git || ! command_exists python3 || ! command_exists pip3 || ! command_exists curl; then
    echo "Installing required packages..."
    sudo apt update && sudo apt install -y unzip wget git python3 python3-pip curl
else
    echo "All required packages are already installed."
fi

# Check if ngrok is installed
if ! command_exists ngrok; then
    echo "Installing ngrok..."
    # Add the ngrok GPG key and repository
    curl -sSL https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null
    echo "deb https://ngrok-agent.s3.amazonaws.com/ buster main" | sudo tee /etc/apt/sources.list.d/ngrok.list

    # Update package list again to include ngrok
    sudo apt update

    # Install ngrok
    sudo apt install -y ngrok

    # Save ngrok authtoken (ensure to replace with your actual token)
    ngrok authtoken 2nXGmMYv5OLZHjxmLxEiIbd5nL8_63mGYjcJQPArP
else
    echo "ngrok is already installed."
fi

# Check for required Python packages
REQUIRED_PACKAGES=(Flask requests dhooks)
for PACKAGE in "${REQUIRED_PACKAGES[@]}"; do
    if ! pip3 show "$PACKAGE" >/dev/null 2>&1; then
        echo "Installing Python package: $PACKAGE"
        pip3 install "$PACKAGE"
    else
        echo "Python package $PACKAGE is already installed."
    fi
done

# Clone the GitHub repository if not already cloned
REPO_DIR="Universal"
if [ ! -d "$REPO_DIR" ]; then
    echo "Cloning the GitHub repository..."
    git clone https://github.com/ArcticHonour/Universal/
else
    echo "Repository $REPO_DIR already exists."
fi

# Navigate to the Universal directory
cd "$REPO_DIR" || { echo "Failed to enter Universal directory"; exit 1; }

# Get the directory of this script
SCRIPT_DIR=$(pwd)

# Set the script name
SCRIPT_NAME="app.py"

# Construct the full path to the script
SCRIPT_PATH="$SCRIPT_DIR/$SCRIPT_NAME"

# Give execution permissions to the Python script
chmod +x "$SCRIPT_PATH"

# Run the app.py script in the background using nohup
nohup python3 "$SCRIPT_PATH" > /dev/null 2>&1 &

echo "Installation, cloning, and running $SCRIPT_NAME in the background completed!"

# Clear the screen
clear

# Install required Python packages from requirements.txt
if [ -f requirements.txt ]; then
    pip install -r requirements.txt
else
    echo "requirements.txt not found."
fi

# Grant execute permissions to run_script.sh (not necessary for Linux, but for consistency)
if [ -f run_script.sh ]; then
    chmod +x run_script.sh
fi
