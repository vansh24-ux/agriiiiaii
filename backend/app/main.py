from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.prices import router as prices_router
from app.api.community import router as community_router
from app.api.routers.mandis import router as mandis_router
from app.core.database import Base, engine
from app.models.crop import Crop
from app.models.mandi import Mandi
from app.models.price import Price
from app.models.community import BuyerBid, FarmerPriceAlert, FpoEnquiry, ProduceListing, SponsorApplication, SponsoredOffer, TransportRequest, TransportPartnerApplication


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="KisanWeb Farmer Services API",
    description="Farmer services for market prices, buyer offers, transport requests, price alerts and FPO tools.",
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(prices_router)
app.include_router(mandis_router)
app.include_router(community_router)

@app.get("/")
def root():
    return {
        "message": "KisanWeb Farmer Services API is running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }
