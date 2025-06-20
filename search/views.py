from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from search.search import metasearch
from django.urls import reverse
from search.models import Song, Source
from django.http import JsonResponse
from fuzzywuzzy import process

def index(request):
    return HttpResponseRedirect(reverse("search"))

def search_view(request):
    if not request.GET:
        return render(request, "search/index.html")
    
    query = request.GET["q"]
    results = metasearch(query)

    songs = []
    for result in results:
        title = result["title"]
        url = result["url"]
        source_name = result["source"]
        
        source, created = Source.objects.get_or_create(name=source_name)
        song, created = Song.objects.get_or_create(title=title, url=url, source=source)
        songs.append(song)

    return render(request, "search/index.html", {
        "songs": songs
    })

def new_search_view(request):
    if not request.GET:
        return render(request, "search/index.html")
    
    query = request.GET["q"]
    songs = Song.objects.all()
    results = []
    for song in songs:
        results.append(song.title)

    songs = process.extract(query, results, limit=10)

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