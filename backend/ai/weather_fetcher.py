"""
Weather Fetcher for AI Power Forecasting
Uses Open-Meteo API for historical and forecast weather data
"""
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import statistics


class WeatherFetcher:
    """Fetch weather data from Open-Meteo API"""
    
    BASE_URL = "https://api.open-meteo.com/v1"
    
    def __init__(self):
        self.session = requests.Session()
    
    def get_weather_data(
        self,
        lat: float,
        lon: float,
        days_ahead: int = 7
    ) -> Dict:
        """
        Fetch historical summary and forecast data
        
        Args:
            lat: Latitude
            lon: Longitude
            days_ahead: Number of forecast days (default 7)
            
        Returns:
            {
                "historical_summary": {
                    "avg_ghi": float,
                    "rain_days": int
                },
                "daily_forecast": [
                    {
                        "date": "2026-01-18",
                        "ghi_wh_m2": float,
                        "temp_c": float,
                        "precip_mm": float,
                        "wind_speed_ms": float,
                        "cloud_risk": float
                    }
                ]
            }
        """
        # Get historical data (last 30 days)
        historical = self._get_historical(lat, lon, days=30)
        
        # Get forecast data
        forecast = self._get_forecast(lat, lon, days=days_ahead)
        
        return {
            "historical_summary": historical,
            "daily_forecast": forecast,
            "location": {"lat": lat, "lon": lon},
            "generated_at": datetime.now().isoformat()
        }
    
    def _get_historical(self, lat: float, lon: float, days: int = 30) -> Dict:
        """Get historical weather summary"""
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        params = {
            "latitude": lat,
            "longitude": lon,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "daily": "shortwave_radiation_sum,temperature_2m_max,precipitation_sum",
            "timezone": "Asia/Kolkata"
        }
        
        try:
            response = self.session.get(
                f"{self.BASE_URL}/forecast",
                params=params,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            daily = data.get("daily", {})
            ghi_values = [v for v in daily.get("shortwave_radiation_sum", []) if v is not None]
            precip_values = daily.get("precipitation_sum", [])
            
            return {
                "avg_ghi": statistics.mean(ghi_values) if ghi_values else 0.0,
                "rain_days": sum(1 for p in precip_values if p and p > 1.0),
                "period_days": days
            }
        except Exception as e:
            print(f"Error fetching historical data: {e}")
            return {
                "avg_ghi": 0.0,
                "rain_days": 0,
                "period_days": days,
                "error": str(e)
            }
    
    def _get_forecast(self, lat: float, lon: float, days: int = 7) -> List[Dict]:
        """Get daily forecast data"""
        params = {
            "latitude": lat,
            "longitude": lon,
            "daily": "shortwave_radiation_sum,temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max,cloud_cover_mean",
            "timezone": "Asia/Kolkata",
            "forecast_days": days
        }
        
        try:
            response = self.session.get(
                f"{self.BASE_URL}/forecast",
                params=params,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            daily = data.get("daily", {})
            dates = daily.get("time", [])
            ghi = daily.get("shortwave_radiation_sum", [])
            temp_max = daily.get("temperature_2m_max", [])
            temp_min = daily.get("temperature_2m_min", [])
            precip = daily.get("precipitation_sum", [])
            wind = daily.get("wind_speed_10m_max", [])
            clouds = daily.get("cloud_cover_mean", [])
            
            forecast = []
            for i in range(len(dates)):
                # Calculate cloud risk (0-1 scale)
                cloud_pct = clouds[i] if i < len(clouds) and clouds[i] is not None else 0
                precip_mm = precip[i] if i < len(precip) and precip[i] is not None else 0
                cloud_risk = min(1.0, (cloud_pct / 100) + (precip_mm / 10))
                
                forecast.append({
                    "date": dates[i],
                    "ghi_wh_m2": ghi[i] if i < len(ghi) and ghi[i] is not None else 0.0,
                    "temp_c": (temp_max[i] + temp_min[i]) / 2 if i < len(temp_max) and i < len(temp_min) else 25.0,
                    "precip_mm": precip_mm,
                    "wind_speed_ms": wind[i] if i < len(wind) and wind[i] is not None else 0.0,
                    "cloud_risk": round(cloud_risk, 2)
                })
            
            return forecast
            
        except Exception as e:
            print(f"Error fetching forecast data: {e}")
            # Return empty forecast on error
            today = datetime.now().date()
            return [
                {
                    "date": (today + timedelta(days=i)).isoformat(),
                    "ghi_wh_m2": 0.0,
                    "temp_c": 25.0,
                    "precip_mm": 0.0,
                    "wind_speed_ms": 0.0,
                    "cloud_risk": 0.0,
                    "error": str(e)
                }
                for i in range(days)
            ]
