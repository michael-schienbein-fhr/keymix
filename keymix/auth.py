"""Encode client ID and Secret key for use with base level authorization"""
import base64
client_id = "a598514bd4fa4304b7ca63c5046fca6a"
client_secret = "ce25bcaa33434f6cae6e39d44ef48446"
redirect_uri = 'http://localhost:5000/user_auth'
redirect_uri_encoded = 'http%3A%2F%2Flocalhost%3A5000%2Fuser_auth'
encodedData = base64.b64encode(
    bytes(f"{client_id}:{client_secret}", "ISO-8859-1")).decode("ascii")
secret_key = "it1s@$3cret!$#!"
