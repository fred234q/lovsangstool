from django.db import models

class Song(models.Model):
    title = models.CharField(max_length=64)
    url = models.URLField()