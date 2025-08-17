import subprocess
import time
import requests

def start_ngrok():
    try:
        # Start Ngrok process
        ngrok_process = subprocess.Popen(["ngrok", "http", "8080"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Allow time for Ngrok to start
        time.sleep(3)

        # Fetch public URL from Ngrok API
        response = requests.get("http://127.0.0.1:4040/api/tunnels")
        if response.status_code == 200:
            tunnels = response.json().get("tunnels", [])
            if tunnels:
                public_url = tunnels[0].get("public_url")
                return public_url
        
        return None  # Return None if Ngrok fails to start

    except Exception as e:
        print(f"Ngrok error: {str(e)}")
        return None