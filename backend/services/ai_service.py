"""Generates a day-wise itinerary from real attraction data.

No paid LLM API is used — this is a deterministic planner that distributes
the fetched attractions across the trip's days and adds sensible packing
suggestions based on the weather forecast. It's structured so a real LLM
call could be swapped in later without changing the route/service contract.
"""


def generate_itinerary(destination_name, days, attractions, weather_forecast=None):
    days = max(1, int(days))
    itinerary = []

    if attractions:
        chunk_size = max(1, len(attractions) // days)
    else:
        chunk_size = 0

    for day_num in range(1, days + 1):
        start = (day_num - 1) * chunk_size
        end = start + chunk_size if day_num < days else len(attractions)
        day_attractions = attractions[start:end] if attractions else []

        activities = [f"Visit {a['name']}" for a in day_attractions[:4]]
        if not activities:
            activities = [f"Explore {destination_name} at your own pace", "Try local cuisine", "Relax and enjoy the surroundings"]

        weather_note = None
        if weather_forecast and day_num - 1 < len(weather_forecast):
            w = weather_forecast[day_num - 1]
            weather_note = f"{w['condition']}, {w['minTemp']}°C–{w['maxTemp']}°C, {w['rainChance']}% rain chance"

        itinerary.append({
            "day": day_num,
            "title": f"Day {day_num}: {'Highlights of ' + destination_name if day_num == 1 else 'Exploring ' + destination_name}",
            "activities": activities,
            "weather": weather_note,
        })

    packing = _packing_suggestions(weather_forecast)

    return {"itinerary": itinerary, "packingSuggestions": packing}


def _packing_suggestions(weather_forecast):
    suggestions = ["Comfortable walking shoes", "Reusable water bottle", "Phone charger / power bank", "Valid ID and travel documents"]
    if not weather_forecast:
        return suggestions

    max_temps = [d["maxTemp"] for d in weather_forecast]
    min_temps = [d["minTemp"] for d in weather_forecast]
    rain_chances = [d["rainChance"] for d in weather_forecast]

    if max(max_temps) > 30:
        suggestions.append("Lightweight, breathable clothing and sunscreen")
    if min(min_temps) < 12:
        suggestions.append("Warm jacket or layers for cooler evenings")
    if max(rain_chances) > 40:
        suggestions.append("Compact umbrella or rain jacket")

    return suggestions
