import datetime
from typing import Optional

def check_parking_violation(spot_type: str, allowed_time: int, parking_start: str,
                            driver_has_permission: bool) -> Optional[str]:
    now = datetime.datetime.now()
    fmt = "%Y-%m-%dT%H:%M:%S" 
    try:
        start_time = datetime.datetime.strptime(parking_start, fmt)
    except ValueError as e:
        return f"Invalid start_time format: {e}"
    
    elapsed_minutes = (now - start_time).total_seconds() / 60

    if not driver_has_permission and elapsed_minutes > allowed_time:
        exceeded = int(elapsed_minutes - allowed_time)
        return f"Przekroczono czas parkowania o {exceeded} minut"
    return None
