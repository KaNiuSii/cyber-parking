from typing import Optional

class ParkingEvent:
    def __init__(self,
                 event_id: int,
                 car_id: int,
                 spot_id: int,
                 start_time: str,
                 end_time: Optional[str],
                 violation: Optional[str]) -> None:
        self.event_id: int = event_id
        self.car_id: int = car_id
        self.spot_id: int = spot_id
        self.start_time: str = start_time
        self.end_time: Optional[str] = end_time
        self.violation: Optional[str] = violation

    def __repr__(self) -> str:
        return (
            f"<ParkingEvent id={self.event_id} "
            f"car_id={self.car_id} "
            f"spot_id={self.spot_id} "
            f"start={self.start_time} "
            f"end={self.end_time} "
            f"violation={self.violation}>"
        )
