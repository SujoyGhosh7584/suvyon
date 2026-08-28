import json

import httpx

_HEADERS = {"User-Agent": "Suvyon/1.0 (world tools; https://github.com)"}


def weather(location: str) -> str:
    """Current conditions and 3-day forecast via Open-Meteo (free, no key)."""
    place = (location or "").strip()
    if not place:
        return "Tool error: weather requires a city or place name."
    try:
        geo = httpx.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": place, "count": 1, "language": "en", "format": "json"},
            headers=_HEADERS,
            timeout=12,
        )
        geo.raise_for_status()
        results = geo.json().get("results") or []
        if not results:
            return f"Could not find a location named “{place}”."
        spot = results[0]
        lat, lon = spot["latitude"], spot["longitude"]
        label = ", ".join(
            part
            for part in [spot.get("name"), spot.get("admin1"), spot.get("country")]
            if part
        )
        forecast = httpx.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": lat,
                "longitude": lon,
                "current_weather": True,
                "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
                "timezone": "auto",
                "forecast_days": 3,
            },
            headers=_HEADERS,
            timeout=12,
        )
        forecast.raise_for_status()
        data = forecast.json()
        current = data.get("current_weather") or {}
        daily = data.get("daily") or {}
        lines = [
            f"Weather for {label} ({lat:.2f}, {lon:.2f})",
            f"Now: {current.get('temperature')}°C, wind {current.get('windspeed')} km/h",
            "Next 3 days:",
        ]
        days = daily.get("time") or []
        highs = daily.get("temperature_2m_max") or []
        lows = daily.get("temperature_2m_min") or []
        rain = daily.get("precipitation_sum") or []
        day_rows = []
        for index, day in enumerate(days[:3]):
            hi = highs[index] if index < len(highs) else "?"
            lo = lows[index] if index < len(lows) else "?"
            precip = rain[index] if index < len(rain) else "?"
            day_rows.append({"date": day, "high": hi, "low": lo, "precip": precip})
            lines.append(f"- {day}: high {hi}°C / low {lo}°C, precip {precip} mm")
        payload = {
            "label": label,
            "temperature": current.get("temperature"),
            "wind": current.get("windspeed"),
            "days": day_rows,
        }
        return "\n".join(lines) + f"\n\n[[suvyon:weather]]{json.dumps(payload)}[[/suvyon:weather]]"
    except Exception as exc:
        return f"Tool error: weather failed ({exc})."


def lookup_place(query: str) -> str:
    """Geocode a place with OpenStreetMap Nominatim (free, no key)."""
    q = (query or "").strip()
    if not q:
        return "Tool error: lookup_place requires a query."
    try:
        response = httpx.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": q, "format": "json", "limit": 3},
            headers=_HEADERS,
            timeout=12,
        )
        response.raise_for_status()
        rows = response.json()
        if not rows:
            return f"No places found for “{q}”."
        lines = []
        for row in rows:
            lines.append(
                f"{row.get('display_name')}\n"
                f"lat={row.get('lat')} lon={row.get('lon')} type={row.get('type')}"
            )
        return "\n\n".join(lines)
    except Exception as exc:
        return f"Tool error: lookup_place failed ({exc})."
