from django.db import models

class Song(models.Model):
    title = models.CharField()
    url = models.URLField()