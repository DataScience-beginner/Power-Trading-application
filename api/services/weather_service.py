"""Bounded Open-Meteo adapter with an explicit deterministic demo fallback."""

from datetime import date, timedelta
import math

import requests


class WeatherService:
    provider = "open-meteo"
    endpoint = "https://api.open-meteo.com/v1/forecast"

    def daily_forecast(self, latitude: float, longitude: float, days: int) -> tuple[list[dict], str, list[str]]:
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "daily": "shortwave_radiation_sum,temperature_2m_mean,cloud_cover_mean",
            "timezone": "Asia/Kolkata",
            "forecast_days": days,
        }
        try:
            response = requests.get(self.endpoint, params=params, timeout=8)
            response.raise_for_status()
            daily = response.json().get("daily", {})
            dates = daily.get("time", [])
            rows = [
                {
                    "date": date.fromisoformat(day),
                    "irradiation_kwh_m2": max(0.0, float(daily["shortwave_radiation_sum"][index] or 0) / 3.6),
                    "temperature_c": float(daily["temperature_2m_mean"][index] or 25),
                    "cloud_cover_pct": float(daily["cloud_cover_mean"][index] or 0),
                }
                for index, day in enumerate(dates)
            ]
            if len(rows) != days:
                raise ValueError(f"Weather provider returned {len(rows)} of {days} requested days")
            return rows, "actual_api", []
        except (requests.RequestException, KeyError, TypeError, ValueError) as exc:
            return self._fallback(latitude, longitude, days), "synthetic_fallback", [
                f"Live weather unavailable; deterministic coordinate-based weather was used ({type(exc).__name__})."
            ]

    @staticmethod
    def _fallback(latitude: float, longitude: float, days: int) -> list[dict]:
        today = date.today()
        phase = (abs(latitude) + abs(longitude)) % 7
        return [
            {
                "date": today + timedelta(days=index),
                "irradiation_kwh_m2": round(4.6 + 1.1 * math.sin((index + phase) / 2.3), 3),
                "temperature_c": round(27 + 4 * math.sin((index + phase) / 3.1), 2),
                "cloud_cover_pct": round(38 + 25 * math.cos((index + phase) / 2.7), 2),
            }
            for index in range(days)
        ]
