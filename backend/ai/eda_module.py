"""
EDA (Exploratory Data Analysis) Module
Analyzes historical weather data to find patterns
"""
import pandas as pd
from typing import Dict, List
import statistics


class WeatherEDA:
    """Perform EDA on historical weather data"""
    
    def analyze(self, raw_data: List[Dict]) -> Dict:
        """
        Analyze historical data and find patterns
        
        Returns:
            {
                "monthly_patterns": {...},
                "seasonal_trends": {...},
                "correlations": {...},
                "insights": [...]
            }
        """
        df = pd.DataFrame(raw_data)
        
        if df.empty:
            return {"error": "No data to analyze"}
        
        # Convert date column to datetime
        df['date'] = pd.to_datetime(df['date'])
        df['month'] = df['date'].dt.month
        df['year'] = df['date'].dt.year
        df['season'] = df['month'].apply(self._get_season)
        
        # Monthly patterns
        monthly = df.groupby('month').agg({
            'ghi_wh_m2': 'mean',
            'temp_max_c': 'mean',
            'precip_mm': 'sum',
            'wind_speed_ms': 'mean'
        }).round(2)
        
        # Seasonal trends
        seasonal = df.groupby('season').agg({
            'ghi_wh_m2': 'mean',
            'temp_max_c': 'mean',
            'precip_mm': 'sum'
        }).round(2)
        
        # Yearly trends
        yearly = df.groupby('year').agg({
            'ghi_wh_m2': 'mean',
            'temp_max_c': 'mean',
            'precip_mm': 'sum'
        }).round(2)
        
        # Find insights
        insights = []
        
        # Best month for solar
        best_solar_month = monthly['ghi_wh_m2'].idxmax()
        insights.append(f"☀️ Best month for solar: {self._month_name(best_solar_month)} (avg {monthly.loc[best_solar_month, 'ghi_wh_m2']:.0f} Wh/m²)")
        
        # Best month for wind
        best_wind_month = monthly['wind_speed_ms'].idxmax()
        insights.append(f"💨 Best month for wind: {self._month_name(best_wind_month)} (avg {monthly.loc[best_wind_month, 'wind_speed_ms']:.1f} m/s)")
        
        # Rainy season
        rainiest_month = monthly['precip_mm'].idxmax()
        insights.append(f"🌧️ Rainiest month: {self._month_name(rainiest_month)} ({monthly.loc[rainiest_month, 'precip_mm']:.0f} mm)")
        
        # Temperature range
        hottest = monthly['temp_max_c'].max()
        coolest = monthly['temp_max_c'].min()
        insights.append(f"🌡️ Temperature range: {coolest:.1f}°C to {hottest:.1f}°C")
        
        return {
            "monthly_patterns": monthly.to_dict(orient="index"),
            "seasonal_trends": seasonal.to_dict(orient="index"),
            "yearly_trends": yearly.to_dict(orient="index"),
            "insights": insights,
            "data_quality": {
                "total_records": len(df),
                "missing_ghi": int(df['ghi_wh_m2'].isna().sum()),
                "missing_temp": int(df['temp_max_c'].isna().sum()),
                "data_completeness": f"{(1 - df.isna().sum().sum() / (len(df) * len(df.columns))) * 100:.1f}%"
            }
        }
    
    def _get_season(self, month: int) -> str:
        """Get season from month"""
        if month in [12, 1, 2]:
            return "Winter"
        elif month in [3, 4, 5]:
            return "Spring"
        elif month in [6, 7, 8]:
            return "Monsoon"
        else:
            return "Autumn"
    
    def _month_name(self, month: int) -> str:
        """Convert month number to name"""
        names = {
            1: "January", 2: "February", 3: "March", 4: "April",
            5: "May", 6: "June", 7: "July", 8: "August",
            9: "September", 10: "October", 11: "November", 12: "December"
        }
        return names.get(month, "Unknown")
