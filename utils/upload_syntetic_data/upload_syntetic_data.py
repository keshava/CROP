#!/usr/bin/python
"""
Script that creates (if needed) a database in an existing PostgreSQL server and uploads
syntetic data to it.
"""

import argparse

import os
import sys
import pandas as pd

from __app__.crop.structure import (
    TypeClass,
    LocationClass,
    SensorClass,
    SensorLocationClass,
)

from __app__.crop.constants import (
    CONST_COREDATA_DIR,
    CONST_ADVANTICSYS_DIR,
    CONST_ADVANTICSYS_TEST_1,
    SQL_CONNECTION_STRING,
    CONST_TEST_DIR_DATA,
    CONST_SENSOR_LOCATION_TESTS,
)

from __app__.crop.db import (
    create_database,
    connect_db,
    session_open,
    session_close,
)

from __app__.crop.ingress_adv import advanticsys_import, insert_advanticsys_data


def error_message(message):
    """
    Prints error message.

    """

    print(f"ERROR: {message}")
    sys.exit()


def insert_type_data(engine):
    """
    Bulk inserts test type data.

    Arguments:
        engine: SQL engine object
    """

    test_csv = "Sensortypes.csv"
    type_df = pd.read_csv(os.path.join(CONST_COREDATA_DIR, test_csv))

    assert not type_df.empty

    # Creates/Opens a new connection to the db and binds the engine
    session = session_open(engine)

    # Check if table is empty and bulk inserts if it is
    first_entry = session.query(TypeClass).first()

    if first_entry is None:
        session.bulk_insert_mappings(TypeClass, type_df.to_dict(orient="records"))
        session_close(session)

        assert session.query(TypeClass).count() == len(type_df.index)
    else:
        session_close(session)

        assert session.query(TypeClass).count() == len(type_df.index)


def insert_location_data(engine):
    """
    Bulk inserts test location data.

    Arguments:
        engine: SQL engine object
    """

    test_csv = "locations.csv"
    loc_df = pd.read_csv(os.path.join(CONST_COREDATA_DIR, test_csv))

    assert not loc_df.empty

    # Creates/Opens a new connection to the db and binds the engine
    session = session_open(engine)

    # Check if table is empty and bulk inserts if it is
    first_entry = session.query(LocationClass).first()

    if first_entry is None:
        session.bulk_insert_mappings(LocationClass, loc_df.to_dict(orient="records"))
        session_close(session)

        assert session.query(LocationClass).count() == len(loc_df.index)
    else:
        session_close(session)

        assert session.query(LocationClass).count() == len(loc_df.index)


def insert_sensor_data(engine):
    """
    Bulk inserts test sensor data.

    Arguments:
        engine: SQL engine object
    """

    test_csv = "Sensors.csv"
    sensor_df = pd.read_csv(os.path.join(CONST_COREDATA_DIR, test_csv))

    assert not sensor_df.empty

    # Creates/Opens a new connection to the db and binds the engine
    session = session_open(engine)

    # Check if table is empty and bulk inserts if it is
    first_entry = session.query(SensorClass).first()

    if first_entry is None:
        session.bulk_insert_mappings(SensorClass, sensor_df.to_dict(orient="records"))
        session_close(session)

        assert session.query(SensorClass).count() == len(sensor_df.index)
    else:
        session_close(session)

        assert session.query(SensorClass).count() == len(sensor_df.index)


def insert_adv_data(engine):
    """
    Bulk inserts test advanticsys data

    Arguments:
        engine: SQL engine object
    """

    file_path = os.path.join(CONST_ADVANTICSYS_DIR, CONST_ADVANTICSYS_TEST_1)
    success, log, test_ingress_df = advanticsys_import(file_path)

    assert success, log
    assert isinstance(test_ingress_df, pd.DataFrame)

    # Creates/Opens a new connection to the db and binds the engine
    session = session_open(engine)

    # tests loading sensor data to db
    success, log = insert_advanticsys_data(session, test_ingress_df)
    session_close(session)
    assert success, log

def import_sensor_location(engine):
    """
    Bulk inserts sensor location data

    Arguments:
        engine: SQL engine object
    """

    test_csv = "sensor_location.csv"

    sensor_df = pd.read_csv(os.path.join(CONST_COREDATA_DIR, test_csv))
    assert not sensor_df.empty

    # Creates/Opens a new connection to the db and binds the engine
    session = session_open(engine)

    # Check if table is empty and bulk inserts if it is
    first_entry = session.query(SensorLocationClass).first()

    if first_entry is None:
        session.bulk_insert_mappings(
            SensorLocationClass, sensor_df.to_dict(orient="records")
        )
        session_close(session)

        assert session.query(SensorLocationClass).count() == len(sensor_df.index)
    else:
        session_close(session)

        assert session.query(SensorLocationClass).count() == len(sensor_df.index)

    # Trying to upload location history data for a sensor that does not exist
    test_csv = "sensor_location_test_1.csv"

    sensor_df = pd.read_csv(
        os.path.join(CONST_TEST_DIR_DATA, CONST_SENSOR_LOCATION_TESTS, test_csv)
    )
    assert not sensor_df.empty

    session = session_open(engine)
    try:
        session.bulk_insert_mappings(
            SensorLocationClass, sensor_df.to_dict(orient="records")
        )
        result = True
    except:
        session.rollback()
        result = False

    session_close(session)

    assert not result

    # Trying to upload location history data for a location that does not exist
    test_csv = "sensor_location_test_2.csv"

    sensor_df = pd.read_csv(
        os.path.join(CONST_TEST_DIR_DATA, CONST_SENSOR_LOCATION_TESTS, test_csv)
    )
    assert not sensor_df.empty

    session = session_open(engine)

    try:
        session.bulk_insert_mappings(
            SensorLocationClass, sensor_df.to_dict(orient="records")
        )
        result = True
    except:
        session.rollback()
        result = False

    session_close(session)

    assert not result

    # Trying to upload location history data with an empty installation date
    test_csv = "sensor_location_test_3.csv"

    sensor_df = pd.read_csv(
        os.path.join(CONST_TEST_DIR_DATA, CONST_SENSOR_LOCATION_TESTS, test_csv)
    )
    assert not sensor_df.empty

    session = session_open(engine)

    try:
        session.bulk_insert_mappings(
            SensorLocationClass, sensor_df.to_dict(orient="records")
        )
        result = True
    except:
        session.rollback()
        result = False

    session_close(session)

    assert not result


def main(db_name):
    """
    Main routine.

    Arguments:
        db_name: Database name
    """

    created, log = create_database(SQL_CONNECTION_STRING, db_name)

    if not created:
        error_message(log)

    # creating an engine
    status, log, engine = connect_db(SQL_CONNECTION_STRING, db_name)

    if not status:
        error_message(log)

    insert_type_data(engine)

    insert_location_data(engine)

    insert_sensor_data(engine)

    insert_adv_data(engine)

    import_sensor_location(engine)


if __name__ == "__main__":

    # Command line arguments
    PARSER = argparse.ArgumentParser(
        description="Uploads syntetic data to a PostgreSQL database."
    )
    PARSER.add_argument("dbname", default=None, help="Database name")

    # Makes sure that the database exists (creates it if needed.)
    ARGS, _ = PARSER.parse_known_args()

    main((ARGS.dbname).strip())

    print("Finished.")
