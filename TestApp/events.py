from pydantic import BaseModel
from datetime import datetime

class ButtonPressEvent(BaseModel):
    Button: int
    DeviceType: str
    DeviceId: str
    Metadata: str

class PackagePickerConfirmedPayload(BaseModel):
    DeviceId:str
    Type: str

class PackageArrivedPayload(BaseModel):
    Location: str
    Type: str

class PackagePickerConfirmedEvent (BaseModel):
    TimeStamp: datetime
    Type: str
    Payload: PackagePickerConfirmedPayload

class PackageArrivedEvent (BaseModel):
    TimeStamp: datetime
    Type: str
    Payload: PackageArrivedPayload
