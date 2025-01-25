# from fastapi import Body

# from typing import List
# from fastapi import FastAPI, HTTPException
# from models.data import Data
# from models.parking_space import ParkingSpace
# from models.car_position import CarPosition
# from models.server_response import ServerResponse
# from workers.iworker import IWorker
# from workers.parked import Parked
# from workers.parked_names import ParkedNames
# from workers.not_moving import NotMoving


# app = FastAPI()

# data_store: List[List[Data]] = []

# workers: List[IWorker] = [
#     Parked(),
#     NotMoving(),
#     ParkedNames()
# ]


# @app.post("/create_parking_data")
# async def create_parking_data(
#     parking_spaces: List[ParkingSpace] = Body(...),
#     car_positions: List[CarPosition] = Body(...)
# ):
#     new_data = Data(
#         id=len(data_store),
#         parking_spaces=parking_spaces,
#         car_positions=car_positions,
#         server_response=ServerResponse(parked=0, not_moving=[], parked_names=[])
#     )
#     data_store.append([new_data])
#     return {"data": new_data}


# @app.post("/update_parking_data")
# async def update_parking_data(new_data: Data):
#     if new_data.id >= len(data_store) or not data_store[new_data.id]:
#         raise HTTPException(status_code=404, detail="No parking data exists to update")

#     data_chain: List[Data] = data_store[new_data.id]

#     for worker in workers:
#         new_data = worker.apply(data_chain=data_chain, new_data=new_data)

#     data_store[new_data.id].append(new_data)
#     return {"data": new_data}




from typing import List
from fastapi import FastAPI, HTTPException, Body
import asyncio
import datetime

from models.data import Data
from models.car_position import CarPosition
from models.parking_space import ParkingSpace
from models.server_response import ServerResponse

from workers.iworker import IWorker
from workers.parked import Parked
from workers.parked_names import ParkedNames
from workers.not_moving import NotMoving

from logic.database import create_tables, insert_or_update_car_position
from logic.database import insert_parking_event_log

app = FastAPI()

data_store: List[List[Data]] = []


last_logged_data_id = None


workers: List[IWorker] = [
    Parked(),
    NotMoving(),
    ParkedNames()
]

@app.on_event("startup")
async def startup_event():
    create_tables()
    asyncio.create_task(store_positions_periodically())


@app.delete("/clear_data_store")
async def clear_data_store():
    data_store.clear()
    return {"message": "data_store cleared"}



async def store_positions_periodically():
    while True:
        try:
            store_current_positions_in_db()
        except Exception as e:
            print(f"Wystąpił błąd przy zapisywaniu pozycji: {e}")
        await asyncio.sleep(3)
    
def store_current_positions_in_db():
    global last_logged_data_id
    if not data_store:
        return
    
    last_chain = data_store[-1]
    if not last_chain:
        return
    
    last_data_obj = last_chain[-1]


    if last_logged_data_id == last_data_obj.id:
        return

    now = datetime.datetime.now().isoformat(timespec='seconds')

    for car_pos in last_data_obj.car_positions:
        car_id = car_pos.name or "Unknown"
        spot_id = car_pos.parked_spot if car_pos.is_parked else None

        insert_parking_event_log(
            car_id=car_id,
            spot_id=spot_id,
            timestamp=now,
            pos_x=car_pos.x,
            pos_y=car_pos.y
        )
    last_logged_data_id = last_data_obj.id



@app.post("/create_parking_data")
async def create_parking_data(
    parking_spaces: List[ParkingSpace] = Body(...),
    car_positions: List[CarPosition] = Body(...)
):
    new_data = Data(
        id=len(data_store),
        parking_spaces=parking_spaces,
        car_positions=car_positions,
        server_response=ServerResponse(parked=0, not_moving=[], parked_names=[])
    )
    data_store.append([new_data])
    return {"data": new_data}

@app.post("/update_parking_data")
async def update_parking_data(new_data: Data):
    if new_data.id >= len(data_store) or not data_store[new_data.id]:
        raise HTTPException(status_code=404, detail="No parking data exists to update")

    data_chain: List[Data] = data_store[new_data.id]

    for worker in workers:
        new_data = worker.apply(data_chain=data_chain, new_data=new_data)

    data_chain.append(new_data)
    return {"data": new_data}

@app.post("/update_positions")
async def update_positions(car_positions: List[CarPosition]):
    if not data_store:
        raise HTTPException(status_code=404, detail="No parking data in data_store.")

    last_chain = data_store[-1]
    if not last_chain:
        raise HTTPException(status_code=404, detail="No data objects in the last chain.")

    last_data_obj = last_chain[-1]

    last_data_obj.car_positions = car_positions

    return {"message": "Pozycje zaktualizowane w ostatnim obiekcie Data."}
@app.post("/update_parking_data")
async def update_parking_data(new_data: Data):
    if new_data.id >= len(data_store) or not data_store[new_data.id]:
        raise HTTPException(status_code=404, detail="No parking data exists to update")

    data_chain: List[Data] = data_store[new_data.id]

    for worker in workers:
        new_data = worker.apply(data_chain=data_chain, new_data=new_data)

    data_store[new_data.id].append(new_data)
    return {"data": new_data}
