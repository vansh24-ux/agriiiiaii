from math import radians, sin, cos, sqrt, atan2


def calculate_distance(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float,
) -> float:
    """
    Calculate the distance between two points
    using the Haversine formula.

    Returns:
        Distance in kilometers.
    """

    earth_radius = 6371.0

    lat1_rad = radians(lat1)
    lat2_rad = radians(lat2)

    delta_lat = radians(lat2 - lat1)
    delta_lon = radians(lon2 - lon1)

    a = (
        sin(delta_lat / 2) ** 2
        + cos(lat1_rad)
        * cos(lat2_rad)
        * sin(delta_lon / 2) ** 2
    )

    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return round(earth_radius * c, 2)


def add_distance_to_mandis(
    mandis: list[dict],
    latitude: float,
    longitude: float,
) -> list[dict]:
    """
    Add distance from the farmer's location
    to each mandi.

    Each mandi must contain:
        latitude
        longitude
    """

    results = []

    for mandi in mandis:
        mandi_lat = mandi.get("latitude")
        mandi_lon = mandi.get("longitude")

        if mandi_lat is None or mandi_lon is None:
            continue

        distance = calculate_distance(
            latitude,
            longitude,
            float(mandi_lat),
            float(mandi_lon),
        )

        mandi_with_distance = dict(mandi)
        mandi_with_distance["distance_km"] = distance

        results.append(mandi_with_distance)

    return sorted(
        results,
        key=lambda mandi: mandi["distance_km"],
    )


def get_nearest_mandis(
    mandis: list[dict],
    latitude: float,
    longitude: float,
    max_distance_km: float = 100,
) -> list[dict]:
    """
    Return mandis within the specified radius,
    sorted from nearest to farthest.
    """

    mandis_with_distance = add_distance_to_mandis(
        mandis,
        latitude,
        longitude,
    )

    return [
        mandi
        for mandi in mandis_with_distance
        if mandi["distance_km"] <= max_distance_km
    ]