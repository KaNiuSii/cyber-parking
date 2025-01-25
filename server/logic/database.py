import sqlite3
from sqlite3 import Connection

DB_NAME = "parking.db"

def get_connection() -> Connection:
    return sqlite3.connect(DB_NAME)

def create_tables():
    conn = get_connection()
    c = conn.cursor()
    
    c.execute("""
        CREATE TABLE IF NOT EXISTS parking_events (
            event_id INTEGER PRIMARY KEY AUTOINCREMENT,
            car_id TEXT,
            spot_id INTEGER,
            start_time TEXT,
            end_time TEXT,
            violation TEXT,
            pos_x REAL,
            pos_y REAL
        )
    """)

    conn.commit()
    conn.close()


def insert_or_update_car_position(nr_rejestracyjny,
                                  czas_wjazdu: str,
                                  czy_zaparkowane: int,
                                  nr_miejsca_zaparkowanego,
                                  aktualna_pozycja_x: float,
                                  aktualna_pozycja_y: float):

    conn = get_connection()
    c = conn.cursor()
    
    
    query = """
        INSERT INTO samochody (
            nr_rejestracyjny,
            czas_wjazdu,
            czy_zaparkowane,
            nr_miejsca_zaparkowanego,
            aktualna_pozycja_x,
            aktualna_pozycja_y
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """
    
    c.execute(query, (
        nr_rejestracyjny,               #  None  --> TODO 
        czas_wjazdu,
        czy_zaparkowane,
        nr_miejsca_zaparkowanego,
        aktualna_pozycja_x,
        aktualna_pozycja_y
    ))
    
    conn.commit()
    conn.close()
def insert_parking_event(car_id: str,
                         spot_id: int,
                         start_time: str,
                         end_time: str = None,
                         violation: str = None) -> int:
    conn = get_connection()
    c = conn.cursor()

    query = """
        INSERT INTO parking_events (car_id, spot_id, start_time, end_time, violation)
        VALUES (?, ?, ?, ?, ?)
    """
    c.execute(query, (car_id, spot_id, start_time, end_time, violation))
    event_id = c.lastrowid

    conn.commit()
    conn.close()

    return event_id

def update_parking_event_end_time(event_id: int, end_time: str):
    conn = get_connection()
    c = conn.cursor()

    query = """
        UPDATE parking_events
        SET end_time = ?
        WHERE event_id = ?
    """
    c.execute(query, (end_time, event_id))

    conn.commit()
    conn.close()

def insert_parking_event_log(car_id: str,
                             spot_id: int | None,
                             timestamp: str,
                             pos_x: float,
                             pos_y: float):
    conn = get_connection()
    c = conn.cursor()

    query = """
        INSERT INTO parking_events (
            car_id, 
            spot_id, 
            start_time,  -- używamy tej kolumny jako 'timestamp'
            pos_x, 
            pos_y
        )
        VALUES (?, ?, ?, ?, ?)
    """
    c.execute(query, (car_id, spot_id, timestamp, pos_x, pos_y))
    conn.commit()
    conn.close()

