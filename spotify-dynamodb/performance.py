import boto3
from sys import argv
from time import time

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Music')

indices = {
    'Artist': None,
    'Song': 'Song-Artist-index',
    'Year': 'Year-Song-index',
}


def performance(method):
    def wrapped(*args, **kw):
        start_time = time()
        response = method(*args, **kw)
        duration = time() - start_time

        print('  - Returned {} items'.format(response.get('Count', 0)))
        print('  - Scanned {} items'.format(response.get('ScannedCount', 0)))
        print('  - Duration {:0.3f} seconds'.format(duration))
        print('')

        return response.get('LastEvaluatedKey')

    return wrapped


@performance
def scan(attribute, value, last_key=None):
    kwargs = {
        'ScanFilter': {
            attribute: {
                'AttributeValueList': [value],
                'ComparisonOperator': 'EQ',
            }
        }
    }

    if last_key:
        kwargs['ExclusiveStartKey'] = last_key

    return table.scan(**kwargs)


@performance
def query(attribute, value, index_name, last_key=None):
    kwargs = {
        'KeyConditions': {
            attribute: {
                'AttributeValueList': [value],
                'ComparisonOperator': 'EQ',
            }
        }
    }

    if index_name:
        kwargs['IndexName'] = index_name

    if last_key:
        kwargs['ExclusiveStartKey'] = last_key

    return table.query(**kwargs)


def scan_iterator(attribute, value):
    print(' == Performing a SCAN operation ==')
    print('')
    last_key = None
    while True:
        last_key = scan(attribute, value, last_key)
        if last_key is None:
            break


def query_iterator(attribute, value, index_name):
    print(' == Performing a QUERY operation ==')
    print('')
    last_key = None
    while True:
        last_key = query(attribute, value, index_name, last_key)
        if last_key is None:
            break


if __name__ == '__main__':
    attribute = argv[1] if len(argv) >= 2 else 'Year'
    value = argv[2] if len(argv) >= 2 else '2010'
    if attribute in indices:
        index_name = indices[attribute]
    else:
        raise Exception('Invalid key. Needs to be Artist, Year or Song')

    scan_iterator(attribute, value)
    query_iterator(attribute, value, index_name)
