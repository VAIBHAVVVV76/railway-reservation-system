from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.train import Train
from app.models.station import Station
from app.models.seat import Seat
from app.models.reservation import Reservation

router = APIRouter(
    prefix="/trains",
    tags=["Trains"]
)


# Priority 4: List all trains with source and destination details
@router.get("/")
def list_trains(
    db: Session = Depends(get_db)
):
    trains = db.query(Train).all()
    results = []

    for t in trains:
        source_station = db.query(Station).filter(Station.id == t.source_station_id).first()
        dest_station = db.query(Station).filter(Station.id == t.destination_station_id).first()

        results.append({
            "id": t.id,
            "train_number": t.train_number,
            "train_name": t.train_name,
            "fare_per_seat": float(t.fare_per_seat),
            "total_seats": t.total_seats,
            "source": {
                "station_code": source_station.station_code,
                "station_name": source_station.station_name,
                "city": source_station.city
            } if source_station else None,
            "destination": {
                "station_code": dest_station.station_code,
                "station_name": dest_station.station_name,
                "city": dest_station.city
            } if dest_station else None
        })

    return results


# Priority 3: Check seat availability for a train on a specific date
@router.get("/{train_id}/availability")
def check_seat_availability(
    train_id: int,
    journey_date: date = Query(..., description="Journey date in YYYY-MM-DD format"),
    db: Session = Depends(get_db)
):
    # 1. Verify train exists
    train = db.query(Train).filter(Train.id == train_id).first()
    if not train:
        raise HTTPException(status_code=404, detail="Train not found")

    # 2. Fetch all seat records for this train
    seats = (
        db.query(Seat)
        .filter(Seat.train_id == train_id, Seat.status == "available")
        .order_by(Seat.coach_number, Seat.seat_number)
        .all()
    )

    seat_ids = [s.id for s in seats]

    # 3. Find seats already booked for the specified journey date
    reserved_seat_ids = set(
        row[0] for row in
        db.query(Reservation.seat_id)
        .filter(
            Reservation.seat_id.in_(seat_ids),
            Reservation.journey_date == journey_date
        )
        .all()
    ) if seat_ids else set()

    # 4. Separate available from booked
    available_seats = []
    booked_seats = []

    for s in seats:
        seat_info = {
            "seat_id": s.id,
            "coach": s.coach_number,
            "seat_number": s.seat_number,
            "seat_class": s.seat_class
        }
        if s.id in reserved_seat_ids:
            booked_seats.append(seat_info)
        else:
            available_seats.append(seat_info)

    return {
        "train_id": train.id,
        "train_number": train.train_number,
        "train_name": train.train_name,
        "journey_date": str(journey_date),
        "total_seats": len(seats),
        "available_seats_count": len(available_seats),
        "booked_seats_count": len(booked_seats),
        "available_seats": available_seats,
        "booked_seats": booked_seats
    }