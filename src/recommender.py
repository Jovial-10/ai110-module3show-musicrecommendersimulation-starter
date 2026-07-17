import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool
    target_valence: Optional[float] = None

# Point weights for the Algorithm Recipe. Kept as module-level constants so
# the weighting strategy is easy to find, explain, and tune in one place.
GENRE_MATCH_POINTS = 2.0
MOOD_MATCH_POINTS = 1.0
ENERGY_MAX_POINTS = 1.5
ACOUSTIC_MAX_POINTS = 1.0
VALENCE_MAX_POINTS = 0.75

# Below this many points a per-feature contribution isn't worth mentioning
# in a human-readable explanation.
REASON_THRESHOLD = 0.05

def _score(
    genre: Optional[str],
    mood: Optional[str],
    energy: float,
    acousticness: float,
    valence: Optional[float],
    favorite_genre: Optional[str],
    favorite_mood: Optional[str],
    target_energy: float,
    likes_acoustic: bool,
    target_valence: Optional[float],
) -> Tuple[float, List[str]]:
    """Apply the Algorithm Recipe's point weights and return (score, reasons)."""
    score = 0.0
    reasons: List[str] = []

    if genre == favorite_genre:
        score += GENRE_MATCH_POINTS
        reasons.append(f"genre match (+{GENRE_MATCH_POINTS:.2f})")

    if mood == favorite_mood:
        score += MOOD_MATCH_POINTS
        reasons.append(f"mood match (+{MOOD_MATCH_POINTS:.2f})")

    energy_pts = ENERGY_MAX_POINTS * max(0.0, 1.0 - abs(energy - target_energy))
    score += energy_pts
    if energy_pts > REASON_THRESHOLD:
        reasons.append(f"energy similarity (+{energy_pts:.2f})")

    acoustic_pts = acousticness if likes_acoustic else (1.0 - acousticness)
    acoustic_pts *= ACOUSTIC_MAX_POINTS
    score += acoustic_pts
    if acoustic_pts > REASON_THRESHOLD:
        label = "acoustic" if likes_acoustic else "non-acoustic"
        reasons.append(f"{label} fit (+{acoustic_pts:.2f})")

    if target_valence is not None and valence is not None:
        valence_pts = VALENCE_MAX_POINTS * max(0.0, 1.0 - abs(valence - target_valence))
        score += valence_pts
        if valence_pts > REASON_THRESHOLD:
            reasons.append(f"valence similarity (+{valence_pts:.2f})")

    return score, reasons

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def _score_song(self, user: UserProfile, song: Song) -> Tuple[float, List[str]]:
        """Score a Song against a UserProfile using the Algorithm Recipe."""
        return _score(
            genre=song.genre,
            mood=song.mood,
            energy=song.energy,
            acousticness=song.acousticness,
            valence=song.valence,
            favorite_genre=user.favorite_genre,
            favorite_mood=user.favorite_mood,
            target_energy=user.target_energy,
            likes_acoustic=user.likes_acoustic,
            target_valence=user.target_valence,
        )

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return the user's top k songs, ranked by score with an energy-closeness tiebreak."""
        scored = [(song, *self._score_song(user, song)) for song in self.songs]
        scored.sort(key=lambda item: (-item[1], abs(item[0].energy - user.target_energy)))
        return [song for song, _score, _reasons in scored[:k]]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return a human-readable sentence explaining a song's score for the user."""
        score, reasons = self._score_song(user, song)
        if not reasons:
            return f'"{song.title}" scored {score:.2f} points but did not strongly match your stated preferences.'
        return f'"{song.title}" scored {score:.2f} points because of: ' + ", ".join(reasons) + "."

def load_songs(csv_path: str) -> List[Dict]:
    """Read songs.csv into a list of typed song dictionaries."""
    songs = []
    with open(csv_path, newline="") as f:
        for row in csv.DictReader(f):
            songs.append({
                "id": int(row["id"]),
                "title": row["title"],
                "artist": row["artist"],
                "genre": row["genre"],
                "mood": row["mood"],
                "energy": float(row["energy"]),
                "tempo_bpm": float(row["tempo_bpm"]),
                "valence": float(row["valence"]),
                "danceability": float(row["danceability"]),
                "acousticness": float(row["acousticness"]),
            })
    return songs

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Score one song dict against user_prefs using the Algorithm Recipe."""
    return _score(
        genre=song.get("genre"),
        mood=song.get("mood"),
        energy=song.get("energy", 0.0),
        acousticness=song.get("acousticness", 0.0),
        valence=song.get("valence"),
        favorite_genre=user_prefs.get("genre"),
        favorite_mood=user_prefs.get("mood"),
        target_energy=user_prefs.get("energy", 0.0),
        likes_acoustic=user_prefs.get("likes_acoustic", False),
        target_valence=user_prefs.get("target_valence"),
    )

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """Score every song, rank them, and return the top k as (song, score, explanation)."""
    target_energy = user_prefs.get("energy", 0.0)
    ranked = sorted(
        ((song, *score_song(user_prefs, song)) for song in songs),
        key=lambda item: (-item[1], abs(item[0].get("energy", 0.0) - target_energy)),
    )
    return [
        (song, score, ", ".join(reasons) if reasons else "no strong matches")
        for song, score, reasons in ranked[:k]
    ]
