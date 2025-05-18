from flask import Flask, request, jsonify
import requests
from spotify_auth import get_access_token
from flask import send_from_directory
app = Flask(__name__)

# Search for artist ID
def get_artist_id(artist_name, token):
    url = f"https://api.spotify.com/v1/search"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"q": artist_name, "type": "artist", "limit": 1}

    response = requests.get(url, headers=headers, params=params)
    results = response.json()
    items = results.get('artists', {}).get('items', [])
    
    if items:
        return items[0]['id']
    return None

# Fetch albums
def get_albums(artist_id, token):
    url = f"https://api.spotify.com/v1/artists/{artist_id}/albums"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"include_groups": "album", "limit": 10}

    response = requests.get(url, headers=headers, params=params)
    albums_data = response.json()
    
    albums = [{
        "name": album["name"],
        "spotify_url": album["external_urls"]["spotify"],
        "release_date": album.get("release_date")
    } for album in albums_data.get("items", [])]
    return albums


# Endpoint to get artist albums
@app.route('/artist-albums')
def artist_albums():
    artist_name = request.args.get('artist_name')
    if not artist_name:
        return jsonify({"error": "artist_name query parameter is required"}), 400

    token = get_access_token()
    artist_id = get_artist_id(artist_name, token)

    if not artist_id:
        return jsonify({"error": "Artist not found"}), 404

    albums = get_albums(artist_id, token)
    return jsonify({"artist": artist_name, "albums": albums})

@app.route('/artist-top-tracks', methods=['GET'])
def get_artist_top_tracks():
    artist_name = request.args.get('artist_name')
    if not artist_name:
        return jsonify({"error": "Artist name is required"}), 400

    access_token = get_access_token()
    headers = {"Authorization": f"Bearer {access_token}"}

    # Step 1: Search for artist ID
    search_url = f"https://api.spotify.com/v1/search"
    search_params = {
        "q": artist_name,
        "type": "artist",
        "limit": 1
    }
    search_response = requests.get(search_url, headers=headers, params=search_params)
    search_data = search_response.json()

    if not search_data['artists']['items']:
        return jsonify({"error": "Artist not found"}), 404

    artist_id = search_data['artists']['items'][0]['id']

    # Step 2: Get Top Tracks
    top_tracks_url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks"
    top_tracks_params = {
        "market": "US"  # or your preferred country code
    }

    top_tracks_response = requests.get(top_tracks_url, headers=headers, params=top_tracks_params)
    tracks_data = top_tracks_response.json()

    top_tracks = [{
        "name": track["name"],
        "album": track["album"]["name"],
        "preview_url": track["preview_url"],
        "external_url": track["external_urls"]["spotify"]
    } for track in tracks_data.get("tracks", [])]

    return jsonify(top_tracks)

# Search for tracks by name
@app.route('/search-track', methods=['GET'])
def search_track():
    track_name = request.args.get('track_name')
    if not track_name:
        return jsonify({"error": "track_name query parameter is required"}), 400

    token = get_access_token()
    headers = {"Authorization": f"Bearer {token}"}
    url = "https://api.spotify.com/v1/search"
    params = {
        "q": track_name,
        "type": "track",
        "limit": 5  # get top 5 matching tracks
    }
    response = requests.get(url, headers=headers, params=params)
    data = response.json()

    tracks = []
    for item in data.get('tracks', {}).get('items', []):
        tracks.append({
            "track_name": item['name'],
            "artist": item['artists'][0]['name'],
            "album": item['album']['name'],
            "preview_url": item['preview_url'],
            "spotify_url": item['external_urls']['spotify']
        })

    return jsonify(tracks)


# Get audio features of a track by track ID
@app.route('/track-audio-features', methods=['GET'])
def track_audio_features():
    track_id = request.args.get('track_id')
    if not track_id:
        return jsonify({"error": "track_id query parameter is required"}), 400

    token = get_access_token()
    headers = {"Authorization": f"Bearer {token}"}
    url = f"https://api.spotify.com/v1/audio-features/{track_id}"

    response = requests.get(url, headers=headers)
    data = response.json()

    # return key audio features
    audio_features = {
        "danceability": data.get("danceability"),
        "energy": data.get("energy"),
        "speechiness": data.get("speechiness"),
        "acousticness": data.get("acousticness"),
        "instrumentalness": data.get("instrumentalness"),
        "liveness": data.get("liveness"),
        "valence": data.get("valence"),
        "tempo": data.get("tempo")
    }

    return jsonify(audio_features)

# 4. Get tracks from a playlist by playlist ID
@app.route('/playlist-tracks', methods=['GET'])
def get_playlist_tracks():
    playlist_id = request.args.get('playlist_id')
    if not playlist_id:
        return jsonify({"error": "playlist_id query parameter is required"}), 400

    token = get_access_token()
    headers = {"Authorization": f"Bearer {token}"}
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"

    response = requests.get(url, headers=headers)
    data = response.json()

    tracks = []
    for item in data.get('items', []):
        track = item.get('track', {})
        tracks.append({
            "track_name": track.get('name'),
            "artist": track.get('artists')[0].get('name') if track.get('artists') else None,
            "album": track.get('album').get('name') if track.get('album') else None,
            "spotify_url": track.get('external_urls', {}).get('spotify'),
            "preview_url": track.get('preview_url')
        })

    return jsonify(tracks)


# 5. Get new releases
@app.route('/new-releases', methods=['GET'])
def get_new_releases():
    token = get_access_token()
    headers = {"Authorization": f"Bearer {token}"}
    url = "https://api.spotify.com/v1/browse/new-releases"
    params = {"limit": 10}  # top 10 new releases

    response = requests.get(url, headers=headers, params=params)
    data = response.json()

    releases = []
    for album in data.get('albums', {}).get('items', []):
        releases.append({
            "album_name": album.get('name'),
            "artist": album.get('artists')[0].get('name') if album.get('artists') else None,
            "release_date": album.get('release_date'),
            "spotify_url": album.get('external_urls', {}).get('spotify')
        })

    return jsonify(releases)

@app.route('/')
def home():
    return send_from_directory('.', 'index.html')


if __name__ == '__main__':
    app.run(debug=True)
