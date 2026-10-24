from app.core.database import SessionLocal
from app.models.mandi import Mandi


mandis = [
    {
        "name": "Jalandhar Mandi",
        "city": "Jalandhar",
        "state": "Punjab",
        "latitude": 31.3260,
        "longitude": 75.5762,
    },
    {
        "name": "Ludhiana Mandi",
        "city": "Ludhiana",
        "state": "Punjab",
        "latitude": 30.9010,
        "longitude": 75.8573,
    },
    {
        "name": "Amritsar Mandi",
        "city": "Amritsar",
        "state": "Punjab",
        "latitude": 31.6340,
        "longitude": 74.8723,
    },
    {
        "name": "Patiala Mandi",
        "city": "Patiala",
        "state": "Punjab",
        "latitude": 30.3398,
        "longitude": 76.3869,
    },
    {
        "name": "Khanna Mandi",
        "city": "Khanna",
        "state": "Punjab",
        "latitude": 30.7055,
        "longitude": 76.2219,
    },
    {
        "name": "Ambala Mandi",
        "city": "Ambala",
        "state": "Haryana",
        "latitude": 30.3782,
        "longitude": 76.7767,
    },
    {
        "name": "Karnal Mandi",
        "city": "Karnal",
        "state": "Haryana",
        "latitude": 29.6857,
        "longitude": 76.9905,
    },
    {
        "name": "Azadpur Mandi",
        "city": "Delhi",
        "state": "Delhi",
        "latitude": 28.7041,
        "longitude": 77.1025,
    },
    {
        "name": "Ghazipur Mandi",
        "city": "Delhi",
        "state": "Delhi",
        "latitude": 28.6271,
        "longitude": 77.2870,
    },
    {
        "name": "Okhla Mandi",
        "city": "Delhi",
        "state": "Delhi",
        "latitude": 28.5355,
        "longitude": 77.2640,
    },
]


db = SessionLocal()

try:
    for data in mandis:
        existing = (
            db.query(Mandi)
            .filter(Mandi.name == data["name"])
            .first()
        )

        if existing:
            existing.city = data["city"]
            existing.state = data["state"]
            existing.latitude = data["latitude"]
            existing.longitude = data["longitude"]
        else:
            db.add(Mandi(**data))

    db.commit()

    print("Mandi data seeded successfully.")

    total = db.query(Mandi).count()
    print(f"Total mandis in database: {total}")

finally:
    db.close()