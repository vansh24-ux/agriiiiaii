from datetime import date

from app.core.database import SessionLocal
from app.models.crop import Crop
from app.models.mandi import Mandi
from app.models.price import Price


db = SessionLocal()

try:
    crop = (
        db.query(Crop)
        .filter(Crop.name.ilike("Wheat"))
        .first()
    )

    if not crop:
        raise RuntimeError("Wheat crop not found in database")

    # Demo prices for hackathon testing
    prices = {
        "Jalandhar Mandi": (2200, 2450, 2380),
        "Ludhiana Mandi": (2250, 2500, 2420),
        "Amritsar Mandi": (2150, 2400, 2320),
        "Patiala Mandi": (2180, 2430, 2360),
        "Khanna Mandi": (2300, 2550, 2480),
        "Ambala Mandi": (2200, 2470, 2390),
        "Karnal Mandi": (2250, 2520, 2440),
    }

    for mandi_name, price_values in prices.items():

        mandi = (
            db.query(Mandi)
            .filter(Mandi.name == mandi_name)
            .first()
        )

        if not mandi:
            print(f"Skipping {mandi_name} - mandi not found")
            continue

        min_price, max_price, modal_price = price_values

        existing = (
            db.query(Price)
            .filter(
                Price.crop_id == crop.id,
                Price.mandi_id == mandi.id
            )
            .first()
        )

        if existing:
            existing.min_price = min_price
            existing.max_price = max_price
            existing.modal_price = modal_price
            existing.date = date.today()
        else:
            db.add(
                Price(
                    crop_id=crop.id,
                    mandi_id=mandi.id,
                    min_price=min_price,
                    max_price=max_price,
                    modal_price=modal_price,
                    date=date.today()
                )
            )

    db.commit()

    print("Wheat prices seeded successfully.")

    total = (
        db.query(Price)
        .filter(Price.crop_id == crop.id)
        .count()
    )

    print(f"Total Wheat price records: {total}")

finally:
    db.close()