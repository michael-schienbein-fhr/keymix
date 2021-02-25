from unittest import TestCase
from keymix import app
from keymix.util import get_keys, get_modes, get_id, get_genres
from keymix.auth import encodedData
import requests


class utilTestCase(TestCase):
    def setUp(self):
        """Add auth Token."""

        data = {
            'grant_type': 'client_credentials'
        }

        headers = {
            "Authorization": "Basic {}".format(encodedData)
        }

        resp = requests.post('https://accounts.spotify.com/api/token',
                             headers=headers, data=data).json()
        token = resp['access_token']
        
        self.token = token

    def tearDown(self):
        """Clean up any fouled transaction."""

        self.token = ''

    def test_get_keys(self):
        """Test to get list keys"""
        self.assertEqual(get_keys(), [('', 'Select a Song Key'), ('1', 'C'), ('2', 'C♯/D♭'), ('3', 'D'), ('4', 'D♯/E♭'), ('5', 'E'),
                                      ('6', 'F'), ('7', 'F♯/G♭'), ('8', 'G'), ('9', 'G♯/A♭'), ('10', 'A'), ('11', 'A♯/B♭'), ('12', 'B')])

    def test_get_modes(self):
        """Test to get list of modes"""
        self.assertEqual(get_modes(), [
                         ('', 'Select Major or Minor Key'), ('0', 'Minor'), ('1', 'Major')])

    def test_get_id(self):
        """Tests call to API for subsearch"""
        input_name = 'Daft Punk'
        input_type = 'artist'
        resp = get_id(input_name, input_type, self.token)
        self.assertEqual(resp['artists']['items'][0]['name'], 'Daft Punk')

    def test_get_genres(self):
        """Tests call to Spotify's API to get list of genres"""
        resp = get_genres(self.token)
        self.assertEqual(('house', 'House'), resp[55])
