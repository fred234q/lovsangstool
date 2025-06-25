from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from search.search import metasearch
from django.urls import reverse
from search.models import Song, Source
from django.http import JsonResponse
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

    return HttpResponse(status=204)

def search_view(request):
    if not request.GET:
        return render(request, "search/index.html")
    
    query = request.GET["q"]
    songs = list(Song.objects.all())

    if not songs:
        get_songs(request, query)
        songs = list(Song.objects.all())

    # Sort songs by partial_ratio score
    songs.sort(key=lambda song: fuzz.partial_ratio(song.title.lower(), query.lower()))
    songs.reverse()

    # Request new songs if bad results
    if fuzz.partial_ratio(songs[0].title.lower(), query.lower()) < 90:
        get_songs(request, query)

        # Repeat songs retrieval
        songs = list(Song.objects.all())
        songs.sort(key=lambda song: fuzz.partial_ratio(song.title.lower(), query.lower()))
        songs.reverse()

    # Adjust amount of search results
    result_count = 10
    songs = songs[:result_count]

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