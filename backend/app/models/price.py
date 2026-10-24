from sqlalchemy import Column, Integer, Float, Date, ForeignKey
from app.core.database import Base


class Price(Base):
    __tablename__ = "prices"

    id = Column(Integer, primary_key=True, index=True)

    crop_id = Column(
        Integer,
        ForeignKey("crops.id"),
        nullable=False
    )

    mandi_id = Column(
        Integer,
        ForeignKey("mandis.id"),
        nullable=False
    )

    min_price = Column(Float, nullable=True)
    max_price = Column(Float, nullable=True)
    modal_price = Column(Float, nullable=False)

    date = Column(Date, nullable=False)