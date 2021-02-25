import os
import requests
from flask import request, render_template, redirect, flash, session, url_for, g, jsonify

from keymix import app, db
from keymix.forms import UserForm, LoginForm, SearchForm, SubSearchForm, SavePlaylistForm
from keymix.models import Song, Playlist, PlaylistSong, User
from keymix.auth import encodedData, client_id, client_secret, redirect_uri_encoded, redirect_uri
from keymix.util import get_user_id, get_genres, get_keys, get_modes, get_id, add_songs_to_playlist, create_playlist
from werkzeug.exceptions import Unauthorized
from sqlalchemy.exc import IntegrityError, DataError


### Create flask global variables ###
CURR_USER_KEY = "curr_user"


@app.context_processor
def inject_auth_info():
    redirect = redirect_uri_encoded
    clientID = client_id
    return dict(client_id=clientID, redirect_uri=redirect)


### User signup/login/logout ###
@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]
    session.pop('token', None)
    session.pop('refresh_token', None)
    session.pop('user_id', None)


@app.route('/register', methods=["GET", "POST"])
def register_user():

    if g.user:
        flash("You are already registered", "danger")
        return redirect("/")

    form = UserForm()

    if form.validate_on_submit():
        try:
            user = User.register(username=form.username.data,
                                 password=form.password.data,
                                 email=form.email.data)

            db.session.add(user)
            db.session.commit()

        except IntegrityError:
            form.username.errors.append("Username/Email is already taken")
            return render_template('register.html', form=form)

        do_login(user)

        flash('Welcome! Account created successfully!', 'success')
        return redirect('/')
    else:
        return render_template('register.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login_user():
    if g.user:
        flash("You are already logged in", "danger")
        return redirect("/")

    form = LoginForm()

    if form.validate_on_submit():

        user = User.authenticate(form.username.data, form.password.data)

        if user:
            do_login(user)
            flash(f"Welcome back, {user.username}!", "success")
            if user.is_admin:
                session["is_admin"] = True
            else:
                session["is_admin"] = False
            return redirect('/')
        else:
            form.username.errors = ['Invalid username/password']

    return render_template('login.html', form=form)


@app.route("/logout")
def logout_user():
    """Clears all stored session data"""

    do_logout()

    flash('Successfully logged out', 'success')
    return redirect('/')


### checks for 'is_admin' in session ###
def authorize(username):
    if "is_admin" not in session or session["is_admin"] == False:
        if "username" not in session or username != session['username']:
            flash("Please login first", "danger")
            raise Unauthorized()


### Default auth routes and user auth routes for API use ###
@app.route("/auth")
def get_spotify_auth():
    """Authenticates app with Spotify's API."""

    session.pop('token', None)
    session.pop('refresh_token', None)
    session.pop('user_id', None)
    data = {
        'grant_type': 'client_credentials'
    }

    headers = {
        "Authorization": "Basic {}".format(encodedData)
    }

    resp = requests.post('https://accounts.spotify.com/api/token',
                         headers=headers, data=data).json()
    token = resp['access_token']
    session['token'] = token
    return redirect('/search')


@app.route("/user_auth", methods=["GET"])
def get_spotify_user_auth():
    """Allows user to login to Spotify and this app"""
    try:
        session.pop('token', None)
        session.pop('refresh_token', None)
        session.pop('user_id', None)
        code = request.args.get('code')
        resp = requests.post('https://accounts.spotify.com/api/token',
                             data={
                                 "grant_type": "authorization_code",
                                 "code": code,
                                 "redirect_uri": redirect_uri,
                                 "client_id": client_id,
                                 "client_secret": client_secret
                             }).json()
        token = resp['access_token']
        refresh_token = resp['refresh_token']
        session['token'] = token
        session['refresh_token'] = refresh_token
        session['user_id'] = get_user_id(session['token'])
        flash(f"Welcome, {session['user_id']}!", "success")
        return redirect('/search')

    except KeyError:
        return redirect('/')


### main app routes ###


@app.route('/')
def home_page():
    """Renders home page"""

    return render_template('index.html')


@app.route("/playlists")
def render_playlists():
    """Sets up search page and redirect user there."""
    if not g.user:
        flash("Please log in to start using KEYmix", "danger")
        return redirect("/")

    playlists = Playlist.query.filter_by(username=g.user.username).all()

    return render_template("playlists.html", playlists=playlists)


@app.route("/playlists/<playlist_id>/tracks")
def render_playlist_tracks(playlist_id):
    if len(playlist_id) < 10:
        if g.user:
            playlists = Playlist.query.filter_by(
                username=g.user.username).all()
            pl_ids = []
            for pl in playlists:
                pl_ids += str(pl.id)
        if not g.user:
            flash("Please log in to start using KEYmix", "danger")
            return redirect("/")
        if playlist_id not in pl_ids:
            raise Unauthorized()
        playlist_track_ids = []
        playlist_track_uris = []
        pl = Playlist.query.get(playlist_id)
        for song in pl.songs:
            playlist_track_ids.append(song.track_id)
        for track_id in playlist_track_ids:
            playlist_track_uris.append(f'spotify:track:{track_id}')
        session['track_uris'] = playlist_track_uris
        print(session['track_uris'])
        return render_template("tracks.html", playlist_track_ids=playlist_track_ids, name=pl.name, description=pl.description, id=playlist_id)
    else:
        playlist_track_ids = []
        try:
            headers = {'Authorization': 'Bearer ' + session['token']}

            resp = requests.get(
                f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks', headers=headers).json()

            # create dict from playlist response json
            song_dict = [[{"title": x['track']['name']}, {"artist": x['track']['artists'][0]['name']}, {
                "track_id": x['track']['id']}] for x in resp['items']]
            session['song_dict'] = song_dict

            for x in resp['items']:
                playlist_track_ids.append(x['track']['id'])
            print(playlist_track_ids)
            return render_template("tracks.html", playlist_track_ids=playlist_track_ids, id=playlist_id)

        except KeyError:
            return redirect('/')


@ app.route("/search", methods=["GET"])
def render_search_page():
    """Sets up search page and redirect user there."""
    if not g.user:
        flash("Please log in to start using KEYmix", "danger")
        return redirect("/")
    try:
        subform = SubSearchForm()
        form = SearchForm()
        form.genre.choices = get_genres(session['token'])
        form.key.choices = get_keys()
        form.mode.choices = get_modes()
        return render_template("search.html", form=form, subform=subform)
    except KeyError:
        return redirect('/')


@ app.route("/subsearch", methods=["GET"])
def artist_or_track_search():
    try:
        artist = request.args.get('q')
        type = request.args.get('type').lower()

        resp = get_id(artist, type, session['token'])

        return jsonify(resp)

    except KeyError:
        return redirect('/')


@ app.route("/seed", methods=["POST"])
def show_recommendations():
    """Processes search data against Spotify's API and gets the user to this results page."""

    try:

        headers = {'Authorization': 'Bearer ' + session['token']}
        payload = {}

        #
        if request.form.get('artist'):
            artist_list = ""
            for artist in request.form.getlist('artist'):
                artist_list += f"{artist},"
            payload['seed_artists'] = artist_list

        #
        if request.form.get('track'):
            track_list = ""
            for track in request.form.getlist('track'):
                track_list += f"{track},"
            payload['seed_tracks'] = track_list
        #
        if request.form.get('genre'):
            payload['seed_genres'] = request.form.get('genre')

        #
        if request.form.get('mode'):
            payload['target_mode'] = int(request.form.get('mode'))
        if request.form.get('key'):
            payload['target_key'] = int(request.form.get('key'))
        if request.form.get('tempo'):
            payload['target_tempo'] = int(request.form.get('tempo'))

        #

        payload['target_danceability'] = float(
            request.form.get('danceability'))
        payload['target_energy'] = float(request.form.get('energy'))
        payload['target_speechiness'] = float(
            request.form.get('speechiness'))
        payload['target_acousticness'] = float(
            request.form.get('acousticness'))
        payload['target_instrumentalness'] = float(
            request.form.get('instrumentalness'))
        payload['target_liveness'] = float(request.form.get('liveness'))
        payload['target_valence'] = float(request.form.get('valence'))
        payload['target_popularity'] = int(
            request.form.get('popularity'))
        payload['target_loudness'] = float(request.form.get('loudness'))

        resp = requests.get('https://api.spotify.com/v1/recommendations',
                            params=payload, headers=headers).json()
        # create dict from recommendation json
        song_dict = [[{"title": x['name']}, {"artist": x['artists'][0]['name']}, {
            "track_id": x['id']}] for x in resp["tracks"]]
        session['song_dict'] = song_dict

        #
        track_uris = ""
        for track_uri in resp['tracks']:
            track_uris += track_uri['uri']+','
        session['track_uris'] = track_uris

        #
        track_id_list = []
        for track in resp['tracks']:
            track_id_list.append(track['id'])
        session['track_id_list'] = track_id_list

        return render_template("results.html", track_id_list=track_id_list)
    except KeyError:
        form = SearchForm()
        subform = SubSearchForm()
        form.genre.choices = get_genres(session['token'])
        form.key.choices = get_keys()
        form.mode.choices = get_modes()
        return render_template("search.html", form=form, subform=subform)


@ app.route('/save', methods=["GET", "POST"])
def save_playlist_results():
    if not g.user:
        flash("Please login first", "danger")
        return redirect("/")

    form = SavePlaylistForm()
    song_dict = session["song_dict"]

    if form.validate_on_submit():
        playlist_name = form.name.data
        playlist_description = form.description.data or None
        playlist_username = g.user.username

        # add song results to db
        for song in song_dict:
            s = Song.query.filter_by(track_id=song[2]['track_id']).first()
            if s is None:
                new_song = Song(
                    title=song[0]['title'], artist=song[1]['artist'], track_id=song[2]['track_id'])

                db.session.add(new_song)
                db.session.commit()

        # create new playlist entry
        new_playlist = Playlist(name=playlist_name,
                                description=playlist_description, username=playlist_username)
        db.session.add(new_playlist)
        db.session.commit()

        # add songs to playlist
        for song in song_dict:
            s = Song.query.filter_by(track_id=song[2]['track_id']).first()
            ps = PlaylistSong(song_id=s.id, playlist_id=new_playlist.id)
            db.session.add(ps)
            db.session.commit()

        flash("Playlist saved succuessfully!", 'success')
        return redirect(f'/playlists/{new_playlist.id}/tracks')

    return render_template('save.html', form=form)


@ app.route('/save/spotify', methods=["GET"])
def save_playlist_spotify():
    if not g.user:
        flash("Please login first", "danger")
        return redirect("/")

    user_id = get_user_id(session['token'])
    track_uris = session['track_uris']
    print(track_uris)
    playlist_id = create_playlist(user_id, session['token'])
    add_songs_to_playlist(playlist_id, track_uris, session['token'])
    flash("Spotify playlist saved succuessfully!", 'success')
    return redirect(f'/playlists/{playlist_id}/tracks')


## Error routes ##


@ app.errorhandler(404)
def page_not_found(e):
    """Show 404 NOT FOUND page."""
    error = '404'
    text = "Looks like we can't find the page you are looking for."

    return render_template('error.html', error=error, text=text), 404


@ app.errorhandler(401)
def page_unauthorized(e):
    """Show 401 Unauthorized page."""
    error = '401'
    text = "You are Unauthorized to view that page."
    return render_template('error.html', error=error, text=text), 401
