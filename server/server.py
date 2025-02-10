from fastapi import Body, Depends, FastAPI, HTTPException
from fastapi.encoders import jsonable_encoder
from typing import List
from datetime import datetime
from pathlib import Path
import csv

from sqlalchemy.orm import Session

from models.data import Data
from models.parking_space import ParkingSpace
from models.car_position import CarPosition
from models.license_plate import LicensePlate
from models.server_response import ServerResponse

from workers.iworker import IWorker
from workers.parked import Parked
from workers.parked_names import ParkedNames
from workers.not_moving import NotMoving
from workers.license_plate_queue import LicensePlateQueue

from database.database import (
    SessionLocal,
    ParkingLogs,
    EntranceInfo,
    ExitInfo,
    ParkingCost,
    LicensePlates,
    init_db,
)

app = FastAPI()

data_store: List[List[Data]] = []

workers: List[IWorker] = [
    Parked(),
    NotMoving(),
    ParkedNames(),
    LicensePlateQueue()
]

def load_subscriptions_from_csv(db: Session, csv_path: str):
    try:
        with open(csv_path, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                plate = row['plate']
                subscription = LicensePlates(Plate=plate)
                db.add(subscription)
        db.commit()
        print("Loaded subscriptions from CSV")
    except Exception as e:
        db.rollback()
        print(f"Error loading subscriptions: {e}")

@app.on_event("startup")
async def startup_event():
    init_db()
    db = SessionLocal()
    try:
        csv_path = Path('./database/subscriptions.csv')
        load_subscriptions_from_csv(db, csv_path)
    finally:
        db.close()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/create_parking_data")
async def create_parking_data(
    parking_spaces: List[ParkingSpace] = Body(...),
    car_positions: List[CarPosition] = Body(...),
    enterance_license_plates: List[LicensePlate] = Body(...),
    exit_license_plates: List[LicensePlate] = Body(...),
    db: Session = Depends(get_db)
):
    new_data = Data(
        id=len(data_store),
        parking_spaces=parking_spaces,
        car_positions=car_positions,
        enterance_license_plates=enterance_license_plates,
        exit_license_plates=exit_license_plates,
        server_response=ServerResponse(
            parked=0,
            not_moving=[],
            parked_names=[],
            enterence_license_plates=[],
            exit_license_plates=[]
        )
    )
    data_store.append([new_data])
    
    log_entry = ParkingLogs(JSONDump=new_data.dict())
    db.add(log_entry)
    db.commit()
    db.refresh(log_entry)
    
    return {"data": new_data}

@app.post("/update_parking_data")
async def update_parking_data(new_data: Data, db: Session = Depends(get_db)):
    if new_data.id >= len(data_store) or not data_store[new_data.id]:
        raise HTTPException(status_code=404, detail="No parking data exists to update")
    
    data_chain: List[Data] = data_store[new_data.id]
    
    for worker in workers:
        new_data = worker.apply(data_chain=data_chain, new_data=new_data)
    
    data_store[new_data.id].append(new_data)
    
    log_entry = ParkingLogs(JSONDump=jsonable_encoder(new_data))
    db.add(log_entry)
    
    for plate in new_data.enterance_license_plates:
        entry = EntranceInfo(
            EntryTime=plate.arrival_time,
            Plate=plate.number
        )
        db.add(entry)
    
    for plate in new_data.exit_license_plates:
        exit_record = ExitInfo(
            ExitTime=plate.arrival_time,
            Plate=plate.number
        )
        db.add(exit_record)
        
        entry_record = (
            db.query(EntranceInfo)
            .filter(EntranceInfo.Plate == plate.number)
            .order_by(EntranceInfo.EntryTime.desc())
            .first()
        )
        
        if entry_record:
            # subscription
            has_subscription = db.query(LicensePlates).filter(LicensePlates.Plate == plate.number).first() is not None
            
            if has_subscription:
                parked_time = 0.0
                cost = 0.0
            else:
                parked_time = (plate.arrival_time - entry_record.EntryTime).total_seconds() / 3600.0
                cost = parked_time * 10.0
            
            parking_cost = ParkingCost(
                Plate=plate.number,
                ParkedTime=parked_time,
                ParkingCost=cost
            )
            db.add(parking_cost)
    
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error")
    
    return {"data": jsonable_encoder(new_data)}