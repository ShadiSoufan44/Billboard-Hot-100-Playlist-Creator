import requests
from bs4 import BeautifulSoup
from decouple import config
import spotipy
from spotipy.oauth2 import SpotifyOAuth


URL = "https://www.billboard.com/charts/hot-100/"
date = input(
    "Which date do you want to go for billboard hot 100? Type the date in YYYY-MM-DD format: ")

response = (requests.get(URL + date))

# web scrape to find all of the song names from the top 100
soup = BeautifulSoup(response.text, 'html.parser')
song_names = soup.find_all(
    name="h3", id="title-of-a-story", class_="a-no-trucate")
song_list = [song.getText().strip("\n\t") for song in song_names]
year = date.split("-")[0]

# get env variables
CLIENT_ID = config("CLIENT_ID")
CLIENT_SECRET = config("CLIENT_SECRET")

# authenticate with spotipy, set redirect URI to a website
sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        scope="playlist-modify-private",
        redirect_uri="https://www.billboard.com/charts/hot-100/",
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        show_dialog=True,
        cache_path="token.txt"
    )
)

# grab your user_id
user_id = sp.current_user()["id"]


song_uris = []

# loop through song list and then add song uris to song_uris array
for song in range(len(song_list)):
    result = sp.search(q=f"track:{song_list[song]} year:{year}", type="track")

    # keep track of current song that is being downloaded
    print(f"Loading Song {song}:")
    try:
        uri = result["tracks"]["items"][0]["uri"]
        song_uris.append(uri)
    except IndexError:
        print(f"{song_list[song]} doesn't exist in Spotify. Skipped.")

print("Finished! Starting to Make Playlist")

# creating the actual spotify playlist
playlist = sp.user_playlist_create(
    user=user_id, name=f"{date} Billboard 100", public=False)

# add song URIs to playlust
sp.playlist_add_items(playlist_id=playlist["id"], items=song_uris)

print("Playlist made! ")
