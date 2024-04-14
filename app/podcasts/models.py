from django.db import models

class Episodes(models.Model):
    link = models.CharField(max_length=200)
    episode = models.IntegerField()
    title = models.CharField(max_length=200)
    date_on_air = models.CharField(max_length=200)
    description = models.CharField(max_length=200)
    transcript = models.TextField()
