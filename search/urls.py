from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("soeg", views.search_view, name="search"),
    path("song/<int:song_id>", views.song_view, name="song"),

    # API routes
    path("song/<int:song_id>/chordpro", views.load_chordpro, name="load_chordpro"),
]