from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.train import Train
from app.models.seat import Seat
from app.models.booking import Booking
from app.models.reservation import Reservation
from app.schemas.booking import BookingCreate

router = APIRouter(
    prefix="/bookings",
    tags=["Bookings"]
)


@router.post("/")
def create_booking(
    request: BookingCreate,
    db: Session = Depends(get_db)
):
    try:
        # 1. Check passenger
        user = db.query(User).filter(
            User.id == request.user_id
        ).first()

        if not user:
            raise HTTPException(
                status_code=404,
                detail="Passenger not found"
            )

        # 2. Check train
        train = db.query(Train).filter(
            Train.id == request.train_id
        ).first()

        if not train:
            raise HTTPException(
                status_code=404,
                detail="Train not found"
            )

        # 3. Lock this train's seat rows
        seats = (
            db.query(Seat)
            .filter(
                Seat.train_id == request.train_id,
                Seat.status == "available"
            )
            .order_by(Seat.id)
            .with_for_update()
            .all()
        )

        # 4. Find seats already reserved for this date
        seat_ids = [seat.id for seat in seats]

        reserved_ids = set(
            row[0] for row in
            db.query(Reservation.seat_id)
            .filter(
                Reservation.seat_id.in_(seat_ids),
                Reservation.journey_date == request.journey_date
            )
            .all()
        ) if seat_ids else set()

        # Identify seats not yet reserved for that journey date
        available_seats = [s for s in seats if s.id not in reserved_ids]

        # 5. Check availability
        if len(available_seats) < request.number_of_seats:
            raise HTTPException(
                status_code=409,
                detail="Not enough seats available"
            )

        selected_seats = available_seats[:request.number_of_seats]

        # 6. Calculate fare
        total_amount = (
            train.fare_per_seat * request.number_of_seats
        )

        # 7. Create booking
        booking = Booking(
            booking_reference=uuid4().hex[:12].upper(),
            user_id=request.user_id,
            train_id=request.train_id,
            journey_date=request.journey_date,
            number_of_seats=request.number_of_seats,
            total_amount=total_amount,
            status="CONFIRMED"
        )

        db.add(booking)
        db.flush()

        # 8. Reserve selected seats
        for seat in selected_seats:
            reservation = Reservation(
                booking_id=booking.id,
                seat_id=seat.id,
                journey_date=request.journey_date
            )
            db.add(reservation)

        # 9. Save everything together
        db.commit()
        db.refresh(booking)

        return {
            "message": "Booking successful",
            "booking_reference": booking.booking_reference,
            "booking_id": booking.id,
            "train": train.train_name,
            "journey_date": str(booking.journey_date),
            "number_of_seats": booking.number_of_seats,
            "total_amount": float(booking.total_amount),
            "status": booking.status,
            "allocated_seats": [
                {
                    "coach": seat.coach_number,
                    "seat_number": seat.seat_number
                }
                for seat in selected_seats
            ]
        }

    except HTTPException:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        raise


@router.get("/{booking_id}")
def get_booking_details(
    booking_id: int,
    db: Session = Depends(get_db)
):
    # 1. Fetch booking
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    # 2. Fetch associated user and train
    user = db.query(User).filter(User.id == booking.user_id).first()
    train = db.query(Train).filter(Train.id == booking.train_id).first()

    # 3. Fetch allocated seats via reservations
    reservations = (
        db.query(Reservation, Seat)
        .join(Seat, Reservation.seat_id == Seat.id)
        .filter(Reservation.booking_id == booking.id)
        .all()
    )

    allocated_seats = [
        {
            "coach": seat.coach_number,
            "seat_number": seat.seat_number,
            "seat_class": seat.seat_class
        }
        for _, seat in reservations
    ]

    return {
        "booking_id": booking.id,
        "booking_reference": booking.booking_reference,
        "status": booking.status,
        "journey_date": str(booking.journey_date),
        "number_of_seats": booking.number_of_seats,
        "total_amount": float(booking.total_amount),
        "passenger": {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "phone": user.phone
        } if user else None,
        "train": {
            "id": train.id,
            "train_number": train.train_number,
            "train_name": train.train_name
        } if train else None,
        "allocated_seats": allocated_seats,
        "created_at": str(booking.created_at) if hasattr(booking, "created_at") else None
    }