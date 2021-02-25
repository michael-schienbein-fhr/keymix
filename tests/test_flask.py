from unittest import TestCase
from keymix import app, db
from keymix.models import Song, Playlist, PlaylistSong, User

# Use test database and don't clutter tests with SQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///keymix_test'
app.config['SQLALCHEMY_ECHO'] = False

# Make Flask errors be real errors, rather than HTML pages with error info
app.config['TESTING'] = True
app.config['WTF_CSRF_ENABLED'] = False
# This is a bit of hack, but don't use Flask DebugToolbar
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

db.drop_all()
db.create_all()


class MainTestCase(TestCase):
    """Tests for routes."""

    def setUp(self):
        """Add sample users."""

        User.query.delete()

        u1 = User.register(username="test1", password="test1",
                           email="test@test.com")
        u2 = User(username="admin", password="admin",
                  email="admin@admin.com", is_admin=True)
        db.session.add_all([u1, u2])
        db.session.commit()

        self.user_id = u1.id
        self.username = u1.username

    def tearDown(self):
        """Clean up any fouled transaction."""

        db.session.rollback()

    def test_home_page(self):
        with app.test_client() as client:
            resp = client.get("/")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<p>What is this Keymix?</p>', html)

    def test_404_page(self):
        with app.test_client() as client:
            resp = client.get("/notalink")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 404)
            self.assertIn(
                "<p>404: Looks like we", html)

    def test_login_render(self):
        with app.test_client() as client:
            resp = client.get("/login")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(
                '<label class="label is-small" for="username">Username</label>', html)
            self.assertIn(
                '<label class="label is-small" for="password">Password</label>', html)

    def test_login(self):
        with app.test_client() as client:
            d = {"username": "test1", "password": "test1"}
            resp = client.post("/login", data=d, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<p>What is this Keymix?</p>', html)
            self.assertIn(
                '<a class="navbar-item is-pulled-left has-text-success">Welcome back, test1!</a>', html)

    def test_logout(self):
        """Tests when user clicks the Logout link"""
        with app.test_client() as client:
            with client.session_transaction() as session:
                session['token'] = 'token'
                session['refresh_token'] = 'refresh_token'
                session['user_id'] = 'user_id'
            user_id = 'user_id'
            self.assertEqual(user_id, session.get('user_id'))
            self.assertEqual(session['user_id'], 'user_id')
            session.clear()
            self.assertNotEqual(user_id, session.get('user_id'))

    def test_register_render(self):
        with app.test_client() as client:
            resp = client.get("/register")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(
                '<label class="label is-small" for="username">Username</label>', html)
            self.assertIn(
                '<label class="label is-small" for="password">Password</label>', html)

    def test_register(self):
        with app.test_client() as client:
            d = {"username": "test2", "password": "test2", "email": "testing@gmail.com",
                 "first_name": "testy", "last_name": "testman"}
            resp = client.post("/register", data=d, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<p>What is this Keymix?</p>', html)
            self.assertIn(
                '<a class="navbar-item is-pulled-left has-text-success">Welcome! Account created successfully!</a>', html)

    def test_seed_parameters(self):
        """Tests seeding based on several seeds including artist, track, genre, and more."""
        with app.test_client() as client:
            client.get('/auth')
            resp = client.post(
                '/seed',
                data={
                    'artist': '1D3hV1Gke8LLRSn1aymglN',
                    'seed_genre': 'house',
                    'tempo': 128,
                    'danceability': 0.9,
                    'energy': 0.9,
                    'speechiness': 0.9,
                    'acousticness': 0.9,
                    'instrumentalness': 0.9,
                    'liveness': 0.9,
                    'valence': 0.9,
                    'popularity': 1,
                    'loudness': 0.9,
                },
                follow_redirects=True
            )
            html = resp.get_data(as_text=True)
            self.assertIn(
                'https://open.spotify.com/embed/track', html)
