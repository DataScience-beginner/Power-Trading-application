"""
Power Forecasting Model for Solar/Wind Farms
Physics-based model with XGBoost boost
"""
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime


class PowerForecastModel:
    """AI-powered solar/wind forecasting model"""
    
    def __init__(self):
        # Model coefficients (can be trained later)
        self.solar_efficiency = 0.18  # 18% panel efficiency
        self.wind_capacity_factor = 0.35  # 35% average capacity factor
        
        # XGBoost boost factors (dummy for MVP, train later)
        self.boost_factors = {
            "clear_sky": 1.05,
            "partly_cloudy": 0.95,
            "cloudy": 0.75,
            "rainy": 0.50
        }
    
    def forecast_power(
        self,
        daily_weather: List[Dict],
        capacity_kw: float,
        farm_type: str = "solar"
    ) -> Dict:
        """
        Forecast power generation with p10/p50/p90 confidence intervals
        
        Args:
            daily_weather: List of daily weather forecasts
            capacity_kw: Farm capacity in kW
            farm_type: "solar" or "wind"
            
        Returns:
            {
                "daily_forecast": [
                    {
                        "date": "2026-01-18",
                        "expected_kwh": float,
                        "p10": float,  # 10th percentile (pessimistic)
                        "p50": float,  # 50th percentile (median)
                        "p90": float,  # 90th percentile (optimistic)
                        "cloud_risk_score": float
                    }
                ],
                "recommended_bid": float,
                "total_week_kwh": float,
                "confidence": "high" | "medium" | "low"
            }
        """
        if farm_type == "solar":
            forecasts = self._forecast_solar(daily_weather, capacity_kw)
        else:
            forecasts = self._forecast_wind(daily_weather, capacity_kw)
        
        # Calculate total and recommended bid
        total_kwh = sum(f["p50"] for f in forecasts)
        recommended_bid = sum(f["p10"] for f in forecasts)  # Conservative bid using p10
        
        # Determine confidence level
        avg_cloud_risk = np.mean([f["cloud_risk_score"] for f in forecasts])
        confidence = "high" if avg_cloud_risk < 0.3 else "medium" if avg_cloud_risk < 0.6 else "low"
        
        return {
            "daily_forecast": forecasts,
            "recommended_bid": round(recommended_bid, 2),
            "total_week_kwh": round(total_kwh, 2),
            "confidence": confidence,
            "farm_type": farm_type,
            "capacity_kw": capacity_kw
        }
    
    def _forecast_solar(self, daily_weather: List[Dict], capacity_kw: float) -> List[Dict]:
        """Solar power forecasting using GHI"""
        forecasts = []
        
        for day in daily_weather:
            ghi = day.get("ghi_wh_m2", 0)  # Wh/m² per day
            cloud_risk = day.get("cloud_risk", 0)
            temp_c = day.get("temp_c", 25)
            
            # Physics-based calculation: P = Capacity × Efficiency × (GHI/1000)
            # Standard test condition: 1000 W/m²
            base_kwh = capacity_kw * self.solar_efficiency * (ghi / 1000)
            
            # Temperature derating: -0.5% per degree above 25°C
            temp_factor = 1.0 - (max(0, temp_c - 25) * 0.005)
            base_kwh *= temp_factor
            
            # Apply XGBoost boost (weather condition based)
            boost = self._get_weather_boost(cloud_risk, day.get("precip_mm", 0))
            expected_kwh = base_kwh * boost
            
            # Calculate p10/p50/p90 based on uncertainty
            uncertainty = 0.15 + (cloud_risk * 0.2)  # 15-35% uncertainty
            p10 = expected_kwh * (1 - uncertainty)
            p50 = expected_kwh
            p90 = expected_kwh * (1 + uncertainty * 0.5)  # Upside limited
            
            forecasts.append({
                "date": day.get("date"),
                "expected_kwh": round(expected_kwh, 2),
                "p10": round(p10, 2),
                "p50": round(p50, 2),
                "p90": round(p90, 2),
                "cloud_risk_score": round(cloud_risk, 2),
                "ghi_wh_m2": round(ghi, 2),
                "temp_c": round(temp_c, 1)
            })
        
        return forecasts
    
    def _forecast_wind(self, daily_weather: List[Dict], capacity_kw: float) -> List[Dict]:
        """Wind power forecasting using wind speed"""
        forecasts = []
        
        for day in daily_weather:
            wind_speed = day.get("wind_speed_ms", 0)  # m/s
            cloud_risk = day.get("cloud_risk", 0)
            
            # Simplified wind power curve (cubic relationship)
            # Cut-in: 3 m/s, Rated: 12 m/s, Cut-out: 25 m/s
            if wind_speed < 3:
                power_factor = 0
            elif wind_speed > 25:
                power_factor = 0
            elif wind_speed > 12:
                power_factor = self.wind_capacity_factor
            else:
                # Cubic power curve between cut-in and rated
                power_factor = self.wind_capacity_factor * ((wind_speed - 3) / 9) ** 3
            
            expected_kwh = capacity_kw * power_factor * 24  # kWh per day
            
            # Wind is less affected by cloud cover
            uncertainty = 0.20  # 20% uncertainty for wind
            p10 = expected_kwh * (1 - uncertainty)
            p50 = expected_kwh
            p90 = expected_kwh * (1 + uncertainty * 0.5)
            
            forecasts.append({
                "date": day.get("date"),
                "expected_kwh": round(expected_kwh, 2),
                "p10": round(p10, 2),
                "p50": round(p50, 2),
                "p90": round(p90, 2),
                "cloud_risk_score": round(cloud_risk, 2),
                "wind_speed_ms": round(wind_speed, 1)
            })
        
        return forecasts
    
    def _get_weather_boost(self, cloud_risk: float, precip_mm: float) -> float:
        """Get XGBoost weather condition boost factor"""
        if precip_mm > 5:
            return self.boost_factors["rainy"]
        elif cloud_risk > 0.7:
            return self.boost_factors["cloudy"]
        elif cloud_risk > 0.3:
            return self.boost_factors["partly_cloudy"]
        else:
            return self.boost_factors["clear_sky"]
