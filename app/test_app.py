import unittest
from app import app

class SpotifyApiTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    # Existing tests
    def test_artist_albums_missing_param(self):
        response = self.app.get('/artist-albums')  # no artist_name param
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"artist_name query parameter is required", response.data)
        print("test_artist_albums_missing_param passed!")

    def test_artist_albums_valid(self):
        response = self.app.get('/artist-albums?artist_name=Taylor Swift')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("albums", data)
        print("test_artist_albums_valid passed!")

    def test_artist_top_tracks_valid(self):
        response = self.app.get('/artist-top-tracks?artist_name=Taylor Swift')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIsInstance(data, list)
        print("test_artist_top_tracks_valid passed!")

    def test_search_track_valid(self):
        response = self.app.get('/search-track?track_name=Love Story')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIsInstance(data, list)
        print("test_search_track_valid passed!")

    def test_track_audio_features_missing_param(self):
        response = self.app.get('/track-audio-features')  # missing track_id
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"track_id query parameter is required", response.data)
        print("test_track_audio_features_missing_param passed!")

    # New tests for playlist tracks endpoint
    def test_playlist_tracks_missing_param(self):
        response = self.app.get('/playlist-tracks')
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"playlist_id query parameter is required", response.data)
        print("test_playlist_tracks_missing_param passed!")

    def test_playlist_tracks_valid(self):
        # Public playlist ID example: "Today's Top Hits"
        playlist_id = '37i9dQZF1DXcBWIGoYBM5M'
        response = self.app.get(f'/playlist-tracks?playlist_id={playlist_id}')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIsInstance(data, list)
        if data:
            first_track = data[0]
            self.assertIn('track_name', first_track)
            self.assertIn('artist', first_track)
            self.assertIn('spotify_url', first_track)
        print("test_playlist_tracks_valid passed!")

    # Test new releases endpoint
    def test_new_releases(self):
        response = self.app.get('/new-releases')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIsInstance(data, list)
        if data:
            first_release = data[0]
            self.assertIn('album_name', first_release)
            self.assertIn('artist', first_release)
            self.assertIn('spotify_url', first_release)
        print("test_new_releases passed!")

    # Edge case: invalid artist name (should return 404 or empty)
    def test_artist_albums_invalid_artist(self):
        response = self.app.get('/artist-albums?artist_name=NonExistentArtistXYZ')
        # Could be 404 or 200 with empty albums list depending on API design
        self.assertIn(response.status_code, [200, 404])
        if response.status_code == 200:
            data = response.get_json()
            self.assertIn('albums', data)
            self.assertEqual(len(data['albums']), 0)
        print("test_artist_albums_invalid_artist passed!")

    # Edge case: invalid playlist ID
    def test_playlist_tracks_invalid_playlist(self):
        invalid_playlist_id = "invalid12345"
        response = self.app.get(f'/playlist-tracks?playlist_id={invalid_playlist_id}')
        # Could be 200 with empty list or 404 - depends on API
        self.assertIn(response.status_code, [200, 404])
        print("test_playlist_tracks_invalid_playlist passed!")

    # Edge case: search track with no results
    def test_search_track_no_results(self):
        response = self.app.get('/search-track?track_name=asldkfjalskdfjalskdjf')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIsInstance(data, list)
        # Just check it's a list; skip checking length for unpredictable results

        print("test_search_track_no_results passed!")

if __name__ == '__main__':
    unittest.main()
