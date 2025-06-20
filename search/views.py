from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from search.search import metasearch
from django.urls import reverse
from search.models import Song, Source

def index(request):
    return HttpResponseRedirect(reverse("search"))

def search_view(request):
    if not request.GET:
        return render(request, "search/index.html")
    
    query = request.GET["q"]
    results = metasearch(query)
    for result in results:
        title = result["title"]
        url = result["url"]
        source_name = result["source"]
        
        source, created = Source.objects.get_or_create(name=source_name)
        song, created = Song.objects.get_or_create(title=title, url=url, source=source)

    return render(request, "search/index.html", {
        "results": results
    })