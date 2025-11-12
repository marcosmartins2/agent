from django.urls import path
from . import views

app_name = "webhooks"

urlpatterns = [
    path("n8n/events", views.receive_event, name="n8n_events"),
]
