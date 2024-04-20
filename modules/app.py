import praw, os, requests, json
from dotenv import load_dotenv
from praw.models import MoreComments

load_dotenv()

client_id = os.environ.get('CLIENT_ID')
client_secret = os.environ.get('CLIENT_SECRET')
password = os.environ.get('PASSWORD')
user_agent = os.environ.get('USER_AGENT')
username = os.environ.get('USERNAME')


reddit = praw.Reddit(
    client_id=client_id,
    client_secret=client_secret,
    password=password,
    user_agent=user_agent,
    username=username,
)

url = ""
submission = reddit.submission(url=url)

# top level comments only

comments = ""

for top_level_comment in submission.comments:
    if isinstance(top_level_comment, MoreComments):
        continue
    comments += top_level_comment.body.replace('\n', '') + " "

# all comments

# submission.comments.replace_more(limit=None)
# for comment in submission.comments.list():
#     print(comment.body)

url = "https://api.openai.com/v1/chat/completions"
openai_key = os.environ.get('OPENAI_KEY')

headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer {}'.format(openai_key)
}

prompt = f"The following is a comment thread from reddit. Please find all of the albums referenced in the text and put them into a python list with both the artist and the album title combined into a single element in the list. Remove any duplicates so that each album only appears in the list once. You may need to remove any punctuation or any extra info so that each line is formatted as 'artist album'  {comments}"

data = {
     "model": "gpt-3.5-turbo",
     "messages": [{"role": "user", "content": f"{prompt}"}],
     "temperature": 0
   }

response = requests.post(url, headers=headers, json=data)

if response.status_code == 200:
    # Parse the JSON response
    response_json = response.json()

    # Extract the content from the response
    content = response_json['choices'][0]['message']['content']

    # maybe change this to json.loads
    albums = eval(content)
    # print(albums[0])
    # Print or return the content
else:
    # Print an error message if the request failed
    print('Error:', response.text)


# get spotify access token

url = "https://accounts.spotify.com/api/token"
headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
}

data = {
    'grant_type': 'client_credentials',
    'client_id': os.environ.get('SPOTIFY_CLIENT_ID'),
    'client_secret': os.environ.get('SPOTIFY_CLIENT_SECRET')
}


response = requests.post(url, data=data)

if response.status_code == 200:
    # Extract the access token from the response JSON
    access_token = response.json()['access_token']
    # print("Access token:", access_token)
else:
    # Print an error message if the request failed
    print("Failed to get access token:", response.text)


# get album id

# Define the base URL for the Spotify API
url = 'https://api.spotify.com/v1/search'



# Define the search query
album = albums[19]
query = f'{album}'

# Define the parameters for the GET request
params = {
    'q': query,
    'type': 'album',
    'limit': 1  # Limit the number of results to 1 (optional)
}

# Make the GET request with the access token
response = requests.get(url, params=params, headers={'Authorization': f'Bearer {access_token}'})

# Check if the request was successful (status code 200)
if response.status_code == 200:
    # Extract the album details from the response JSON
    album_details = response.json()['albums']['items'][0]
    album_id = album_details['id']
    print(f"album id for {album} is {album_id}")
else:
    # Print an error message if the request failed
    print("Failed to search for album:", response.text)

url = "https://api.spotify.com/v1/me"
headers = {
    "Authorization": f'Bearer {access_token}'
}

response = requests.get(url, headers=headers)

print(response.json())

# create empty playlist
# for each album
#     get album id
#     get all track ids for album
#     add all tracks to playlist

