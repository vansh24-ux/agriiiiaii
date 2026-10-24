from datetime import date

from app.core.database import Base, SessionLocal, engine
from app.models.crop import Crop
from app.models.mandi import Mandi
from app.models.price import Price


# Create tables if they do not exist
Base.metadata.create_all(bind=engine)

db = SessionLocal()


try:
    # Clear existing demo data
    db.query(Price).delete()
    db.query(Mandi).delete()
    db.query(Crop).delete()

    # -------------------------
    # CROPS
    # -------------------------
    crops = [
        Crop(name="Wheat", variety="Lokwan"),
        Crop(name="Rice", variety="Basmati"),
        Crop(name="Mustard", variety="Yellow Mustard"),
        Crop(name="Potato", variety="Local"),
        Crop(name="Onion", variety="Red Onion"),
    ]

    db.add_all(crops)
    db.commit()

    # -------------------------
    # MANDIS
    # -------------------------
    mandis = [
        Mandi(
            name="Azadpur Mandi",
            city="Delhi",
            state="Delhi",
            latitude=28.7041,
            longitude=77.1025,
        ),
        Mandi(
            name="Ghazipur Mandi",
            city="Delhi",
            state="Delhi",
            latitude=28.6271,
            longitude=77.2870,
        ),
        Mandi(
            name="Okhla Mandi",
            city="Delhi",
            state="Delhi",
            latitude=28.5355,
            longitude=77.2640,
        ),
    ]

    db.add_all(mandis)
    db.commit()

    # Refresh objects to get their IDs
    for crop in crops:
        db.refresh(crop)

    for mandi in mandis:
        db.refresh(mandi)

    # -------------------------
    # PRICES
    # -------------------------
    prices = [
        # Wheat
        Price(
            crop_id=crops[0].id,
            mandi_id=mandis[0].id,
            min_price=2200,
            max_price=2450,
            modal_price=2350,
            date=date.today(),
        ),
        Price(
            crop_id=crops[0].id,
            mandi_id=mandis[1].id,
            min_price=2150,
            max_price=2400,
            modal_price=2300,
            date=date.today(),
        ),
        Price(
            crop_id=crops[0].id,
            mandi_id=mandis[2].id,
            min_price=2250,
            max_price=2500,
            modal_price=2420,
            date=date.today(),
        ),

        # Rice
        Price(
            crop_id=crops[1].id,
            mandi_id=mandis[0].id,
            min_price=3000,
            max_price=3400,
            modal_price=3250,
            date=date.today(),
        ),
        Price(
            crop_id=crops[1].id,
            mandi_id=mandis[1].id,
            min_price=2900,
            max_price=3300,
            modal_price=3150,
            date=date.today(),
        ),

        # Mustard
        Price(
            crop_id=crops[2].id,
            mandi_id=mandis[0].id,
            min_price=5600,
            max_price=6100,
            modal_price=5900,
            date=date.today(),
        ),
        Price(
            crop_id=crops[2].id,
            mandi_id=mandis[1].id,
            min_price=5500,
            max_price=6000,
            modal_price=5800,
            date=date.today(),
        ),

        # Potato
        Price(
            crop_id=crops[3].id,
            mandi_id=mandis[0].id,
            min_price=1200,
            max_price=1700,
            modal_price=1500,
            date=date.today(),
        ),
        Price(
            crop_id=crops[3].id,
            mandi_id=mandis[2].id,
            min_price=1300,
            max_price=1800,
            modal_price=1600,
            date=date.today(),
        ),

        # Onion
        Price(
            crop_id=crops[4].id,
            mandi_id=mandis[0].id,
            min_price=1800,
            max_price=2400,
            modal_price=2150,
            date=date.today(),
        ),
        Price(
            crop_id=crops[4].id,
            mandi_id=mandis[1].id,
            min_price=1700,
            max_price=2300,
            modal_price=2050,
            date=date.today(),
        ),
    ]

    db.add_all(prices)
    db.commit()

    print("✅ Database seeded successfully!")
    print(f"🌾 Crops added: {len(crops)}")
    print(f"🏪 Mandis added: {len(mandis)}")
    print(f"💰 Prices added: {len(prices)}")

finally:
    db.close()