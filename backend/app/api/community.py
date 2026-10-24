from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.community import (
    BuyerBid,
    FarmerPriceAlert,
    FpoEnquiry,
    ProduceListing,
    SponsorApplication,
    SponsoredOffer,
    TransportRequest,
    TransportPartnerApplication,
)
from app.schemas.community import (
    BuyerBidCreate,
    FpoEnquiryCreate,
    PriceAlertCreate,
    ProduceListingCreate,
    SponsorApplicationCreate,
    TransportRequestCreate,
    TransportPartnerApplicationCreate,
)


router = APIRouter(prefix="/community", tags=["Farmer services"])


def listing_payload(db: Session, listing: ProduceListing) -> dict:
    bids = db.query(BuyerBid).filter(BuyerBid.listing_id == listing.id).order_by(BuyerBid.created_at.desc()).all()
    return {
        "id": listing.id,
        "farmer_name": listing.farmer_name,
        "crop": listing.crop,
        "quantity_quintals": listing.quantity_quintals,
        "location": listing.location,
        "harvest_date": listing.harvest_date,
        "details": listing.details,
        "is_open": listing.is_open,
        "created_at": listing.created_at.isoformat(),
        "offers": [{
            "id": bid.id,
            "buyer_name": bid.buyer_name,
            "price_per_quintal": bid.price_per_quintal,
            "message": bid.message,
            "created_at": bid.created_at.isoformat(),
        } for bid in bids],
    }


@router.get("/listings")
def get_produce_listings(
    farmer_name: str | None = Query(default=None, max_length=80),
    db: Session = Depends(get_db),
):
    query = db.query(ProduceListing).filter(ProduceListing.is_open.is_(True))
    if farmer_name:
        query = query.filter(ProduceListing.farmer_name != farmer_name)
    rows = query.order_by(ProduceListing.created_at.desc()).limit(100).all()
    return {"listings": [listing_payload(db, row) for row in rows]}


@router.post("/listings", status_code=201)
def create_produce_listing(payload: ProduceListingCreate, db: Session = Depends(get_db)):
    listing = ProduceListing(**payload.model_dump())
    db.add(listing)
    db.commit()
    db.refresh(listing)
    return listing_payload(db, listing)


@router.post("/listings/{listing_id}/offers", status_code=201)
def create_buyer_offer(listing_id: int, payload: BuyerBidCreate, db: Session = Depends(get_db)):
    listing = db.query(ProduceListing).filter(ProduceListing.id == listing_id, ProduceListing.is_open.is_(True)).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Produce listing not found")
    if listing.farmer_name.casefold() == payload.buyer_name.strip().casefold():
        raise HTTPException(status_code=400, detail="You cannot bid on your own listing")
    bid = BuyerBid(listing_id=listing_id, **payload.model_dump())
    db.add(bid)
    db.commit()
    db.refresh(bid)
    return {"id": bid.id, "listing_id": bid.listing_id, "buyer_name": bid.buyer_name, "price_per_quintal": bid.price_per_quintal, "message": bid.message}


@router.get("/transport-requests")
def get_transport_requests(
    farmer_name: str = Query(min_length=1, max_length=80),
    db: Session = Depends(get_db),
):
    rows = db.query(TransportRequest).filter(TransportRequest.farmer_name == farmer_name).order_by(TransportRequest.created_at.desc()).limit(100).all()
    return {"requests": [{
        "id": row.id,
        "crop": row.crop,
        "quantity_quintals": row.quantity_quintals,
        "pickup_location": row.pickup_location,
        "destination": row.destination,
        "pickup_date": row.pickup_date,
        "status": row.status,
        "created_at": row.created_at.isoformat(),
    } for row in rows]}


@router.post("/transport-requests", status_code=201)
def create_transport_request(payload: TransportRequestCreate, db: Session = Depends(get_db)):
    request = TransportRequest(**payload.model_dump())
    db.add(request)
    db.commit()
    db.refresh(request)
    return {"id": request.id, "status": request.status}


@router.get("/price-alerts")
def get_price_alerts(
    farmer_name: str = Query(min_length=1, max_length=80),
    db: Session = Depends(get_db),
):
    rows = db.query(FarmerPriceAlert).filter(FarmerPriceAlert.farmer_name == farmer_name, FarmerPriceAlert.is_active.is_(True)).order_by(FarmerPriceAlert.created_at.desc()).all()
    return {"alerts": [{
        "id": row.id,
        "crop": row.crop,
        "market": row.market,
        "target_price": row.target_price,
        "direction": row.direction,
    } for row in rows]}


@router.post("/price-alerts", status_code=201)
def create_price_alert(payload: PriceAlertCreate, db: Session = Depends(get_db)):
    alert = FarmerPriceAlert(**payload.model_dump())
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return {"id": alert.id, "crop": alert.crop, "market": alert.market, "target_price": alert.target_price, "direction": alert.direction}


@router.delete("/price-alerts/{alert_id}")
def delete_price_alert(
    alert_id: int,
    farmer_name: str = Query(min_length=1, max_length=80),
    db: Session = Depends(get_db),
):
    alert = db.query(FarmerPriceAlert).filter(FarmerPriceAlert.id == alert_id, FarmerPriceAlert.farmer_name == farmer_name).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Price alert not found")
    alert.is_active = False
    db.commit()
    return {"deleted": True}


@router.get("/fpo/summary")
def get_fpo_summary(db: Session = Depends(get_db)):
    listing_count, total_quintals = db.query(
        func.count(ProduceListing.id), func.coalesce(func.sum(ProduceListing.quantity_quintals), 0)
    ).filter(ProduceListing.is_open.is_(True)).one()
    bid_count = db.query(func.count(BuyerBid.id)).scalar() or 0
    return {"open_listings": listing_count or 0, "available_quintals": float(total_quintals or 0), "buyer_offers": bid_count}


@router.post("/fpo/enquiries", status_code=201)
def create_fpo_enquiry(payload: FpoEnquiryCreate, db: Session = Depends(get_db)):
    enquiry = FpoEnquiry(**payload.model_dump())
    db.add(enquiry)
    db.commit()
    db.refresh(enquiry)
    return {"id": enquiry.id, "status": enquiry.status}


@router.get("/sponsored-offers")
def get_sponsored_offers(db: Session = Depends(get_db)):
    rows = db.query(SponsoredOffer).filter(SponsoredOffer.is_active.is_(True)).order_by(SponsoredOffer.created_at.desc()).limit(50).all()
    return {"offers": [{
        "id": row.id,
        "business_name": row.business_name,
        "offer_title": row.offer_title,
        "category": row.category,
        "target_crop": row.target_crop,
        "description": row.description,
    } for row in rows]}


@router.post("/sponsored-offers/applications", status_code=201)
def create_sponsor_application(payload: SponsorApplicationCreate, db: Session = Depends(get_db)):
    application = SponsorApplication(**payload.model_dump())
    db.add(application)
    db.commit()
    db.refresh(application)
    return {"id": application.id, "status": application.status}


@router.post("/transport-partners/applications", status_code=201)
def create_transport_partner_application(payload: TransportPartnerApplicationCreate, db: Session = Depends(get_db)):
    application = TransportPartnerApplication(**payload.model_dump())
    db.add(application)
    db.commit()
    db.refresh(application)
    return {"id": application.id, "status": application.status}
