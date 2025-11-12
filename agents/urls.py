from django.urls import path
from . import views

app_name = "agents"

urlpatterns = [
    path("", views.agent_list, name="list"),
    path("create/", views.agent_create, name="create"),
    path("<slug:slug>/", views.agent_detail, name="detail"),
    path("<slug:slug>/edit/", views.agent_edit, name="edit"),
    path("<slug:slug>/delete/", views.agent_delete, name="delete"),
    path("<slug:slug>/playground/", views.agent_playground, name="playground"),
]
