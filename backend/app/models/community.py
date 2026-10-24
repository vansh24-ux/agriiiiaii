from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text

from app.core.database import Base


class ProduceListing(Base):
    __tablename__ = "produce_listings"

    id = Column(Integer, primary_key=True, index=True)
    farmer_name = Column(String(80), nullable=False, index=True)
    crop = Column(String(80), nullable=False, index=True)
    quantity_quintals = Column(Float, nullable=False)
    location = Column(String(120), nullable=False)
    harvest_date = Column(String(20), nullable=True)
    details = Column(Text, nullable=False, default="")
    is_open = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class BuyerBid(Base):
    __tablename__ = "buyer_bids"

    id = Column(Integer, primary_key=True, index=True)
    listing_id = Column(Integer, ForeignKey("produce_listings.id"), nullable=False, index=True)
    buyer_name = Column(String(80), nullable=False)
    price_per_quintal = Column(Float, nullable=False)
    message = Column(Text, nullable=False, default="")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class TransportRequest(Base):
    __tablename__ = "transport_requests"

    id = Column(Integer, primary_key=True, index=True)
    farmer_name = Column(String(80), nullable=False, index=True)
    crop = Column(String(80), nullable=False)
    quantity_quintals = Column(Float, nullable=False)
    pickup_location = Column(String(120), nullable=False)
    destination = Column(String(120), nullable=False)
    pickup_date = Column(String(20), nullable=True)
    status = Column(String(30), nullable=False, default="pending")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class FarmerPriceAlert(Base):
    __tablename__ = "farmer_price_alerts"

    id = Column(Integer, primary_key=True, index=True)
    farmer_name = Column(String(80), nullable=False, index=True)
    crop = Column(String(80), nullable=False, index=True)
    market = Column(String(120), nullable=False, default="Any nearby market")
    target_price = Column(Float, nullable=False)
    direction = Column(String(10), nullable=False, default="above")
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class FpoEnquiry(Base):
    __tablename__ = "fpo_enquiries"

    id = Column(Integer, primary_key=True, index=True)
    organization_name = Column(String(140), nullable=False)
    district = Column(String(120), nullable=False)
    member_count = Column(Integer, nullable=False)
    submitted_by = Column(String(80), nullable=False)
    status = Column(String(30), nullable=False, default="demo_requested")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class SponsorApplication(Base):
    __tablename__ = "sponsor_applications"

    id = Column(Integer, primary_key=True, index=True)
    business_name = Column(String(140), nullable=False)
    offer_title = Column(String(140), nullable=False)
    category = Column(String(80), nullable=False)
    target_crop = Column(String(80), nullable=False, default="All crops")
    description = Column(Text, nullable=False)
    submitted_by = Column(String(80), nullable=False)
    status = Column(String(30), nullable=False, default="pending_review")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class SponsoredOffer(Base):
    __tablename__ = "sponsored_offers"

    id = Column(Integer, primary_key=True, index=True)
    business_name = Column(String(140), nullable=False)
    offer_title = Column(String(140), nullable=False)
    category = Column(String(80), nullable=False)
    target_crop = Column(String(80), nullable=False, default="All crops")
    description = Column(Text, nullable=False)
    is_active = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class TransportPartnerApplication(Base):
    __tablename__ = "transport_partner_applications"

    id = Column(Integer, primary_key=True, index=True)
    provider_name = Column(String(140), nullable=False)
    service_area = Column(String(120), nullable=False)
    vehicle_capacity_quintals = Column(Float, nullable=False)
    submitted_by = Column(String(80), nullable=False)
    status = Column(String(30), nullable=False, default="pending_review")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
