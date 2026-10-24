from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.mandi import Mandi
from app.services.distance_service import get_nearest_mandis


router = APIRouter(
    prefix="/mandis",
    tags=["Mandis"],
)


@router.get("/nearby")
def get_nearby_mandis(
    latitude: float = Query(...),
    longitude: float = Query(...),
    max_distance_km: float = Query(100, gt=0),
    db: Session = Depends(get_db),
):
    """
    Find mandis near the farmer's location.
    """

    mandis = db.query(Mandi).all()

    mandi_data = [
        {
            "id": mandi.id,
            "mandi": mandi.name,
            "city": mandi.city,
            "state": mandi.state,
            "latitude": mandi.latitude,
            "longitude": mandi.longitude,
        }
        for mandi in mandis
    ]

    nearby = get_nearest_mandis(
        mandi_data,
        latitude,
        longitude,
        max_distance_km,
    )

    return {
        "count": len(nearby),
        "farmer_location": {
            "latitude": latitude,
            "longitude": longitude,
        },
        "mandis": nearby,
    }