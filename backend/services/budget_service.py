# Per-person, per-day baseline costs (in generic currency units / USD-equivalent).
# These are heuristic estimates, not live pricing data.
PREFERENCE_MULTIPLIERS = {
    "budget": 0.7,
    "standard": 1.0,
    "luxury": 1.8,
}

BASE_HOTEL_PER_NIGHT = 40
BASE_FOOD_PER_DAY = 20
BASE_LOCAL_TRANSPORT_PER_DAY = 8
BASE_ENTRY_FEES_PER_DAY = 10


def estimate_budget(people, days, preference, distance_km=0):
    multiplier = PREFERENCE_MULTIPLIERS.get(preference, 1.0)

    travel_cost = round(distance_km * 0.08 * people, 2)  # rough per-km fuel/fare estimate
    hotel_cost = round(BASE_HOTEL_PER_NIGHT * multiplier * days * max(1, people // 2), 2)
    food_cost = round(BASE_FOOD_PER_DAY * multiplier * days * people, 2)
    local_transport = round(BASE_LOCAL_TRANSPORT_PER_DAY * multiplier * days * people, 2)
    entry_fees = round(BASE_ENTRY_FEES_PER_DAY * multiplier * days * people, 2)

    total = round(travel_cost + hotel_cost + food_cost + local_transport + entry_fees, 2)

    return {
        "travelCost": travel_cost,
        "hotelCost": hotel_cost,
        "foodCost": food_cost,
        "localTransport": local_transport,
        "entryFees": entry_fees,
        "totalEstimatedBudget": total,
        "currency": "USD",
        "note": "Estimated costs based on typical averages; actual prices vary by season and provider.",
    }
