
from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    DateTime,
    Date,
    UniqueConstraint
)
from sqlalchemy.sql import func

from app.database import Base


class Reservation(Base):
    __tablename__ = "reservations"

    __table_args__ = (
        UniqueConstraint(
            "seat_id",
            "journey_date",
            name="uq_reservations_seat_journey_date"
        ),
    )

    id = Column(Integer, primary_key=True, index=True)

    booking_id = Column(
        Integer,
        ForeignKey("bookings.id"),
        nullable=False
    )

    seat_id = Column(
        Integer,
        ForeignKey("seats.id"),
        nullable=False
    )

    journey_date = Column(Date, nullable=False)

    reserved_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )
