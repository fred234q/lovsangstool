from django.db import models

class Song(models.Model):
    title = models.CharField()
    link = models.URLField()