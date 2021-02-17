from flask_wtf import FlaskForm
from wtforms.validators import InputRequired, Optional, URL, NumberRange, Length, Email
from wtforms.widgets.html5 import RangeInput
from wtforms.fields.html5 import DecimalRangeField, IntegerRangeField
from wtforms import FloatField, BooleanField, IntegerField, RadioField, SelectField, TextAreaField, StringField, PasswordField


class MyInputRequired(InputRequired):
    field_flags = ()


class UserForm(FlaskForm):
    """Form for adding users"""

    username = StringField("Username", validators=[
        MyInputRequired(message="Username cannot be blank")])
    password = PasswordField("Password", validators=[
        MyInputRequired(message="Password cannot be blank")])
    email = StringField("Email", validators=[Email(),
                                             MyInputRequired(message="Email cannot be blank")])


class LoginForm(FlaskForm):
    """Form for loggining in"""

    username = StringField("Username", validators=[
        MyInputRequired(message="Username cannot be blank")])
    password = PasswordField("Password", validators=[
        MyInputRequired(message="Password cannot be blank")])


class SearchForm(FlaskForm):
    """Form for using recommendation search"""

    genre = SelectField("Genre", choices=[])
    key = SelectField("Key", choices=[])
    mode = SelectField("Mode", choices=[])
    tempo = IntegerRangeField("Tempo")
    danceability = DecimalRangeField("Danceability")
    energy = DecimalRangeField("Energy")
    speechiness = DecimalRangeField("Speechiness")
    acousticness = DecimalRangeField("Acousticness")
    instrumentalness = DecimalRangeField("Instrumentalness")
    liveness = DecimalRangeField("Liveness")
    valence = DecimalRangeField("Valence")
    popularity = IntegerRangeField("Popularity")
    loudness = DecimalRangeField("Loudness")
    duration_ms = IntegerRangeField("Duration")


class SubSearchForm(FlaskForm):
    """Form for using recommendation search"""

    subsearch_input = StringField("Track or Artist Subsearch", validators=[
        MyInputRequired(message="Playlist Name cannot be blank")])
    subsearch_radio = RadioField(
        "Track or Artist", choices=["Track", "Artist"])


class SavePlaylistForm(FlaskForm):
    """Form for edit/saving recommendations playlist to db"""

    name = StringField("Playlist Name", validators=[
        MyInputRequired(message="Playlist Name cannot be blank")])
    description = TextAreaField("Description")
