from django.db import models

# Create your models here.
class Deployment(models.Model):
    repo_url = models.URLField(unique=True)  # GitHub repository URL
    container_id = models.CharField(max_length=100, unique=True)  # Docker container ID
    ngrok_url = models.URLField()  # The public URL from ngrok
    created_at = models.DateTimeField(auto_now_add=True)