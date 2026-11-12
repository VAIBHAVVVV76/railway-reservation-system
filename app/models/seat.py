
from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint

from app.database import Base


class Seat(Base):
    __tablename__ = "seats"
    __table_args__ = (
    UniqueConstraint(
        "train_id",
        "coach_number",
        "seat_number",
        name="uq_seats_train_coach_seat"
    ),
    )

    id = Column(Integer, primary_key=True, index=True)

    train_id = Column(Integer, ForeignKey("trains.id"), nullable=False)

    coach_number = Column(String(10), nullable=False)

    seat_number = Column(String(10), nullable=False)

    seat_class = Column(String(30), nullable=False)

    status = Column(String(20), default="available", nullable=False)
