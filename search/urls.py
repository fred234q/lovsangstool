from django.urls import path
from . import views

urlpatterns = [
    path("", views.searchView, name="search")
]