# backend_awtc/api/urls.py
from django.urls import path, include
from . import views

urlpatterns = [
    path("hello/", views.hello_world, name="hello_world"),
]
