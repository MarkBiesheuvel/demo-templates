import requests
import boto3
from os import environ
from base64 import b64encode

# Create a function that takes a string as input and output, no bytestring
base64_encode_string = lambda string: b64encode(string.encode()).decode()

client_id = environ.get('SPOTIFY_CLIENT_ID')
client_secret = environ.get('SPOTIFY_CLIENT_SECRET')

playlists = [
    '37i9dQZF1DX6J5NfMJS675', # Techno Bunker
    '37i9dQZF1DX5xiztvBdlUf', # Truly Deeply House
    '37i9dQZF1DX0r3x8OtiwEM', # Lowkey Tech
    '37i9dQZF1DX87JE1B72J6C', # This Is deadmau5
    '37i9dQZF1DX1nSIVoqxfC0', # This Is Tiësto
    '37i9dQZF1DZ06evO2wAAFP', # This Is Joris Voorn
    '37i9dQZF1DWYacvJEtDkU8', # This Is Eric Prydz
    '37i9dQZF1DZ06evO1meuUV', # This Is Stephan Bodzin
]

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Music')

def get_authorization():
    authorization = base64_encode_string('{}:{}'.format(client_id, client_secret))

    response = requests.post(
        'https://accounts.spotify.com/api/token',
        headers={
            'authorization': 'Basic {}'.format(authorization)
        },
        data={
            'grant_type': 'client_credentials'
        },
    )

    if response.status_code != 200:
        raise Exception('Unable to authenticate')

    body = response.json()

    return '{} {}'.format(body['token_type'], body['access_token'])

def get_playlist(authorization, playlist_id):
    # TODO: pagination
    response = requests.get(
        'https://api.spotify.com/v1/playlists/{}/tracks'.format(playlist_id),
        headers={
            'authorization': authorization
        },
    )
    body = response.json()

    for item in body['items']:
        track = item['track']
        album = track['album']
        for artist in track['artists']:
            yield {
                'Artist': artist['name'],
                'Song': track['name'],
                'Album': album['name'],
                'Date': album['release_date'],
                'Year': album['release_date'][:4],
                'Popularity': track['popularity'],
                'Preview': track['preview_url'],
                'Duration': track['duration_ms'],
            }

def insert_records(records):
    i = 0
    with table.batch_writer() as batch:
        for record in records:
            batch.put_item(Item=record)
            i += 1
    return i

if __name__ == '__main__':
    authorization = get_authorization()
    for playlist in playlists:
        records = get_playlist(authorization, playlist)
        total = insert_records(records)
        print('Inserted {} records'.format(total))
