import boto3
from sys import argv
from time import time

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Music')

indices = {
    'Song': 'Song-Artist-index',
    'Year': 'Year-Song-index',
}

def performance(method):
    def wrapped(*args, **kw):
        start_time = time()
        response = method(*args, **kw)
        duration = time() - start_time

        print('Returned {} items'.format(response['Count']))
        print('Scanned {} items'.format(response['ScannedCount']))
        print('Duration {:0.3f} seconds'.format(duration))
        print('')

    return wrapped

@performance
def scan(key, value):
    print('Performing a SCAN operation')
    return table.scan(
        ScanFilter={
            key: {
                'AttributeValueList': [value],
                'ComparisonOperator': 'EQ',
            }
        }
    )

@performance
def query(key, value, index_name):
    print('Performing a QUERY operation')
    return table.query(
        IndexName=index_name,
        KeyConditions={
            key: {
                'AttributeValueList': [value],
                'ComparisonOperator': 'EQ',
            }
        }
    )

if __name__ == '__main__':
    key = argv[1] if len(argv) >= 2 else 'Year'
    value = argv[2] if len(argv) >= 2 else '2010'
    if key in indices:
        index_name = indices[key]
    else:
        raise Exception('Invalid key. Needs to be Year or Song')

    scan(key, value)
    query(key, value, index_name)
