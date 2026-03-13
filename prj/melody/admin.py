from django.contrib import admin
from .models import Artist, Album, Track, Playlist

# Zobrazení interpretů v adminu
@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

# Zobrazení alb
@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist', 'release_date')
    list_filter = ('artist', 'release_date')
    search_fields = ('title',)

# Zobrazení skladeb
@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
    list_display = ('title', 'album', 'genre', 'duration')
    list_filter = ('genre', 'album')
    search_fields = ('title',)

# Zobrazení playlistů
@admin.register(Playlist)
class PlaylistAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'is_public', 'created_at')
    list_filter = ('is_public', 'created_at')
    search_fields = ('name', 'user__username')