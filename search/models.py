from django.db import models
from django.core.files import File

import requests
import os
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

class Song(models.Model):
    title = models.CharField(max_length=64)
    url = models.URLField()
    source = models.ForeignKey("Source", on_delete=models.CASCADE, related_name="songs")
    chordpro = models.FileField()

    def __str__(self):
        return self.title
    
    def get_chordpro(self):
        if self.chordpro:
            return
        
        if self.source.name == "WorshipToday":
            url_cutoff = len("https://worshiptoday.dk/lovsange/")
            path = self.url[url_cutoff:len(self.url) - 1]
            chordpro_url = f"https://worshiptoday.dk/lovsange/download/{path}.cho"

            r = requests.get(chordpro_url)

            filename = f"{path}.chordpro"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(r.text)

            with open(filename, "r") as f:
                self.chordpro.save(f"songs/{filename}", File(f))
            os.remove(filename)
            
            return
        
        if self.source.name == "lovsang.dk":
            headers = {
                "User-Agent": "Mozilla/5.0",
            }   

            r = requests.get(
                self.url,
                headers=headers
                )

            cookies = {"PHPSESSID": r.cookies["PHPSESSID"]}

            r = requests.get(
                "https://lovsang.dk/song/download.php",
                headers=headers,
                cookies=cookies
                )

            # Find title from header
            title_header = r.headers["Content-Disposition"]
            title_start = title_header.find("\"") + 1
            title = title_header[title_start:len(title_header) - 1]

            filename = title
            with open(filename, "w", encoding="utf-8") as f:
                f.write("\n" + r.text)

            with open(filename, "r") as f:
                self.chordpro.save(f"songs/{filename}", File(f))
            os.remove(filename)
            
            return

class Source(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name