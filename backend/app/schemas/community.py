from pydantic import BaseModel, Field


class ProduceListingCreate(BaseModel):
    farmer_name: str = Field(min_length=1, max_length=80)
    crop: str = Field(min_length=1, max_length=80)
    quantity_quintals: float = Field(gt=0, le=1000000)
    location: str = Field(min_length=2, max_length=120)
    harvest_date: str | None = Field(default=None, max_length=20)
    details: str = Field(default="", max_length=1000)


class BuyerBidCreate(BaseModel):
    buyer_name: str = Field(min_length=1, max_length=80)
    price_per_quintal: float = Field(gt=0, le=10000000)
    message: str = Field(default="", max_length=1000)


class TransportRequestCreate(BaseModel):
    farmer_name: str = Field(min_length=1, max_length=80)
    crop: str = Field(min_length=1, max_length=80)
    quantity_quintals: float = Field(gt=0, le=1000000)
    pickup_location: str = Field(min_length=2, max_length=120)
    destination: str = Field(min_length=2, max_length=120)
    pickup_date: str | None = Field(default=None, max_length=20)


class PriceAlertCreate(BaseModel):
    farmer_name: str = Field(min_length=1, max_length=80)
    crop: str = Field(min_length=1, max_length=80)
    market: str = Field(default="Any nearby market", max_length=120)
    target_price: float = Field(gt=0, le=10000000)
    direction: str = Field(pattern="^(above|below)$")


class FpoEnquiryCreate(BaseModel):
    organization_name: str = Field(min_length=2, max_length=140)
    district: str = Field(min_length=2, max_length=120)
    member_count: int = Field(gt=0, le=1000000)
    submitted_by: str = Field(min_length=1, max_length=80)


class SponsorApplicationCreate(BaseModel):
    business_name: str = Field(min_length=2, max_length=140)
    offer_title: str = Field(min_length=2, max_length=140)
    category: str = Field(min_length=2, max_length=80)
    target_crop: str = Field(default="All crops", max_length=80)
    description: str = Field(min_length=5, max_length=1000)
    submitted_by: str = Field(min_length=1, max_length=80)


class TransportPartnerApplicationCreate(BaseModel):
    provider_name: str = Field(min_length=2, max_length=140)
    service_area: str = Field(min_length=2, max_length=120)
    vehicle_capacity_quintals: float = Field(gt=0, le=1000000)
    submitted_by: str = Field(min_length=1, max_length=80)
