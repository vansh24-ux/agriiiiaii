def generate_recommendation(markets):
    """
    Generate a farmer-friendly recommendation
    based on net earning after transport costs.
    """

    if not markets:
        return {
            "recommended_mandi": None,
            "reason": "No nearby markets found."
        }

    # Best market = highest net earning
    best_market = max(
        markets,
        key=lambda market: market["net_earning"]
    )

    # Nearest market
    nearest_market = min(
        markets,
        key=lambda market: market["distance_km"]
    )

    # Best option is also the nearest
    if best_market["mandi"] == nearest_market["mandi"]:
        return {
            "recommended_mandi": best_market["mandi"],
            "reason": (
                f"{best_market['mandi']} is the nearest market "
                f"({best_market['distance_km']} km) and gives the "
                f"highest estimated net earning of "
                f"₹{best_market['net_earning']} after transport."
            )
        }

    net_difference = (
        best_market["net_earning"]
        - nearest_market["net_earning"]
    )

    distance_difference = (
        best_market["distance_km"]
        - nearest_market["distance_km"]
    )

    return {
        "recommended_mandi": best_market["mandi"],
        "reason": (
            f"{best_market['mandi']} gives the highest estimated "
            f"net earning of ₹{best_market['net_earning']} after "
            f"transport. This is approximately ₹{net_difference:.2f} "
            f"more than {nearest_market['mandi']}. It is approximately "
            f"{distance_difference:.2f} km farther away."
        )
    }