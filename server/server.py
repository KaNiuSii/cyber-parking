from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI()

# Models
class ParkingSpot(BaseModel):
    id: int
    status: str  # e.g., "occupied", "available"

class CreateParkingRequest(BaseModel):
    total_spots: int

class UpdateParkingRequest(BaseModel):
    spot_updates: List[ParkingSpot]

# In-memory data store
parking_lot = {}

# Endpoints
@app.post("/create_parking")
async def create_parking(request: CreateParkingRequest):
    if parking_lot:
        raise HTTPException(status_code=400, detail="Parking lot already created")
    parking_lot.update({i: "available" for i in range(1, request.total_spots + 1)})
    return {"message": "Parking lot created", "total_spots": len(parking_lot)}

@app.post("/update_parking")
async def update_parking(request: UpdateParkingRequest):
    for spot in request.spot_updates:
        if spot.id not in parking_lot:
            raise HTTPException(status_code=404, detail=f"Spot ID {spot.id} not found")
        parking_lot[spot.id] = spot.status
    return {"message": "Parking lot updated", "updated_spots": request.spot_updates}

# Endpoint to check the parking lot state (for testing)
@app.get("/parking_status")
async def parking_status():
    return parking_lot
