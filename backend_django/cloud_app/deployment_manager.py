import os
import subprocess
import re
import time
import requests

GITHUB_URL_PATTERN = r"^(https?:\/\/)?(www\.)?github\.com\/[\w-]+\/[\w-]+(\.git)?$"
BASE_DIR = "C:/Users/hasin/OneDrive/Desktop/cloud computing final/clone"

# Ensure BASE_DIR exists
if not os.path.exists(BASE_DIR):
    os.makedirs(BASE_DIR)

def get_exposed_port(dockerfile_path):
    if os.path.exists(dockerfile_path):
        with open(dockerfile_path, "r") as f:
            for line in f:
                if line.strip().startswith("EXPOSE"):
                    return line.strip().split()[1]  # Extract port number
    return None

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
                return public_url, ngrok_process.pid
        
        return None  # Return None if Ngrok fails to start

    except Exception as e:
        print(f"Ngrok error: {str(e)}")
        return None

def clone_repository(repo_url):
    if not repo_url:
        return {"error": "Missing repo_url"}, 400
    
    if not re.match(GITHUB_URL_PATTERN, repo_url):
        return {"error": "Invalid GitHub repository URL"}, 400
    
    repo_name = repo_url.split("/")[-1].replace(".git", "")
    repo_path = os.path.join(BASE_DIR, repo_name)

    # Convert to forward slashes
    repo_path = repo_path.replace("\\", "/")
    
    # If repo already exists, append a number to avoid conflicts
    counter = 1
    new_repo_path = repo_path

    while os.path.exists(new_repo_path):  
        new_repo_path = f"{repo_path}_{counter}"
        counter += 1

    print(f"Cloning repo into: {new_repo_path}")
    
    # Clone the GitHub Repository
    try:
        subprocess.run(["git", "clone", repo_url, new_repo_path], check=True)
        print("clone successfully")
        return new_repo_path, None
    except subprocess.CalledProcessError:
        return None, {"error": "Failed to clone repository"}

def build_docker_image(repo_path, repo_name):
    dockerfile_path = os.path.join(repo_path, "Dockerfile")
    if not os.path.exists(dockerfile_path):
        print("docker file not found")
        return None, {"error": "No Dockerfile found in repo"}

    # Define image name (ensure lowercase for Docker compatibility)
    image_name = f"app_{repo_name.lower()}"
    build_command = ["docker", "build", "-t", image_name, repo_path]

    try:
        print(f"📌 Running Docker Build: {' '.join(build_command)}")
        # Run Docker build command
        result = subprocess.run(build_command, check=True, capture_output=True, text=True)
        
        # Print output for debugging
        print("Docker Build Output:", result.stdout)
        
        return image_name, None

    except subprocess.CalledProcessError as e:
        # Print error output for debugging
        print("Docker Build Error:", e.stderr)
        return None, {"error": f"Failed to build Docker image: {e.stderr}"}

def run_docker_container(repo_path, repo_name, image_name):
    dockerfile_path = os.path.join(repo_path, "Dockerfile")
    exposed_port = get_exposed_port(dockerfile_path)
    container_name = f"container_{repo_name}"

    # Run container with or without port mapping
    if exposed_port:
        run_command = ["docker", "run", "-d", "-p", f"8080:{exposed_port}", "--name", container_name, image_name]
    else:
        run_command = ["docker", "run", "-d", "-P", "--name", container_name, image_name]

    try:
        result = subprocess.run(run_command, check=True, capture_output=True, text=True)
        print("Docker Run Output:", result.stdout, result.stderr)
        return container_name, None
    except subprocess.CalledProcessError as e:
        return None, {"error": f"Failed to run Docker container: {e.stderr}"}

def deploy_repository(repo_url):
    # Clone repository
    repo_path, error = clone_repository(repo_url)
    if error:
        return error, 400
    
    repo_name = repo_url.split("/")[-1].replace(".git", "")
    
    # Build Docker image
    image_name, error = build_docker_image(repo_path, repo_name)
    if error:
        return error, 500
    
    # Run Docker container
    container_name, error = run_docker_container(repo_path, repo_name, image_name)
    if error:
        return error, 500
    
    # Start Ngrok and store the URL
    ngrok_url, ngrok_pid = start_ngrok()
    if ngrok_url:
        response_data = {
            "message": "Deployment successful",
            "deployment_id": repo_name,
            "container_id": container_name,
            "ngrok_url": ngrok_url,
            "image_id": image_name,
            "repo_path": repo_path,
            "ngrok_pid": ngrok_pid,
        }
        return response_data, 200
    else:
        return {"error": "Ngrok failed to start"}, 500 