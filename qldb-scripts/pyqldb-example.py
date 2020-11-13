from pyqldb.driver.qldb_driver import QldbDriver
from pyqldb.execution.executor import Executor

qldb_driver = QldbDriver(ledger_name='vehicle-registration')

statement = 'SELECT h.metadata.version, h.data.VIN, h.data.City, h.data.Owners, h.hash FROM history(VehicleRegistration) AS h WHERE h.metadata.id = \'L7S9pXJJaSn3YvTcpNXgTL\''


def query(transaction_executor: Executor, statement: str):
    cursor = transaction_executor.execute_statement(statement)

    for doc in cursor:
        print('Version={version} VIN={vin} City={city}'.format(
            version=doc['version'],
            vin=doc['VIN'],
            city=doc['City']
        ))


if __name__ == '__main__':
    qldb_driver.execute_lambda(lambda executor: query(executor, statement))
