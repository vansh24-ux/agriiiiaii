from app.services.recommendation_service import generate_recommendation
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.crop import Crop
from app.models.mandi import Mandi
from app.models.price import Price
from app.services.mandi_services import get_live_mandi_prices
from app.services.distance_service import calculate_distance


router = APIRouter(
    prefix="/prices",
    tags=["Market information"]
)


# ---------------------------------------------------------
# LIVE GOVERNMENT MANDI PRICES
# ---------------------------------------------------------

@router.get("/live/{commodity}")
def get_live_prices(
    commodity: str,
    state: str | None = None,
    district: str | None = None,
):
    try:
        records = get_live_mandi_prices(
            commodity=commodity,
            state=state,
            district=district,
        )

        return {
            "commodity": commodity,
            "state": state,
            "district": district,
            "count": len(records),
            "records": records,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch live mandi data: {str(e)}"
        )


# ---------------------------------------------------------
# PRICE TREND / HISTORY
# ---------------------------------------------------------

@router.get("/trend/{crop_name}")
def get_price_trend(
    crop_name: str,
    mandi: str | None = None,
    db: Session = Depends(get_db)
):
    crop = (
        db.query(Crop)
        .filter(Crop.name.ilike(crop_name))
        .first()
    )

    if not crop:
        raise HTTPException(
            status_code=404,
            detail=f"Crop '{crop_name}' not found"
        )

    query = (
        db.query(Price, Mandi)
        .join(
            Mandi,
            Price.mandi_id == Mandi.id
        )
        .filter(
            Price.crop_id == crop.id
        )
    )

    # Optional mandi filter
    if mandi:
        query = query.filter(
            Mandi.name.ilike(mandi)
        )

    results = (
        query
        .order_by(Price.date.asc())
        .all()
    )

    if not results:
        raise HTTPException(
            status_code=404,
            detail=f"No price history found for {crop.name}"
        )

    # If no mandi was selected, return history grouped
    # by mandi.
    if mandi is None:

        mandi_history = {}

        for price, mandi_obj in results:

            if mandi_obj.name not in mandi_history:
                mandi_history[mandi_obj.name] = {
                    "mandi": mandi_obj.name,
                    "city": mandi_obj.city,
                    "state": mandi_obj.state,
                    "history": []
                }

            mandi_history[mandi_obj.name]["history"].append({
                "date": str(price.date),
                "modal_price": price.modal_price
            })

        # Calculate trend for every mandi
        for market in mandi_history.values():

            history = market["history"]

            if len(history) < 2:
                market["trend"] = "Stable"
            else:
                first_price = history[0]["modal_price"]
                last_price = history[-1]["modal_price"]

                if last_price > first_price:
                    market["trend"] = "Rising"
                elif last_price < first_price:
                    market["trend"] = "Falling"
                else:
                    market["trend"] = "Stable"

            market["current_price"] = history[-1]["modal_price"]

        return {
            "crop": crop.name,
            "mandis": list(mandi_history.values())
        }

    # -----------------------------------------------------
    # SINGLE MANDI HISTORY
    # -----------------------------------------------------

    history = []

    for price, mandi_obj in results:

        history.append({
            "date": str(price.date),
            "modal_price": price.modal_price
        })

    first_price = history[0]["modal_price"]
    last_price = history[-1]["modal_price"]

    if len(history) < 2:
        trend = "Stable"
    elif last_price > first_price:
        trend = "Rising"
    elif last_price < first_price:
        trend = "Falling"
    else:
        trend = "Stable"

    return {
        "crop": crop.name,
        "mandi": mandi_obj.name,
        "city": mandi_obj.city,
        "state": mandi_obj.state,
        "current_price": last_price,
        "trend": trend,
        "history": history
    }


# ---------------------------------------------------------
# MARKET PRICE LOOKUP
# ---------------------------------------------------------

@router.get("/{crop_name}")
def get_market_prices(
    crop_name: str,
    db: Session = Depends(get_db)
):
    crop = (
        db.query(Crop)
        .filter(Crop.name.ilike(crop_name))
        .first()
    )

    if not crop:
        raise HTTPException(
            status_code=404,
            detail=f"Crop '{crop_name}' not found"
        )

    results = (
        db.query(Price, Mandi)
        .join(
            Mandi,
            Price.mandi_id == Mandi.id
        )
        .filter(
            Price.crop_id == crop.id
        )
        .all()
    )

    if not results:
        raise HTTPException(
            status_code=404,
            detail=f"No prices found for {crop.name}"
        )

    mandis = []

    for price, mandi in results:

        mandis.append({
            "mandi": mandi.name,
            "city": mandi.city,
            "state": mandi.state,
            "min_price": price.min_price,
            "max_price": price.max_price,
            "modal_price": price.modal_price,
            "date": str(price.date)
        })

    best_mandi = max(
        mandis,
        key=lambda x: x["modal_price"]
    )

    best_price = best_mandi["modal_price"]

    for mandi in mandis:

        mandi["price_difference"] = round(
            best_price - mandi["modal_price"],
            2
        )

    recommendation = (
        f"Sell at {best_mandi['mandi']} for the highest modal "
        f"price of ₹{best_price}/quintal."
    )

    return {
        "crop": crop.name,
        "variety": crop.variety,
        "best_mandi": best_mandi,
        "recommendation": recommendation,
        "all_mandis": mandis
    }


# ---------------------------------------------------------
# NEARBY MANDIS + PRICE + TRANSPORT-AWARE NET EARNING
# ---------------------------------------------------------

@router.get("/nearby/{crop_name}")
def get_nearby_market_prices(
    crop_name: str,
    latitude: float,
    longitude: float,
    max_distance_km: float = 100,
    quantity: float = 10,
    db: Session = Depends(get_db)
):
    crop = (
        db.query(Crop)
        .filter(Crop.name.ilike(crop_name))
        .first()
    )

    if not crop:
        raise HTTPException(
            status_code=404,
            detail=f"Crop '{crop_name}' not found"
        )

    if quantity <= 0:
        raise HTTPException(
            status_code=400,
            detail="Quantity must be greater than 0."
        )

    if max_distance_km <= 0:
        raise HTTPException(
            status_code=400,
            detail="Maximum distance must be greater than 0."
        )

    results = (
        db.query(Price, Mandi)
        .join(
            Mandi,
            Price.mandi_id == Mandi.id
        )
        .filter(
            Price.crop_id == crop.id
        )
        .all()
    )

    nearby_markets = []

    # Estimated transport cost:
    # ₹20 per km per quintal
    TRANSPORT_RATE = 20

    for price, mandi in results:

        if mandi.latitude is None or mandi.longitude is None:
            continue

        distance = calculate_distance(
            latitude,
            longitude,
            mandi.latitude,
            mandi.longitude,
        )

        if distance <= max_distance_km:

            transport_cost = (
                distance *
                TRANSPORT_RATE *
                quantity
            )

            gross_earning = (
                price.modal_price *
                quantity
            )

            net_earning = (
                gross_earning -
                transport_cost
            )

            nearby_markets.append({
                "mandi": mandi.name,
                "city": mandi.city,
                "state": mandi.state,

                "latitude": mandi.latitude,
                "longitude": mandi.longitude,

                "distance_km": round(
                    distance,
                    2
                ),

                "min_price": price.min_price,
                "max_price": price.max_price,
                "modal_price": price.modal_price,

                "date": str(price.date),

                "quantity": quantity,

                "transport_cost": round(
                    transport_cost,
                    2
                ),

                "gross_earning": round(
                    gross_earning,
                    2
                ),

                "net_earning": round(
                    net_earning,
                    2
                ),
            })

    if not nearby_markets:

        return {
            "crop": crop.name,
            "count": 0,
            "message": "No markets found within the selected distance.",
            "markets": [],
        }

    # Highest market price
    highest_price = max(
        market["modal_price"]
        for market in nearby_markets
    )

    # Price difference
    for market in nearby_markets:

        market["price_difference"] = round(
            highest_price -
            market["modal_price"],
            2
        )

    # Best market based on NET EARNING
    best_market = max(
        nearby_markets,
        key=lambda market:
        market["net_earning"]
    )

    # Recommendation based on net earning
    recommendation = generate_recommendation(
        nearby_markets
    )

    return {
        "crop": crop.name,

        "count": len(
            nearby_markets
        ),

        "farmer_location": {
            "latitude": latitude,
            "longitude": longitude,
        },

        "quantity": quantity,

        "transport_rate_per_km_per_quintal":
            TRANSPORT_RATE,

        "best_market": best_market,

        "recommendation":
            recommendation,

        "markets": sorted(
            nearby_markets,
            key=lambda market:
            market["distance_km"]
        ),
    }