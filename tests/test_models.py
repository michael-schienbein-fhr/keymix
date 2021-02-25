from unittest import TestCase

from keymix import app
from keymix.models import db, Song, Playlist, PlaylistSong, User

# Use test database and don't clutter tests with SQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///keymix_test'
app.config['SQLALCHEMY_ECHO'] = False

db.drop_all()
db.create_all()


class UserModelTestCase(TestCase):
    """Tests for model for User class."""

    def setUp(self):
        """Clean up any existing users."""
        PlaylistSong.query.delete()
        Song.query.delete()
        Playlist.query.delete()
        User.query.delete()

    def tearDown(self):
        """Clean up any fouled transaction."""

        db.session.rollback()

    def test_create_user(self):
        u = User.register(username="test1", password="test1",
                          email="test@test.com")
        db.session.add(u)
        db.session.commit()

        self.assertEqual(u.username, "test1")

    def test_authenticate(self):
        r = User.register(username="test1", password="test1",
                          email="test@test.com")
        db.session.add(r)
        db.session.commit()
        u = User.authenticate(username="test1", password="test1")

        self.assertEqual(r.username, "test1")
        self.assertEqual(u.username, "test1")


class SongModelTestCase(TestCase):
    """Tests for model for song class."""

    def setUp(self):
        """Clean up any existing users."""
        PlaylistSong.query.delete()
        Song.query.delete()
        Playlist.query.delete()
        User.query.delete()

    def tearDown(self):
        """Clean up any fouled transaction."""

        db.session.rollback()

    def test_create_song(self):
        s = Song(title='Test Song', artist='Testerson',
                 track_id="testid1235432")

        db.session.add(s)
        db.session.commit()

        self.assertEqual(s.title, 'Test Song')
        self.assertEqual(s.artist, 'Testerson')
        self.assertEqual(s.track_id, 'testid1235432')


class PlaylistModelTestCase(TestCase):
    """Tests for model for Playlist class."""

    def setUp(self):
        """Clean up any existing users."""
        PlaylistSong.query.delete()
        Song.query.delete()
        Playlist.query.delete()
        User.query.delete()

    def tearDown(self):
        """Clean up any fouled transaction."""

        db.session.rollback()

    def test_create_playlist(self):
        u = User.register(username="test1", password="test1",
                          email="test@test.com")
        db.session.add(u)
        db.session.commit()

        p = Playlist(name='Test Playlist', description="Testing",
                     username=u.username)

        db.session.add(p)
        db.session.commit()

        self.assertEqual(p.name, 'Test Playlist')
        self.assertEqual(p.description, 'Testing')
        self.assertEqual(p.username, 'test1')

class PlaylistSongModelTestCase(TestCase):
    """Tests for model for PlaylistSong class."""

    def setUp(self):
        """Clean up any existing users."""
        PlaylistSong.query.delete()
        Playlist.query.delete()
        Song.query.delete()
        User.query.delete()

    def tearDown(self):
        """Clean up any fouled transaction."""

        db.session.rollback()

    def test_playlist_song(self):
        u = User(username="test1", password="test1",
                          email="test@test.com")
        db.session.add(u)
        db.session.commit()

        s = Song(title='Test Song', artist='Testerson',
                 track_id="testid1235432")
        
        db.session.add(s)
        db.session.commit()


        p = Playlist(name='Test Playlist', description="Testing",
                     username=u.username)

        db.session.add(p)
        db.session.commit()
        
        ps = PlaylistSong(song_id=s.id,playlist_id=p.id)

        db.session.add(ps)
        db.session.commit()

        self.assertEqual(ps.song_id, s.id)
        self.assertEqual(ps.playlist_id, p.id)