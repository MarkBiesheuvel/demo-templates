import amazon.ion.simpleion as ion
import boto3

client = boto3.client('qldb-session')

statement = 'SELECT h.metadata.version, h.data.VIN, h.data.City, h.data.Owners, h.hash FROM history(VehicleRegistration) AS h WHERE h.metadata.id = \'L7S9pXJJaSn3YvTcpNXgTL\''


def start_session(ledger_name: str) ->  str:
    response = client.send_command(
        StartSession={
            'LedgerName': ledger_name
        }
    )

    return response['StartSession']['SessionToken']


def start_transaction(session_token: str) -> str:
    response = client.send_command(
        SessionToken=session_token,
        StartTransaction={}
    )

    return response['StartTransaction']['TransactionId']


def execute_statement(session_token: str, transaction_id: str, statement: str):
    response = client.send_command(
        SessionToken=session_token,
        ExecuteStatement={
            'TransactionId': transaction_id,
            'Statement': statement
        }
    )

    return [
        ion.loads(value['IonBinary'])
        for value in response['ExecuteStatement']['FirstPage']['Values']
    ]



if __name__ == '__main__':
    session_token = start_session('vehicle-registration')

    transaction_id = start_transaction(session_token)

    values = execute_statement(session_token, transaction_id, statement)

    for value in values:
        print('Version={version} VIN={vin} City={city}'.format(
            version=value.get('version'),
            vin=value.get('VIN'),
            city=value.get('City')
        ))
