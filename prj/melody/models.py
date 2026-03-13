from django.db import models
from django.contrib.auth.models import User

class Artist(models.Model):
    name = models.CharField(max_length=200, verbose_name="Jméno interpreta")
    bio = models.TextField(blank=True, null=True, verbose_name="Biografie")
    # Pro obrázky je potřeba mít nainstalovanou knihovnu Pillow (pip install Pillow)
    image = models.ImageField(upload_to='artists/', blank=True, null=True, verbose_name="Fotografie")

    def __str__(self):
        return self.name

class Album(models.Model):
    title = models.CharField(max_length=200, verbose_name="Název alba")
    release_date = models.DateField(verbose_name="Datum vydání")
    cover = models.ImageField(upload_to='albums/', blank=True, null=True, verbose_name="Obal alba")
    # Vztah M:1 k interpretovi
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name='albums', verbose_name="Interpret")

    def __str__(self):
        return f"{self.title} ({self.artist.name})"

class Track(models.Model):
    title = models.CharField(max_length=200, verbose_name="Název skladby")
    duration = models.IntegerField(verbose_name="Délka (v sekundách)")
    audio_file = models.FileField(upload_to='tracks/', verbose_name="Audio soubor")
    genre = models.CharField(max_length=100, verbose_name="Žánr")
    # Vztah M:1 k albu
    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name='tracks', verbose_name="Album")

    def __str__(self):
        return self.title

class Playlist(models.Model):
    name = models.CharField(max_length=200, verbose_name="Název playlistu")
    is_public = models.BooleanField(default=False, verbose_name="Veřejný playlist")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Vytvořeno")
    # Vztah M:1 k uživateli
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='playlists', verbose_name="Vlastník")
    # Vztah M:N ke skladbám
    tracks = models.ManyToManyField(Track, related_name='playlists', blank=True, verbose_name="Skladby")

    def __str__(self):
        return self.name