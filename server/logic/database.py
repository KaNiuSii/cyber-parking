import sqlite3
from typing import List
from sqlite3 import Connection
from models.data import Data
from models.car_position import CarPosition
from models.server_response import ServerResponse
from models.parking_space import ParkingSpace
from models.license_plate import LicensePlate

DB_NAME = "parking.db"

def get_connection() -> Connection:
    return sqlite3.connect(DB_NAME)

def create_tables():
    conn = get_connection()
    c = conn.cursor()
    
    c.execute("""
        CREATE TABLE IF NOT EXISTS ParkingLogs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            JSONDump TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS LicencePlate (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plate TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS EntrenceInfo (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            EntryTime TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS ExitInfo (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ExitTime TEXT
        )
    """)

    conn.commit()
    conn.close()

def clear_database():
    conn = get_connection()
    c = conn.cursor()
    
    c.execute("DELETE FROM ParkingLogs")
    c.execute("DELETE FROM LicencePlate")
    c.execute("DELETE FROM EntrenceInfo")
    c.execute("DELETE FROM ExitInfo")

    conn.commit()
    conn.close()


def insert_data_model(data_obj: Data) -> int:
    conn = get_connection()
    c = conn.cursor()

    json_data = data_obj.json() 
    query = "INSERT INTO ParkingLogs (JSONDump) VALUES (?);"
    c.execute(query, (json_data,))
    new_id = c.lastrowid

    conn.commit()
    conn.close()

    return new_id

def get_data_model(log_id: int) -> Data:
    conn = get_connection()
    c = conn.cursor()

    c.execute("SELECT JSONDump FROM ParkingLogs WHERE id = ?", (log_id,))
    row = c.fetchone()
    conn.close()

    if not row:
        raise ValueError(f"No record in ParkingLogs for id={log_id}")

    json_data = row[0]
    return Data.parse_raw(json_data)

def insert_or_update_car_position(car_pos: CarPosition, czas_wjazdu: str = None):
    data_obj = Data(
        id=0,
        parking_spaces=[],
        car_positions=[car_pos],
        server_response=ServerResponse(parked=0, not_moving=[], parked_names=[])
    )
    insert_data_model(data_obj)

    conn = get_connection()
    c = conn.cursor()
    if car_pos.name and car_pos.name.lower() != "unknown":
        c.execute("INSERT INTO LicencePlate (plate) VALUES (?)", (car_pos.name,))

    if czas_wjazdu:
        c.execute("INSERT INTO EntrenceInfo (EntryTime) VALUES (?)", (czas_wjazdu,))

    conn.commit()
    conn.close()

def insert_parking_event(
    car_id: str,
    spot_id: int,
    start_time: str,
    end_time: str = None,
    violation: str = None,
    x: float = 0,
    y: float = 0,
    w: float = 0,
    h: float = 0
) -> int:
    is_parked_flag = (end_time is None)

    from models.car_position import CarPosition
    car_pos = CarPosition(
        name=car_id,
        x=int(x),
        y=int(y),
        w=int(w),
        h=int(h),
        is_parked=is_parked_flag,
        parked_spot=spot_id
    )
    data_obj = Data(
        id=0,
        parking_spaces=[],
        car_positions=[car_pos],
        server_response=ServerResponse(
            parked=1 if is_parked_flag else 0,
            not_moving=[],
            parked_names=[]
        )
    )

    new_id = insert_data_model(data_obj)

    conn = get_connection()
    c = conn.cursor()
    if start_time:
        c.execute("INSERT INTO EntrenceInfo (EntryTime) VALUES (?)", (start_time,))
    if end_time:
        c.execute("INSERT INTO ExitInfo (ExitTime) VALUES (?)", (end_time,))

    conn.commit()
    conn.close()

    return new_id

def update_parking_event_end_time(event_id: int, end_time: str):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT JSONDump FROM ParkingLogs WHERE id = ?", (event_id,))
    row = c.fetchone()
    conn.close()

    if not row:
        raise ValueError(f"No record in ParkingLogs with id={event_id}")

    current_json = row[0]
    data_obj = Data.parse_raw(current_json)

    data_obj.server_response.parked = 0
    for cp in data_obj.car_positions:
        cp.is_parked = False

    new_json = data_obj.json()

    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE ParkingLogs SET JSONDump = ? WHERE id = ?", (new_json, event_id))
    c.execute("INSERT INTO ExitInfo (ExitTime) VALUES (?)", (end_time,))
    conn.commit()
    conn.close()



def insert_parking_event_log(
    frame_id: int,
    timestamp: str,
    data: Data
) -> int:
    try:
        conn = get_connection()
        c = conn.cursor()
        
        json_data = data.json()
        c.execute("INSERT INTO ParkingLogs (JSONDump) VALUES (?)", (json_data,))
        log_id = c.lastrowid
        c.execute("INSERT INTO EntrenceInfo (EntryTime) VALUES (?)", (timestamp,))
        
        conn.commit()
        return log_id
    except Exception as e:
        print(f"Database insertion error: {e}")
        raise
    finally:
        conn.close()


def get_parking_log(log_id: int) -> Data:
    conn = get_connection()
    c = conn.cursor()
    
    try:
        c.execute("SELECT JSONDump FROM ParkingLogs WHERE id = ?", (log_id,))
        row = c.fetchone()
        
        if not row:
            raise ValueError(f"No log found with id {log_id}")
            
        data = Data.parse_raw(row[0])
        return data
    finally:
        conn.close()