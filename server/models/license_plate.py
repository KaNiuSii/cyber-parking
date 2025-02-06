from datetime import datetime
from pydantic import BaseModel, Field
from typing import Dict, Any

class LicensePlate(BaseModel):
    number: str
    arrival_time: datetime

    def dict(self, *args, **kwargs) -> Dict[str, Any]:
        d = super().dict(*args, **kwargs)
        d['arrival_time'] = d['arrival_time'].isoformat()
        return d

    model_config = {
        'json_encoders': {
            datetime: lambda dt: dt.isoformat()
        }
    }