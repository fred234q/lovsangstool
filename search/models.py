from django.db import models
from django.core.files import File

import requests
import os

class Song(models.Model):
    title = models.CharField(max_length=64)
    url = models.URLField()
    source = models.ForeignKey("Source", on_delete=models.CASCADE, related_name="songs")
    chordpro = models.FileField()

    def __str__(self):
        return self.title
    
    def get_chordpro(self):
        if self.source.name == "WorshipToday" and not self.chordpro:
            url_cutoff = len("https://worshiptoday.dk/lovsange/")
            path = self.url[url_cutoff:len(self.url) - 1]
            chordpro_url = f"https://worshiptoday.dk/lovsange/download/{path}.cho"

            r = requests.get(chordpro_url)

            filename = f"{path}.chordpro"
            with open(filename, "wb") as fd:
                for chunk in r.iter_content(chunk_size=128):
                    fd.write(chunk)
            
            with open(filename, "rb") as fd:
                self.chordpro.save(f"songs/{filename}", File(fd))
            os.remove(filename)

class Source(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name