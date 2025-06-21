import requests


def should_delay_watering(lat: float, lon: float) -> str:
    try:
        url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&longitude={lon}&hourly=precipitation&forecast_days=1"
        )
        print("[DEBUG] URL:", url)

        response = requests.get(url, timeout=8)
        data = response.json()
        print("[DEBUG] Full JSON:", data)

        rain_values = data.get("hourly", {}).get("precipitation", [])

        if not rain_values:
            print("[Weather Module] Warning: No precipitation data found")
            return ""

        max_rain = max(rain_values)
        print("[DEBUG] Max precipitation today:", max_rain)

        if max_rain > 0.5:
            return "Rain is expected later today. Watering delayed."
        else:
            return ""

    except Exception as e:
        print("[Weather Module] Error:", e)
        return ""


if __name__ == "__main__":
    result = should_delay_watering(51.5074, -0.1278)  # London
    print(f"[TEST] Recommendation: {result}")
