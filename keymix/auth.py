import base64

client_id = 'a598514bd4fa4304b7ca63c5046fca6a'
client_secret = 'ce25bcaa33434f6cae6e39d44ef48446'
# production:
redirect_uri_encoded = 'https%3A%2F%2Fkeymix.herokuapp.com%2Fuser_auth'
redirect_uri = "https://keymix.herokuapp.com/user_auth"
# testing:
# redirect_uri_encoded = 'http%3A%2F%2F127.0.0.1%3A5000%2Fuser_auth'
# redirect_uri = "http://127.0.0.1:5000/user_auth"

secret_key = "4$2#%%3se@#$cret"
encodedData = base64.b64encode(
    bytes(f"{client_id}:{client_secret}", "ISO-8859-1")).decode("ascii")
