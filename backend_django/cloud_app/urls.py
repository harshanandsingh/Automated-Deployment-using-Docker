from django.urls import path
from . import views

urlpatterns = [
    path("deploy_repo/",views.deploy_repo,name="deploy"),
    path("deploy_repo/stop/", views.stop_deployment, name="stop_deployment"),
    # path("deploy_repo/restart/", docker_manager.restart_deployment, name="restart_deployment"),
    # path("deploy_repo/delete/", docker_manager.delete_deployment, name="delete_deployment"),

]