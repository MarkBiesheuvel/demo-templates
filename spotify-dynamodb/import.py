import requests
import boto3
from os import environ
from base64 import b64encode


client_id = environ.get('SPOTIFY_CLIENT_ID')
client_secret = environ.get('SPOTIFY_CLIENT_SECRET')

playlists = [
    '37i9dQZF1DX6J5NfMJS675',  # Techno Bunker
    '37i9dQZF1DX5xiztvBdlUf',  # Truly Deeply House
    '37i9dQZF1DX0r3x8OtiwEM',  # Lowkey Tech
    '3fO6aR6zI3NiVUbt0Av20h',  # Strobe - deadmau5
    '37i9dQZF1DX87JE1B72J6C',  # This Is deadmau5
    '37i9dQZF1DWZAkrucRF6Gq',  # This is Daft Punk
    '37i9dQZF1DX1nSIVoqxfC0',  # This Is Tiësto
    '37i9dQZF1DZ06evO2wAAFP',  # This Is Joris Voorn
    '37i9dQZF1DWYacvJEtDkU8',  # This Is Eric Prydz
    '37i9dQZF1DZ06evO1meuUV',  # This Is Stephan Bodzin
    '37i9dQZF1DZ06evO1vHx6D',  # This Is Kölsch
    '37i9dQZF1DZ06evO3tjkZi',  # This Is Netksy
    '37i9dQZF1DZ06evO2h7ny3',  # This Is Maceo Plex
    '37i9dQZF1DZ06evO1cvtuL',  # This Is Lane 8
    '37i9dQZF1DX0yuTyG4DkZ3',  # This Is Sam Feldt
    '37i9dQZF1DX3sNH1cCGwYU',  # This Is Armin van Buuren
    '37i9dQZF1DX2TRYkJECvfC',  # Deep House Relax
    '37i9dQZF1DWSf2RDTDayIx',  # Happy Beats
    '37i9dQZF1DXaXB8fQg7xif',  # Dance Party
    '37i9dQZF1DX32NsLKyzScr',  # Power Hour
    '37i9dQZF1DWTwCImwcYjDL',  # 360 Dance
    '37i9dQZF1DXa8NOEUWPn9W',  # Housewerk
    '37i9dQZF1DX0AMssoUKCz7',  # Tropical House
    '37i9dQZF1DX8a1tdzq5tbM',  # Dance Classics
    '37i9dQZF1DX8tZsk68tuDw',  # Dance Rising
    '37i9dQZF1DX91oIci4su1D',  # Trance Mission
    '37i9dQZF1DXbXD9pMSZomS',  # Lo-Fi House
    '37i9dQZF1DX6GJXiuZRisr',  # Night Rider
    '37i9dQZF1DX0AZ24QB6TCx',  # Afterhours
    '37i9dQZF1DX2W6AhhHuQN4',  # In a Past Life
    '37i9dQZF1DWVrtsSlLKzro',  # Sad Beats
    '37i9dQZF1DX8CopunbDxgW',  # Metropolis
    '37i9dQZF1DX5GiUwx1edLZ',  # mint Acoustic
    '37i9dQZF1DX13R6rBZEpj7',  # Bassline Bangers
    '37i9dQZF1DWYzMfRQj22Nd',  # Stepping Out
    '37i9dQZF1DXa41CMuUARjl',  # Friday Cratediggers
    '37i9dQZF1DX8AliSIsGeKd',  # Electronis Rising
    '37i9dQZF1DX4pbGJDhTXK3',  # Space Disco
    '37i9dQZF1DX5YyEO1dtgbR',  # Electronis Avant-Grande
]

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Music')


# Create a function that takes a string as input and output, no bytestring
def base64_encode_string(string):
    return b64encode(string.encode()).decode()


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
            record = {
                'Artist': artist['name'],
                'Song': track['name'],
                'Album': album['name'],
                'Date': album['release_date'],
                'Year': album['release_date'][:4],
                'Popularity': track['popularity'],
                'Preview': track['preview_url'],
                'Duration': track['duration_ms'],
                'Markets': track['available_markets'],
            }
            if record['Preview'] is None:
                del record['Preview']

            yield record


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
