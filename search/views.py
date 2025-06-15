from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from search.search import metasearch
from django import forms
from django.urls import reverse

# class SearchForm(forms.Form):
#     query = form.char

def index(request):
    return HttpResponseRedirect(reverse("search"))

def search_view(request):
    if not request.GET:
        return render(request, "search/index.html")
    
    query = request.GET["q"]
    results = metasearch(query)
    return render(request, "search/index.html", {
        "results": results
    })