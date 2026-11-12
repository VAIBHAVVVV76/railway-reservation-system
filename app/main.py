from app.database import Base, engine
from app.models.user import User
from app.models.station import Station
from app.models.train import Train
from app.models.booking import Booking
from app.models.seat import Seat
from app.models.reservation import Reservation
from app.routes.booking import router as booking_router
from app.routes.train import router as train_router

from fastapi import FastAPI

app = FastAPI(
    title="Railway Reservation System",
    description="Backend API for railway ticket booking",
    version="1.0.0"
)
app.include_router(booking_router)
app.include_router(train_router)
Base.metadata.create_all(bind=engine)

@app.get("/")
def home():
    return {
        "message": "Welcome to Railway Reservation System!",
        "status": "Backend is running successfully"
    }