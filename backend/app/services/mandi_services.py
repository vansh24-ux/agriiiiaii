import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("DATA_GOV_API_KEY")

BASE_URL = (
    "https://api.data.gov.in/resource/"
    "9ef84268-d588-465a-a308-a864a43d0070"
)


def get_live_mandi_prices(
    commodity: str,
    state: str | None = None,
    district: str | None = None,
    limit: int = 50,
):
    if not API_KEY:
        raise RuntimeError("DATA_GOV_API_KEY is not configured")

    params = {
        "api-key": API_KEY,
        "format": "json",
        "limit": limit,
        "filters[commodity]": commodity,
    }

    if state:
        params["filters[state.keyword]"] = state

    if district:
        params["filters[district]"] = district

    session = requests.Session()
    session.trust_env = False

    response = session.get(
        BASE_URL,
        params=params,
        headers={
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json",
            "Connection": "close",
        },
        timeout=(10, 30),
    )

    response.raise_for_status()

    data = response.json()

    return data.get("records", [])