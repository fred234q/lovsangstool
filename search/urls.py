from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("soeg", views.search_view, name="search"),
    path("sang/<int:song_id>", views.song_view, name="song"),
    path("soeg/opdater", views.update_results_view, name="update_results"),
    path("sang/<int:song_id>/merge", views.merge_songs, name="merge_songs"),

    # API routes
    path("sang/<int:song_id>/chordpro", views.load_chordpro, name="load_chordpro"),
    path("get-songs/<str:query>", views.get_songs, name="get_songs"),
]