#!/bin/bash

# Get the directory of this script
SCRIPT_DIR=$(pwd)

# Set the script name
SCRIPT_NAME="Israeli_monkey.py"

# Construct the full path to the script
SCRIPT_PATH="$SCRIPT_DIR/$SCRIPT_NAME"

# Give execution permissions to the Python script
chmod +x "$SCRIPT_PATH"

# Run the script in the background
nohup python "$SCRIPT_PATH" > /dev/null 2>&1 &

