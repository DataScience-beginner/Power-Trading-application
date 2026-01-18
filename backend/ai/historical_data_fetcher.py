"""
Historical Data Fetcher with Caching
Fetches 10 years of weather data from Open-Meteo API and caches it
"""
import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json
import os
from pathlib import Path


class HistoricalDataFetcher:
    """Fetch and cache historical weather data"""
    
    BASE_URL = "https://archive-api.open-meteo.com/v1/archive"
    CACHE_DIR = Path(__file__).parent.parent / "data" / "cache"
    
    def __init__(self):
        self.session = requests.Session()
        self.CACHE_DIR.mkdir(parents=True, exist_ok=True)
    
    def get_historical_data(
        self,
        lat: float,
        lon: float,
        years: int = 10
    ) -> Dict:
        """
        Fetch 10 years of historical weather data
        
        Returns:
            {
                "logs": ["Step 1...", "Step 2..."],
                "raw_data": pd.DataFrame,
                "summary_stats": {},
                "cached": True/False
            }
        """
        logs = []
        cache_key = f"hist_{lat}_{lon}_{years}y"
        cache_file = self.CACHE_DIR / f"{cache_key}.json"
        
        # Check cache
        logs.append(f"🔍 Step 1: Checking cache for lat={lat}, lon={lon}...")
        if cache_file.exists():
            logs.append("✅ Step 2: Found cached data! Loading from disk...")
            with open(cache_file, 'r') as f:
                cached = json.load(f)
            return {
                "logs": logs + cached["logs"],
                "raw_data": cached["raw_data"],
                "summary_stats": cached["summary_stats"],
                "cached": True,
                "cache_date": cached.get("fetch_date")
            }
        
        logs.append("⚠️ Step 2: No cache found. Fetching from Open-Meteo API...")
        
        # Calculate date range (last 10 years)
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=years * 365)
        
        logs.append(f"📅 Step 3: Date range: {start_date} to {end_date} ({years} years)")
        
        # Fetch data from API
        logs.append("🌐 Step 4: Connecting to Open-Meteo Archive API...")
        params = {
            "latitude": lat,
            "longitude": lon,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "daily": "shortwave_radiation_sum,temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max",
            "timezone": "Asia/Kolkata"
        }
        
        try:
            logs.append("⏳ Step 5: Downloading data (this may take 30-60 seconds)...")
            response = self.session.get(self.BASE_URL, params=params, timeout=120)
            response.raise_for_status()
            data = response.json()
            logs.append(f"✅ Step 6: Data received! Got {len(data.get('daily', {}).get('time', []))} days")
            
            # Convert to DataFrame
            logs.append("🔄 Step 7: Converting to tabular format...")
            daily = data.get("daily", {})
            df_data = {
                "date": daily.get("time", []),
                "ghi_wh_m2": daily.get("shortwave_radiation_sum", []),
                "temp_max_c": daily.get("temperature_2m_max", []),
                "temp_min_c": daily.get("temperature_2m_min", []),
                "precip_mm": daily.get("precipitation_sum", []),
                "wind_speed_ms": daily.get("wind_speed_10m_max", [])
            }
            df = pd.DataFrame(df_data)
            
            # Calculate summary stats
            logs.append("📊 Step 8: Calculating statistical summary...")
            summary = {
                "total_days": len(df),
                "avg_ghi": float(df["ghi_wh_m2"].mean()),
                "avg_temp": float(((df["temp_max_c"] + df["temp_min_c"]) / 2).mean()),
                "total_precip": float(df["precip_mm"].sum()),
                "rainy_days": int((df["precip_mm"] > 1).sum()),
                "avg_wind": float(df["wind_speed_ms"].mean()),
                "date_range": f"{df['date'].min()} to {df['date'].max()}"
            }
            logs.append(f"✅ Step 9: Analysis complete! {summary['total_days']} days analyzed")
            
            # Cache the data
            logs.append("💾 Step 10: Saving to cache for future use...")
            cache_data = {
                "logs": logs,
                "raw_data": df.to_dict(orient="records"),
                "summary_stats": summary,
                "fetch_date": datetime.now().isoformat(),
                "location": {"lat": lat, "lon": lon}
            }
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f)
            logs.append("✅ Step 11: Cache saved! Future requests will be instant.")
            
            return {
                "logs": logs,
                "raw_data": df.to_dict(orient="records"),
                "summary_stats": summary,
                "cached": False,
                "cache_date": cache_data["fetch_date"]
            }
            
        except Exception as e:
            logs.append(f"❌ Error at Step 5: {str(e)}")
            return {
                "logs": logs,
                "raw_data": [],
                "summary_stats": {},
                "cached": False,
                "error": str(e)
            }
