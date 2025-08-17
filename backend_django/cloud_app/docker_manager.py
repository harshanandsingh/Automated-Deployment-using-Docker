import docker
import shutil
import os
import psutil

client = docker.from_env()

def remove_readonly(func, path, _):
    """Change permission and retry deletion"""
    os.chmod(path, 0o777)  # Give full permissions
    func(path)  # Retry the deletion

def stop_container(container_id,image_id,repo_path,ngrok_pid):
    try:
        # Step 1: Remove the container
        container = client.containers.get(container_id)
        container.remove(force=True)  # Forcefully remove the container
        #return {"status": "success", "message": f"Container {container_id} deleted successfully"}
        #container.stop()
        #return {"status": "success", "message": f"Container {container_id} stopped successfully"}

        # Step 2: Remove the Docker image
        client.images.remove(image=image_id, force=True)

        # Step 3: Delete the cloned GitHub repository
        if os.path.exists(repo_path):
            shutil.rmtree(repo_path, onerror=remove_readonly)  # Force delete
            print("Folder deleted successfully!")
        else:
            print("Folder not found.")
        
        if ngrok_pid:
            try:
                ngrok_process = psutil.Process(ngrok_pid)
                ngrok_process.terminate()  # Gracefully stop
            except psutil.NoSuchProcess:
                pass  # ngrok already stopped
            except Exception as e:
                return {"status": "error", "message": f"Failed to stop ngrok: {str(e)}"}

        return {
            "status": "success",
            "message": f"Container {container_id}, Image {image_id}, and Repo {repo_path} deleted successfully"
        } 
    except Exception as e:
        return {"status": "error", "message": str(e)}

# def restart_container(container_id):
#     try:
#         container = client.containers.get(container_id)
#         container.restart()
#         return {"status": "success", "message": f"Container {container_id} restarted successfully"}
#     except Exception as e:
#         return {"status": "error", "message": str(e)}

# def delete_container(container_id):
#     try:
#         container = client.containers.get(container_id)
#         container.remove(force=True)  # Forcefully remove the container
#         return {"status": "success", "message": f"Container {container_id} deleted successfully"}
#     except Exception as e:
#         return {"status": "error", "message": str(e)}
