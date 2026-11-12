from sqlalchemy import Column, Integer, String, Numeric, ForeignKey
from app.database import Base


class Train(Base):
    __tablename__ = "trains"

    id = Column(Integer, primary_key=True, index=True)
    train_number = Column(String(20), unique=True, nullable=False)
    train_name = Column(String(100), nullable=False)
    source_station_id = Column(Integer, ForeignKey("stations.id"), nullable=False)
    destination_station_id = Column(Integer, ForeignKey("stations.id"), nullable=False)
    total_seats = Column(Integer, nullable=False)
    fare_per_seat = Column(Numeric(10, 2), nullable=False)