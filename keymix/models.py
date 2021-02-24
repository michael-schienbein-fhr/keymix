from keymix import db
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt()


class Song(db.Model):
    """Song model"""

    __tablename__ = "songs"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String, nullable=False)
    artist = db.Column(db.String, nullable=False)
    track_id = db.Column(db.String, nullable=False, unique=True)


class Playlist(db.Model):
    """Playlist Model"""

    __tablename__ = "playlists"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    songs = db.relationship(
        "Song", secondary="playlist_songs", backref="playlist")
    username = db.Column(db.String(20), db.ForeignKey(
        'users.username'), nullable=False)


class PlaylistSong(db.Model):
    """Mapping of a playlist to a song."""

    __tablename__ = "playlist_songs"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    song_id = db.Column(db.Integer, db.ForeignKey('songs.id'), nullable=False)
    playlist_id = db.Column(db.Integer, db.ForeignKey(
        'playlists.id'), nullable=False)


# class Detail(db.Model):
#     """Audio details model"""

#     __tablename__ = "details"

#     song_id = db.Column(db.Integer, db.ForeignKey(
#         'songs.id'), primary_key=True, nullable=False)
#     key = db.Column(db.Integer)
#     mode = db.Column(db.Integer)
#     tempo = db.Column(db.Float)
#     danceability = db.Column(db.Float)
#     energy = db.Column(db.Float)
#     loudness = db.Column(db.Float)
#     speechiness = db.Column(db.Float)
#     acousticness = db.Column(db.Float)
#     instrumentalness = db.Column(db.Float)
#     liveness = db.Column(db.Float)
#     valence = db.Column(db.Float)
#     duration_ms = db.Column(db.Integer)
#     time_signature = db.Column(db.Float)


class User(db.Model):
    """User Model"""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    playlists = db.relationship(
        "Playlist", backref="user", cascade="all,delete")

    @classmethod
    def register(cls, username, password, email):
        """Register User with hashed password and return user object"""

        hashed = bcrypt.generate_password_hash(password)

        hashed_utf8 = hashed.decode("utf8")

        return cls(username=username, password=hashed_utf8, email=email)

    @classmethod
    def authenticate(cls, username, password):
        """Validate user exists in db and password is correct"""

        u = User.query.filter_by(username=username).first()

        if u and bcrypt.check_password_hash(u.password, password):
            return u
        else:
            return False
