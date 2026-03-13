from .forms import PlaylistForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Artist, Album, Playlist
from .models import Track, Playlist
from django.db.models import Q # Importuj Q pro komplexní dotazy
from django.contrib.auth import login
from .forms import SignUpForm

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) # Automaticky přihlásí uživatele po registraci
            return redirect('dashboard')
    else:
        form = SignUpForm()
    return render(request, 'melody/signup.html', {'form': form})

@login_required
def search(request):
    query = request.GET.get('q') # Získáme text z URL (např. ?q=linkin)
    results_tracks = []
    results_artists = []
    
    if query:
        # Hledáme skladby, které mají query v názvu
        results_tracks = Track.objects.filter(title__icontains=query)
        # Hledáme interprety, kteří mají query ve jméně
        results_artists = Artist.objects.filter(name__icontains=query)
    
    context = {
        'query': query,
        'tracks': results_tracks,
        'artists': results_artists,
    }
    return render(request, 'melody/search_results.html', context)

@login_required
def add_to_playlist(request, track_id):
    if request.method == 'POST':
        track = get_object_or_404(Track, id=track_id)
        playlist_id = request.POST.get('playlist_id')
        playlist = get_object_or_404(Playlist, id=playlist_id, user=request.user)
        
        playlist.tracks.add(track) # Tady se děje ta magie M:N vztahu
        return redirect('album_detail', album_id=track.album.id)
    return redirect('dashboard')

def landing_page(request):
    # Pokud je uživatel přihlášený, přesměrujeme ho rovnou na dashboard
    if request.user.is_authenticated:
        return redirect('dashboard')
    # Jinak mu ukážeme úvodní stránku
    return render(request, 'melody/landing_page.html')

@login_required(login_url='/admin/login/') # Zatím využijeme přihlašování z adminu
def dashboard(request):
    # Vytáhneme z databáze nejnovější alba a interprety
    recent_albums = Album.objects.all().order_by('-release_date')[:6]
    artists = Artist.objects.all()[:6]
    user_playlists = Playlist.objects.filter(user=request.user)
    
    context = {
        'recent_albums': recent_albums,
        'artists': artists,
        'user_playlists': user_playlists,
    }
    return render(request, 'melody/dashboard.html', context)

@login_required(login_url='/admin/login/')
def artist_detail(request, artist_id):
    artist = get_object_or_404(Artist, id=artist_id)
    return render(request, 'melody/artist_detail.html', {'artist': artist})

@login_required(login_url='/admin/login/')
def album_detail(request, album_id):
    album = get_object_or_404(Album, id=album_id)
    return render(request, 'melody/album_detail.html', {'album': album})

@login_required(login_url='/admin/login/')
def playlists(request):
    user_playlists = Playlist.objects.filter(user=request.user)
    return render(request, 'melody/playlists.html', {'user_playlists': user_playlists})

@login_required(login_url='/admin/login/')
def playlist_detail(request, playlist_id):
    playlist = get_object_or_404(Playlist, id=playlist_id, user=request.user)
    return render(request, 'melody/playlist_detail.html', {'playlist': playlist})
@login_required(login_url='/admin/login/')
def create_playlist(request):
    if request.method == 'POST':
        # Pokud uživatel formulář odeslal
        form = PlaylistForm(request.POST)
        if form.is_valid():
            # Uložíme formulář do paměti, ale zatím ne do databáze (commit=False)
            new_playlist = form.save(commit=False)
            # Musíme mu totiž přiřadit autora (aktuálně přihlášeného uživatele)
            new_playlist.user = request.user
            # Nyní můžeme bezpečně uložit do databáze
            new_playlist.save()
            # A přesměrujeme uživatele do jeho knihovny
            return redirect('playlists')
    else:
        # Pokud uživatel na stránku teprve přišel, ukážeme mu prázdný formulář
        form = PlaylistForm()
        
    return render(request, 'melody/create_playlist.html', {'form': form})

@login_required
def remove_from_playlist(request, playlist_id, track_id):
    playlist = get_object_or_404(Playlist, id=playlist_id, user=request.user)
    track = get_object_or_404(Track, id=track_id)
    
    playlist.tracks.remove(track) # Odstraní pouze vazbu, ne skladbu z DB
    return redirect('playlist_detail', playlist_id=playlist.id)