from typing import List, Optional

from django.db.models import Avg
from django.shortcuts import get_object_or_404
from ninja import NinjaAPI, Schema
from ninja.security import django_auth

from .models import Artist, Comment, FeaturedArtist, Genre, Rating, Track

api = NinjaAPI(title="MelodyStream API", description="REST API pro hudební streamovací platformu MelodyStream.")


# ---------- Schemas ----------

class MessageSchema(Schema):
    message: str


class GenreOut(Schema):
    id: int
    name: str


class ArtistOut(Schema):
    id: int
    name: str
    formed_year: Optional[int] = None
    country: str = ""
    photo_url: str = ""


class TrackOut(Schema):
    id: int
    title: str
    album_title: str = ""
    release_year: Optional[int] = None
    duration_seconds: Optional[int] = None
    audio_url: str = ""
    cover_url: str = ""
    artist: Optional[ArtistOut] = None
    featured_artists: List[ArtistOut] = []
    genres: List[GenreOut] = []
    average_rating: Optional[float] = None


class TrackListItem(Schema):
    id: int
    title: str
    release_year: Optional[int] = None
    cover_url: str = ""
    artist: Optional[str] = None
    average_rating: Optional[float] = None


class TrackListingSchema(Schema):
    count: int
    results: List[TrackListItem]


class TrackIn(Schema):
    title: str
    album_title: str = ""
    release_year: Optional[int] = None
    duration_seconds: Optional[int] = None
    audio_url: str = ""
    cover_url: str = ""
    artist_id: Optional[int] = None
    featured_artist_ids: List[int] = []
    genre_ids: List[int] = []


class CommentOut(Schema):
    id: int
    track_id: int
    user: str
    text: str
    created_at: str


class CommentIn(Schema):
    text: str


class RatingOut(Schema):
    id: int
    track_id: int
    user: str
    value: int


class RatingIn(Schema):
    value: int


# ---------- Helpers ----------

def _track_to_out(track: Track) -> dict:
    avg = track.ratings.aggregate(avg=Avg("value"))["avg"]
    return {
        "id": track.id,
        "title": track.title,
        "album_title": track.album_title,
        "release_year": track.release_year,
        "duration_seconds": track.duration_seconds,
        "audio_url": track.audio_url,
        "cover_url": track.cover_url,
        "artist": (
            {
                "id": track.artist.id,
                "name": track.artist.name,
                "formed_year": track.artist.formed_year,
                "country": track.artist.country,
                "photo_url": track.artist.photo_url,
            }
            if track.artist
            else None
        ),
        "featured_artists": [
            {
                "id": fa.id,
                "name": fa.name,
                "formed_year": fa.formed_year,
                "country": fa.country,
                "photo_url": fa.photo_url,
            }
            for fa in track.featured_artists.all()
        ],
        "genres": [{"id": g.id, "name": g.name} for g in track.genres.all()],
        "average_rating": round(avg, 2) if avg is not None else None,
    }


def _apply_track_input(track: Track, payload: TrackIn) -> Track:
    track.title = payload.title
    track.album_title = payload.album_title
    track.release_year = payload.release_year
    track.duration_seconds = payload.duration_seconds
    track.audio_url = payload.audio_url
    track.cover_url = payload.cover_url
    if payload.artist_id is not None:
        track.artist = get_object_or_404(Artist, pk=payload.artist_id)
    else:
        track.artist = None
    track.save()
    track.featured_artists.set(FeaturedArtist.objects.filter(id__in=payload.featured_artist_ids))
    track.genres.set(Genre.objects.filter(id__in=payload.genre_ids))
    return track


# ---------- Track endpoints ----------

@api.get("/track", response=TrackListingSchema, tags=["tracks"])
def list_tracks(request, q: str = "", release_year: Optional[int] = None,
                genre_id: Optional[int] = None, artist_id: Optional[int] = None,
                featured_artist_id: Optional[int] = None):
    tracks = Track.objects.all().annotate(avg=Avg("ratings__value")).select_related("artist")
    if q:
        tracks = tracks.filter(title__icontains=q)
    if release_year is not None:
        tracks = tracks.filter(release_year=release_year)
    if genre_id is not None:
        tracks = tracks.filter(genres__id=genre_id)
    if artist_id is not None:
        tracks = tracks.filter(artist__id=artist_id)
    if featured_artist_id is not None:
        tracks = tracks.filter(featured_artists__id=featured_artist_id)
    tracks = tracks.distinct()

    results = [
        {
            "id": t.id,
            "title": t.title,
            "release_year": t.release_year,
            "cover_url": t.cover_url,
            "artist": t.artist.name if t.artist else None,
            "average_rating": round(t.avg, 2) if t.avg is not None else None,
        }
        for t in tracks
    ]
    return {"count": len(results), "results": results}


@api.get("/track/{track_id}", response={200: TrackOut, 404: MessageSchema}, tags=["tracks"])
def get_track(request, track_id: int):
    try:
        track = Track.objects.prefetch_related("featured_artists", "genres").select_related("artist").get(pk=track_id)
    except Track.DoesNotExist:
        return 404, {"message": "Skladba nebyla nalezena."}
    return _track_to_out(track)


@api.post("/track", response={201: TrackOut}, auth=django_auth, tags=["tracks"])
def create_track(request, payload: TrackIn):
    track = _apply_track_input(Track(), payload)
    return 201, _track_to_out(track)


@api.put("/track/{track_id}", response={200: TrackOut, 404: MessageSchema}, auth=django_auth, tags=["tracks"])
def update_track(request, track_id: int, payload: TrackIn):
    try:
        track = Track.objects.get(pk=track_id)
    except Track.DoesNotExist:
        return 404, {"message": "Skladba nebyla nalezena."}
    track = _apply_track_input(track, payload)
    return _track_to_out(track)


@api.delete("/track/{track_id}", response={204: None, 404: MessageSchema}, auth=django_auth, tags=["tracks"])
def delete_track(request, track_id: int):
    try:
        Track.objects.get(pk=track_id).delete()
    except Track.DoesNotExist:
        return 404, {"message": "Skladba nebyla nalezena."}
    return 204, None


# ---------- Comment endpoints ----------

@api.get("/track/{track_id}/comments", response=List[CommentOut], tags=["comments"])
def list_comments(request, track_id: int):
    comments = Comment.objects.filter(track_id=track_id).select_related("user")
    return [
        {
            "id": c.id,
            "track_id": c.track_id,
            "user": c.user.username,
            "text": c.text,
            "created_at": c.created_at.isoformat(),
        }
        for c in comments
    ]


@api.post("/track/{track_id}/comments", response={201: CommentOut, 404: MessageSchema},
          auth=django_auth, tags=["comments"])
def create_comment(request, track_id: int, payload: CommentIn):
    try:
        track = Track.objects.get(pk=track_id)
    except Track.DoesNotExist:
        return 404, {"message": "Skladba nebyla nalezena."}
    c = Comment.objects.create(track=track, user=request.user, text=payload.text)
    return 201, {
        "id": c.id,
        "track_id": c.track_id,
        "user": c.user.username,
        "text": c.text,
        "created_at": c.created_at.isoformat(),
    }


# ---------- Rating endpoints ----------

@api.get("/track/{track_id}/ratings", response=List[RatingOut], tags=["ratings"])
def list_ratings(request, track_id: int):
    ratings = Rating.objects.filter(track_id=track_id).select_related("user")
    return [
        {"id": r.id, "track_id": r.track_id, "user": r.user.username, "value": r.value}
        for r in ratings
    ]


@api.put("/track/{track_id}/rate", response={200: RatingOut, 404: MessageSchema},
         auth=django_auth, tags=["ratings"])
def rate_track(request, track_id: int, payload: RatingIn):
    try:
        track = Track.objects.get(pk=track_id)
    except Track.DoesNotExist:
        return 404, {"message": "Skladba nebyla nalezena."}
    rating, _ = Rating.objects.update_or_create(
        track=track, user=request.user, defaults={"value": payload.value}
    )
    return {"id": rating.id, "track_id": rating.track_id, "user": rating.user.username, "value": rating.value}
