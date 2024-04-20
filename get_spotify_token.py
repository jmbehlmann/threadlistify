import requests, os
from urllib.parse import urlencode
from dotenv import load_dotenv
import base64
import webbrowser

load_dotenv()

client_id = os.environ.get('SPOTIFY_CLIENT_ID')
client_secret = os.environ.get('SPOTIFY_CLIENT_SECRET')

# auth_headers = {
#     "client_id": client_id,
#     "response_type": "code",
#     "redirect_uri": "http://localhost:8080/callback",
#     "scope": "user-library-read playlist-modify-private playlist-modify-public"
# }

# webbrowser.open("https://accounts.spotify.com/authorize?" + urlencode(auth_headers))

# code will be in url of redirect window

code = "AQA1QXa_t7cvUv5fMtVqsRG0O8R4KFSUOwAYbhg1HAqniLZJHZyyNbUrKJoJozFGWzJPBFvctpRHoPOejo0UcRZSPPUcEodWwaEVnn05-h2WmPoe1I95kAG0IKkwX-Dhi9i9VIMNSpGKAbII5VDtHlwtVreZjUM1_OYoUvoq21lG7406IMikpk1LFpCWRitYb9Ywkpy592wq-XNfLN2lYTJSUfqpeP-jVf3XbzLJ9LqcBKJ40uHz-Ufo8-3MIqA9a8fubngq"


encoded_credentials = base64.b64encode(client_id.encode() + b':' + client_secret.encode()).decode("utf-8")

token_headers = {
    "Authorization": "Basic " + encoded_credentials,
    "Content-Type": "application/x-www-form-urlencoded"
}

token_data = {
    "grant_type": "authorization_code",
    "code": code,
    "redirect_uri": "http://localhost:8080/callback"
}

r = requests.post("https://accounts.spotify.com/api/token", data=token_data, headers=token_headers)

token = r.json()["access_token"]

print(token)