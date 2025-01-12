from fastapi import Body

from typing import List
from fastapi import FastAPI, HTTPException
from models.data import Data
from models.parking_space import ParkingSpace
from models.car_position import CarPosition
from models.server_response import ServerResponse
from workers.iworker import IWorker
from workers.parked import Parked
from workers.not_moving import NotMoving


app = FastAPI()

data_store: List[List[Data]] = []

workers: List[IWorker] = [
    Parked(),
    NotMoving()
]


@app.post("/create_parking_data")
async def create_parking_data(
    parking_spaces: List[ParkingSpace] = Body(...),
    car_positions: List[CarPosition] = Body(...)
):
    new_data = Data(
        id=len(data_store),
        parking_spaces=parking_spaces,
        car_positions=car_positions,
        server_response=ServerResponse(parked=0, not_moving=[])
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

    data_store[new_data.id].append(new_data)
    return {"data": new_data}
