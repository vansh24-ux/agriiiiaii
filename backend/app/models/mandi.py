from sqlalchemy import Column, Integer, String, Float
from app.core.database import Base


class Mandi(Base):
    __tablename__ = "mandis"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    city = Column(String, nullable=False)
    state = Column(String, nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)