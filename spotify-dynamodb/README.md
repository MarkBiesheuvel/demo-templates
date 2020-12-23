# Spotify DynamoDB (Music table)

This demo shows the difference in performance between a DynamoDB `scan` vs `query`. The table design is inspired by an example from [AWS Technical Essentials](https://aws.amazon.com/training/course-descriptions/essentials/) course.

To create the table you can upload the template in the AWS Management Console or you can run the following command on the CLI:

```sh
aws cloudformation create-stack --stack-name Music --template-body file://spotify-dynamodb/template.yml
```

To import records you can use the `import.py` script. For this script you need to have configured Spotify API Client credentials:

```sh
export SPOTIFY_CLIENT_ID=0123456789abcdef0123456789abcdef
export SPOTIFY_CLIENT_SECRET=0123456789abcdef0123456789abcdef
python spotify-dynamodb/import.py
```

To show the performance difference you can run the following commands:

```sh
python spotify-dynamodb/performance.py Year 2010
python spotify-dynamodb/performance.py Song Strobe
python spotify-dynamodb/performance.py Artist deadmau5
```

Shout out to **[deadmau5 - Strobe](https://open.spotify.com/track/4kJWtxDDNb9oAk3h7sX3N4?si=UedLYLq3QUecPRcj_OsMXw)**
