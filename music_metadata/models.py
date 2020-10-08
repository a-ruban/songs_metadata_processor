from django.db import models


class Contributor(models.Model):
    name = models.CharField(max_length=200, null=True, blank=True, unique=True)


class Song(models.Model):
    title = models.CharField(max_length=300, null=True, blank=True)
    contributors = models.ManyToManyField(Contributor, 'contributed_songs')
    iswc = models.CharField(max_length=13, null=True, blank=True, unique=True)
