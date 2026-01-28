from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from search.search import metasearch, scrape_all
from django.urls import reverse
from search.models import Song, Source
from django.http import JsonResponse
from thefuzz import fuzz
from thefuzz import process

# Variables
SORTING_ALG = "process"
RESULT_COUNT = 10

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
        song, created = Song.objects.get_or_create(url=url, defaults={
            "title":title,
            "source":source
        })
        if created:
            song.main_version = song
            song.save()
        print(f"{song}: {song.main_version}")
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
    
    if SORTING_ALG == "process":
        songs = process.extract(query, songs, limit=RESULT_COUNT)
        songs = [song[0] for song in songs]

    if SORTING_ALG == "partial_ratio":
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
    songs = songs[:RESULT_COUNT]

    return render(request, "search/index.html", {
        "songs": songs
    })

def update_results_view(request):
    query = request.GET["q"]
    get_songs(request, query)
    return HttpResponseRedirect(reverse("search") + f"?q={query}")

def song_view(request, song_id):
    try:
        song = Song.objects.get(id=song_id)
    except:
        return HttpResponseRedirect(reverse("search"))
    
    query = song.title
    results = list(Song.objects.all())

    if SORTING_ALG == "process":
        results = process.extract(query, results, limit=RESULT_COUNT)
        results = [song[0] for song in results]

    if SORTING_ALG == "partial_ratio":
        # Sort songs by partial_ratio score
        results.sort(key=lambda song: fuzz.partial_ratio(song.title.lower(), query.lower()))
        results.reverse()

    # Adjust amount of search results
    results = results[:RESULT_COUNT]
    
    return render(request, "search/song.html", {
        "song": song,
        "results": results
    })

def get_all(request):
    results = scrape_all()

    songs = []
    for result in results:
        title = result["title"]
        url = result["url"]
        source_name = result["source"]
        
        source, created = Source.objects.get_or_create(name=source_name)
        song, created = Song.objects.get_or_create(url=url, defaults={
            "title": title,
            "source": source
        })
        if created:
            song.main_version = song
            song.save()
        print(f"{song}: {song.main_version}")
        songs.append(song)

    return HttpResponseRedirect(reverse("index"))


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

def merge_songs(request, song_id):
    if request.method == "POST":
        primary_id = song_id
        secondary_id = request.POST.get("secondary-id")
        mode = request.POST.get("mode")

        try:
            primary_song = Song.objects.get(pk=primary_id)
            secondary_song = Song.objects.get(pk=secondary_id)
            main_song = primary_song.main_version

        except:
            return HttpResponseRedirect(reverse("song", kwargs={"song_id": song_id}))
        
        if mode == "add":
            secondary_song.main_version = main_song

        elif mode == "remove":
            secondary_song.main_version = secondary_song

        elif mode == "make-main":
            for version in main_song.versions.all():
                version.main_version = secondary_song
                version.save()
                # Update model from database to get new correct main
                secondary_song.refresh_from_db()

        secondary_song.save()

        return HttpResponseRedirect(reverse("song", kwargs={"song_id": song_id}))

    
    else:
        return HttpResponseRedirect(reverse("song", kwargs={"song_id": song_id}))