from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from search.search import metasearch
from django.urls import reverse
from search.models import Song, Source
from django.http import JsonResponse
from thefuzz import process
from thefuzz import fuzz

def index(request):
    return HttpResponseRedirect(reverse("search"))

def get_songs(request, query):
    results = metasearch(query)

    songs = []
    for result in results:
        title = result["title"]
        url = result["url"]
        source_name = result["source"]
        
        source, created = Source.objects.get_or_create(name=source_name)
        song, created = Song.objects.get_or_create(title=title, url=url, source=source)
        songs.append(song)
    print(f"{len(songs)} songs found.")
    return HttpResponse(status=204)

def search_view(request):
    if not request.GET:
        return render(request, "search/index.html")
    
    query = request.GET["q"]
    songs = Song.objects.all()

    unsorted_songs = []
    for song in songs:
        print(song.title, fuzz.partial_ratio(song.title.lower(), query.lower()))
        unsorted_songs.append((song.title, song))
    
    sorted_songs = process.extract(query, unsorted_songs, limit=10)

    songs = []
    for song in sorted_songs:
        songs.append(song[0][1])

    if not songs:
        get_songs(request, query)

    return render(request, "search/index.html", {
        "songs": songs
    })

def song_view(request, song_id):
    try:
        song = Song.objects.get(id=song_id)
    except:
        return HttpResponseRedirect(reverse("search"))
    
    return render(request, "search/song.html", {
        "song": song
    })

# API functions
def load_chordpro(request, song_id):
    try:
        song = Song.objects.get(id=song_id)
    except:
        return JsonResponse({"error": "Song not found."}, status=404)
    
    song.get_chordpro()

    if not song.chordpro:
        return JsonResponse({"error": "Chordpro file not found."}, status=404)
    
    file_path = song.chordpro.path
    with open(file_path, "r", encoding="utf-8") as f:
        chordpro = f.read()
        return JsonResponse({"chordpro": chordpro})