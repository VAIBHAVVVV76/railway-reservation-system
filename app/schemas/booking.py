from datetime import date
from pydantic import BaseModel, Field


class BookingCreate(BaseModel):
    user_id: int
    train_id: int
    journey_date: date
    number_of_seats: int = Field(gt=0)