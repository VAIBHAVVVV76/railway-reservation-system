
from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Numeric
from sqlalchemy.sql import func

from app.database import Base


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)

    booking_reference = Column(String(20), unique=True, nullable=False)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    train_id = Column(Integer, ForeignKey("trains.id"), nullable=False)

    journey_date = Column(Date, nullable=False)

    number_of_seats = Column(Integer, nullable=False)

    total_amount = Column(Numeric(10, 2), nullable=False)

    status = Column(String(20), default="PENDING", nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
