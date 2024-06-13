from bs4 import BeautifulSoup
import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Spotify Authentication
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id="ffae1d2594724396ae38079612f8d1c6",
                                               client_secret="5a04c874e1fe47e9a4bb8a137e46df6f",
                                               redirect_uri="http://example.com",
                                               scope="playlist-modify-private",
                                               cache_path="token.txt",
                                               show_dialog=True))

user_id = sp.me()["id"]

# Scraping Billboard 100
date = input("Which Year do you want to travel to? Type the date in this format YYYY-MM-DD: ")
response = requests.get(f"https://www.billboard.com/charts/hot-100/{date}")
soup = BeautifulSoup(response.text, 'html.parser')

# Extract song titles and artist names
songs = soup.find_all("li", {"class": "o-chart-results-list__item"})

# Extract song titles and artist names
song_data = []
for song in songs:
    title_element = song.find("h3", id="title-of-a-story")
    artist_element = song.find("span", {"class": "c-label"})
    if title_element and artist_element:
        title = title_element.get_text(strip=True)
        artist = artist_element.get_text(strip=True)
        song_data.append((title, artist))

# Search Spotify for songs by title and artist
year = date.split("-")[0]
spotify_song_uris = []

for title, artist in song_data:
    result = sp.search(q=f"track:{title} artist:{artist} year:{year}", type="track", limit=1)
    try:
        uri = result["tracks"]["items"][0]["uri"]
        spotify_song_uris.append(uri)
    except IndexError:
        print(f"{title} by {artist} doesn't exist on Spotify. Skipped.")

# Create a new private playlist in Spotify
playlist_name = f"{date} Billboard 100"
playlist = sp.user_playlist_create(user=user_id, name=playlist_name, public=False, description="Live your time")

# Add songs found into the new playlist
playlist_id = playlist["id"]
if spotify_song_uris:
    sp.user_playlist_add_tracks(user=user_id, playlist_id=playlist_id, tracks=spotify_song_uris)

print(f"Playlist '{playlist_name}' created successfully with {len(spotify_song_uris)} tracks.")
