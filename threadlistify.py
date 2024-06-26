import praw, os, requests, json, base64
from dotenv import load_dotenv
from praw.models import MoreComments
from urllib.parse import urlparse, parse_qs
import webbrowser


def get_spotify_auth_code(url):
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    auth_code = query_params.get('code', [None])[0]
    return auth_code

# propt user to input spotify code

def get_spotify_code():
    client_id = os.environ.get('SPOTIFY_CLIENT_ID')
    redirect_uri = "http://localhost:8080/callback"

    auth_url = f"https://accounts.spotify.com/authorize?client_id={client_id}&response_type=code&redirect_uri={redirect_uri}&scope=user-library-read%20playlist-modify-private%20playlist-modify-public"

    webbrowser.open(auth_url)

    try:
        while True:
            url = input("Enter the URL you were redirected to after authorizing: ")
            auth_code = get_spotify_auth_code(url)
            if auth_code:
                print("Authorization code:", auth_code)
                return auth_code
            else:
                print("No authorization code found in the URL.")
    except KeyboardInterrupt:
        print("\nExiting...")
        exit()


# get top level reddit comments

def get_reddit_comments(thread_url):
    print("getting reddit comments")
    load_dotenv()
    reddit = praw.Reddit(
        client_id=os.environ.get('CLIENT_ID'),
        client_secret=os.environ.get('CLIENT_SECRET'),
        password=os.environ.get('PASSWORD'),
        user_agent=os.environ.get('USER_AGENT'),
        username=os.environ.get('USERNAME'),
    )
    submission = reddit.submission(url=thread_url)
    title = submission.title
    print(title)
    comments = ""

    for top_level_comment in submission.comments:
        if isinstance(top_level_comment, MoreComments):
            continue
        comments += top_level_comment.body.replace('\n', '') + " "

    print("got reddit comments")
    return comments, title


# send comments to openai to return artists and albums

def send_to_openai(comments):
    print("sending to openai")

    url = "https://api.openai.com/v1/chat/completions"
    openai_key = os.environ.get('OPENAI_KEY')

    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer {}'.format(openai_key)
    }

    prompt = f"The following is a comment thread from reddit. Please find all of the albums referenced in the text and put them into a python list with both the artist and the album title combined into a single element in the list. There may be additional text in the comments which needs to be removed. Sometimes the comment will reference only an album. Remove any duplicates so that each album only appears in the list once. It is importatnt to remove all punctuation including parenthesis, brackets, quotes, etc. so that each line is formatted as 'artist album'  {comments}"

    data = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": f"{prompt}"}],
        "temperature": 0
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        response_json = response.json()
        content = response_json['choices'][0]['message']['content']
        # certain characters in the response may cause issues with using eval
        albums = eval(content)
    else:
        print('Error:', response.text)

    print("received data from openai")
    return albums

def get_token(code):

    client_id = os.environ.get('SPOTIFY_CLIENT_ID')
    client_secret = os.environ.get('SPOTIFY_CLIENT_SECRET')

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

    access_token = r.json()["access_token"]

    return access_token


# get album ids

def get_album_ids(albums, access_token):
    print("getting album ids")
    url = 'https://api.spotify.com/v1/search'
    album_ids = []
    for album in albums:
        query = album
        params = {
            'q': query,
            'type': 'album',
            'limit': 1  # limit the number of results to 1 (optional)
        }

        response = requests.get(url, params=params, headers={'Authorization': f'Bearer {access_token}'})

        if response.status_code == 200:
            album_details = response.json()['albums']['items'][0]
            album_id = album_details['id']
            print(f"the album id for {album} is {album_id}")
            album_ids.append(album_id)
        else:
            print("Failed to search for album:", response.text)
    return album_ids



def create_playlist(access_token, thread_url, title):
    url = "https://api.spotify.com/v1/me"
    response = requests.get(url, headers={'Authorization': f'Bearer {access_token}'})

    user_data = response.json()
    user_id = user_data['id']
    url = f"https://api.spotify.com/v1/users/{user_id}/playlists"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    data = {
        "name": f"{title}",
        "description": f"Made using Threadlistify - https://github.com/jmbehlmann/threadlistify From reddit thread {thread_url}",
        "public": False
    }

    response = requests.post(url, headers=headers, json=data)

    playlist_data = response.json()
    playlist_id = playlist_data['id']

    print(f"created playlist: {title}")
    return playlist_id


# get track ids for each album
def add_to_playlist(album_ids, playlist_id, access_token):
    print("getting track ids")
    for album_id in album_ids:
        track_ids = []
        url = f"https://api.spotify.com/v1/albums/{album_id}/tracks"
        headers = {
            "Authorization": f"Bearer {access_token}"
        }

        response = requests.get(url, headers=headers)
        tracks = response.json()
        # loop through the items in the response json and extract the track ids
        for item in tracks['items']:
            track_ids.append(item['id'])

        formatted_track_ids = []
        for track_id in track_ids:
            formatted_track_ids.append(f'spotify:track:{track_id}')

        url = f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks'

        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }

        data = {
            'uris': formatted_track_ids
        }

        response = requests.post(url, headers=headers, json=data)

        print("added an album")

def main():
    load_dotenv()
    thread_url = os.environ.get('REDDIT_THREAD_URL')

    code = get_spotify_code()
    comments, title = get_reddit_comments(thread_url)
    albums =  send_to_openai(comments)
    access_token = get_token(code)
    album_ids = get_album_ids(albums, access_token)
    playlist_id = create_playlist(access_token, thread_url, title)
    add_to_playlist(album_ids, playlist_id, access_token)
    print("done")

if __name__ == "__main__":
    main()
