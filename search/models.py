from django.db import models
from django.core.files import File

import requests
import os
from bs4 import BeautifulSoup

class Song(models.Model):
    title = models.CharField(max_length=64)
    url = models.URLField(unique=True)
    source = models.ForeignKey("Source", on_delete=models.CASCADE, related_name="songs")
    chordpro = models.FileField(null=True, blank=True)
    main_version = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True, related_name="versions")

    def __str__(self):
        return self.title
    
    def is_main(self):
        return self.main_version == self or self.main_version == None
    
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
            # Add headers needed to not get flagged
            headers = {
                "User-Agent": "Mozilla/5.0",
            }   

            r = requests.get(
                self.url,
                headers=headers
                )

            # Get session cookie to retrive the right chordpro file
            cookies = {"PHPSESSID": r.cookies["PHPSESSID"]}

            r = requests.get(
                "https://lovsang.dk/song/download.php",
                headers=headers,
                cookies=cookies
                )
            
            # Manage encoding for æ, ø and å
            r.encoding = "iso-8859-1"

            # Find title from header
            title_header = r.headers["Content-Disposition"]
            title_start = title_header.find("\"") + 1
            title = title_header[title_start:len(title_header) - 1]

            filename = title
            with open(filename, "w", encoding="utf-8") as f:
                # Add line break missing from lovsang.dk chordpro files
                f.write("\n" + r.text)

            with open(filename, "r") as f:
                self.chordpro.save(f"songs/{filename}", File(f))
            os.remove(filename)
            
            return
        
        if self.source.name == "Worship Together":
            headers = {
                "User-Agent": "Mozilla/5.0",
            }

            cookies = {"yourAuthCookie": "CAC94B6526925B2FB3E13FDCBCE4564692CFE48B519E4A06FA0581AC345DBA0668B4CBDD422C781F69B0C447F2A1C7A4DA19189D462588C3E0075AB254710962FF85AEDE101BC51925AFCF7C007DF705A529ABBBF1A0E02209C7E6B65AB115AE9EA05588E2D283930695992BE86C3E5C790A52EC15A39ADE171AFC89FB25CB4E"}
            r = requests.get(
                self.url,
                headers=headers,
                cookies=cookies
                )
            soup = BeautifulSoup(r.text, "html.parser")

            chordpro_button = soup.find_all(class_="free-chords")
            path = chordpro_button[-1]["href"]
            chordpro_url = f"https://www.worshiptogether.com{path}"

            if path == "#chordsDownload":
                print("Error: Login cookie invalid.")
                return

            r = requests.get(
                chordpro_url,
                headers=headers,
                cookies=cookies
            )

            url_cutoff = len("https://www.worshiptogether.com/songs/")
            name = self.url[url_cutoff:len(self.url) - 1]

            filename = f"{name}.chordpro"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(r.text)

            with open(filename, "r") as f:
                self.chordpro.save(f"songs/{filename}", File(f))
            os.remove(filename)
            
            return

class Source(models.Model):
    name = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return self.name