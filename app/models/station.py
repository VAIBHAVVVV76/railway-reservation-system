
from sqlalchemy import Column, Integer, String

from app.database import Base


class Station(Base):
    __tablename__ = "stations"

    id = Column(Integer, primary_key=True, index=True)

    station_code = Column(String(10), unique=True, nullable=False, index=True)

    station_name = Column(String(100), nullable=False)

    city = Column(String(100), nullable=False)

    state = Column(String(100), nullable=False)
