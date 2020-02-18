import pytest
import pandas as pd
import os
from sqlalchemy.orm import sessionmaker, relationship


from crop.structure import(
    Type,
    Location,
    Sensor
    )

from crop.constants import (
    SQL_DBNAME,
    CONST_COREDATA_DIR,
    CONST_ADVANTIX_DIR,
    CONST_ADVANTIX_TEST_1,
    CONST_ADVANTIX_TEST_10,
    SQL_CONNECTION_STRING,
)
from crop.db import (
    connect_db,
    create_database,
    drop_db
)
from crop.ingress import (
    advantix_import
)

from crop.populate_db import (
    session_open,
    session_close,
    insert_advantix_data
)


test_db_name = "fake_db"

@pytest.mark.order1
def test_create_database():

     #Test create new db
     created, log = create_database(SQL_CONNECTION_STRING, test_db_name)
     assert created, log

@pytest.mark.order2
def test_insert_type_data():
    
     test_csv = "Sensortypes.csv"
    
     type_df = pd.read_csv(os.path.join(CONST_COREDATA_DIR, test_csv))
     assert type_df.empty == False

     # Try to connect to an engine that exists
     status, log, engine = connect_db(SQL_CONNECTION_STRING, test_db_name)
     assert status, log

     #Creates/Opens a new connection to the db and binds the engine
     session = session_open(engine)

     session.bulk_insert_mappings(Type, type_df.to_dict(orient='records'))
     assert session.query(Type).count() == len(type_df.index)

     session_close(session)

@pytest.mark.order3
def test_insert_sensor_data():
    
     test_csv = "Sensors.csv"
    
     sensor_df = pd.read_csv(os.path.join(CONST_COREDATA_DIR, test_csv))
     assert sensor_df.empty == False

     # Try to connect to an engine that exists
     status, log, engine = connect_db(SQL_CONNECTION_STRING, test_db_name)
     assert status, log

     #Creates/Opens a new connection to the db and binds the engine
     session = session_open(engine)
    
     session.bulk_insert_mappings(Sensor, sensor_df.to_dict(orient='records'))
     assert session.query(Sensor).count() == len(sensor_df.index)
    
     session_close (session)

@pytest.mark.order4   
def test_insert_location_data():
    
     test_csv = "Locations.csv"
    
     #test reading type data
     df = pd.read_csv(os.path.join(CONST_COREDATA_DIR, test_csv))
     assert df.empty == False

     # Try to connect to an engine that exists
     status, log, engine = connect_db(SQL_CONNECTION_STRING, test_db_name)
     assert status, log

     #Creates/Opens a new connection to the db and binds the engine
     session = session_open (engine)

     session.bulk_insert_mappings(Location, df.to_dict(orient='records'))
     assert session.query(Location).count() == len(df.index)

     session_close(session)

@pytest.mark.order5    
def test_insert_advantix_data():
 
    file_path = os.path.join(CONST_ADVANTIX_DIR, CONST_ADVANTIX_TEST_1)
    success,log, test_ingress_df = advantix_import(file_path)
    assert success, log
    assert isinstance(test_ingress_df, pd.DataFrame)
    
    # Try to connect to an engine that exists
    status, log, engine = connect_db(SQL_CONNECTION_STRING, test_db_name)
    assert status, log

    #Creates/Opens a new connection to the db and binds the engine
    session = session_open(engine)
    #stest loading sensor data to db
    success, log = insert_advantix_data(session, test_ingress_df)
    assert success, log

    file_path = os.path.join(CONST_ADVANTIX_DIR, CONST_ADVANTIX_TEST_10)
    success,log, test_ingress_df = advantix_import(file_path)
    assert success, log
    assert isinstance(test_ingress_df, pd.DataFrame)

    success, log = insert_advantix_data(session, test_ingress_df)
    assert not success, log


    session_close (session)


test_insert_advantix_data()
# #test_insert_type_data()
# #test_insert_sensor_data()
# #test_insert_location_data()

# @pytest.mark.order20
# def test_drop_db():

#     #Test create new db
#     success, log = drop_db(SQL_CONNECTION_STRING, test_db_name)
#     assert success, log