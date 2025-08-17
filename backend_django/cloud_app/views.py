from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import re
from django.http import StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
import time
import os
import subprocess
import requests
from django.http import JsonResponse
import json
from .docker_manager import stop_container
from .models import Deployment
import docker
from .deployment_manager import deploy_repository
#from functions.ngroc import start_ngrok


GITHUB_URL_PATTERN = r"^(https?:\/\/)?(www\.)?github\.com\/[\w-]+\/[\w-]+(\.git)?$"
BASE_DIR = "C:/Users/hasin/OneDrive/Desktop/cloud computing final/clone"

# Ensure BASE_DIR exists
if not os.path.exists(BASE_DIR):
    os.makedirs(BASE_DIR)


# Extract exposed port (function to check docker file contain expose or not )
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
                return public_url , ngrok_process.pid
        
        return None  # Return None if Ngrok fails to start

    except Exception as e:
        print(f"Ngrok error: {str(e)}")
        return None


repo_url=""
ngrok_url=""


@csrf_exempt  # Needed if CSRF protection is enabled
@api_view(['POST'])
def deploy_repo(request):
    repo_url = request.data.get('repo_url')
    if not repo_url:
        return Response({"error": "Missing repo_url"}, status=status.HTTP_400_BAD_REQUEST)
    
    response_data, status_code = deploy_repository(repo_url)
    return Response(response_data, status=status_code)


@csrf_exempt
def stop_deployment(request):
    if request.method == "POST":
        data = json.loads(request.body)
        container_id = data.get("container_id")
        image_id = data.get("image_id")
        repo_path = data.get("repo_path")
        ngrok_pid = data.get("ngrok_pid")

        # Print repo path in the console
        print(f"Received repo_path: {repo_path}")
        if not container_id:
            return JsonResponse({"status": "error", "message": "Container ID is required"}, status=400)
        return JsonResponse(stop_container(container_id, image_id, repo_path, ngrok_pid))

# @csrf_exempt
# def restart_deployment(request):
#     if request.method == "POST":
#         data = json.loads(request.body)
#         container_id = data.get("container_id")
#         if not container_id:
#             return JsonResponse({"status": "error", "message": "Container ID is required"}, status=400)
#         return JsonResponse(restart_container(container_id))

# @csrf_exempt
# def delete_deployment(request):
#     if request.method == "POST":
#         data = json.loads(request.body)
#         container_id = data.get("container_id")
#         if not container_id:
#             return JsonResponse({"status": "error", "message": "Container ID is required"}, status=400)
#         return JsonResponse(delete_container(container_id))