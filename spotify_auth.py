import requests, os
from urllib.parse import urlencode
from dotenv import load_dotenv
import base64
import webbrowser

load_dotenv()

client_id = os.environ.get('SPOTIFY_CLIENT_ID')
client_secret = os.environ.get('SPOTIFY_CLIENT_SECRET')

auth_headers = {
    "client_id": client_id,
    "response_type": "code",
    "redirect_uri": "http://localhost:8080/callback",
    "scope": "user-library-read playlist-modify-private playlist-modify-public"
}

# webbrowser.open("https://accounts.spotify.com/authorize?" + urlencode(auth_headers))

# code will be in url of redirect window

code = "AQAd5DIODq4d75Uep0p3Lkz5mNCdanbfuAyp7bxtkfhbTX9Qx8foZ_rZL4tBGz5fcAuOKXDFiPvYbNWV2whEh0X9sEHrWHKPLn5zlOdNjkX85AX_zMCMSaBq1KlYDH5VCGH2WNpqG0bIKK9Nyf2q5pSTxkMApJ83RJiuTNLva1jExlyPnljkhNXfQtIkdPDDWNrRozmMTUHBMnbDQW11FbvFNRnHPoD89-rLdyJeNuJawoYOvZZ1GJRDy1iJ2LuK6Mc6uNxZ"


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