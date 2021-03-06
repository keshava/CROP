
from utils.upload_syntetic_data import upload_syntetic_data

from __app__.crop.constants import SQL_CONNECTION_STRING, SQL_TEST_DBNAME
from __app__.crop.db import drop_db

def pytest_configure(config):
    """
    Allows plugins and conftest files to perform initial configuration.
    This hook is called for every plugin and initial conftest
    file after command line options have been parsed.
    """

    print("pytest_configure: start")
    
    # establishes temp DB for testing
    upload_syntetic_data.main(SQL_TEST_DBNAME)

    print("pytest_configure: end")

def pytest_unconfigure(config):
    """
    called before test process is exited.
    """

    print("pytest_unconfigure: start")
    
    # drops test db
    success, log = drop_db(SQL_CONNECTION_STRING, SQL_TEST_DBNAME)
    assert success, log

    print("pytest_unconfigure: end")