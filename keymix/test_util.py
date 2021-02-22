
from unittest import TestCase
from app import app
from util import *


class utilTestCase(TestCase):

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
        with app.test_client() as client:
            client.get('/auth')
            input_name = 'Daft Punk'
            input_type = 'artist'
            resp = get_id(input_name, input_type)
            session.clear()
            self.assertEqual(resp['artists']['items'][0]['name'], 'Daft Punk')

    def test_get_genres(self):
        """Tests call to Spotify's API to get list of genres"""
        with app.test_client() as client:
            client.get('/auth')
            resp = get_genres()
            session.clear()
            self.assertEqual(('house', 'House'), resp[55])
