"""AI forecasting and weather-analysis routes."""

from typing import Any

from fastapi import APIRouter, Body, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from backend.ai.eda_module import WeatherEDA
from backend.ai.historical_data_fetcher import HistoricalDataFetcher
from backend.ai.power_model import PowerForecastModel
from backend.ai.weather_fetcher import WeatherFetcher


router = APIRouter(tags=["ai"])

weather_fetcher = WeatherFetcher()
power_model = PowerForecastModel()
historical_fetcher = HistoricalDataFetcher()
eda_analyzer = WeatherEDA()


class PowerForecastRequest(BaseModel):
    """Request body for AI-powered power generation forecasting."""

    lat: float = Field(..., description="Latitude of the generation site.")
    lon: float = Field(..., description="Longitude of the generation site.")
    capacity_kw: float = Field(5000, description="Generation capacity in kW.")
    farm_type: str = Field("solar", description="Generation type, usually solar or wind.")
    days_ahead: int = Field(7, description="Number of days to forecast.")


@router.get(
    "/api/ai/weather/{client_id}",
    summary="Get weather forecast",
    description="Fetches weather inputs used by AI power forecasting for a client/site.",
)
async def get_weather_forecast(
    client_id: str,
    lat: float,
    lon: float,
    days_ahead: int = 7,
) -> JSONResponse:
    """Return weather data for AI power forecasting."""
    try:
        weather_data = weather_fetcher.get_weather_data(lat, lon, days_ahead)

        return JSONResponse(
            content={
                "success": True,
                "client_id": client_id,
                "data": weather_data,
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching weather data: {str(e)}") from e


@router.post(
    "/api/ai/forecast-power/{client_id}",
    summary="Forecast power generation",
    description="Generates AI-assisted power forecast using weather data and generation capacity.",
)
async def forecast_power_generation(
    client_id: str,
    payload: PowerForecastRequest,
) -> JSONResponse:
    """Return p10/p50/p90 style power forecast output for a client/site."""
    try:
        weather_data = weather_fetcher.get_weather_data(payload.lat, payload.lon, payload.days_ahead)
        daily_weather = weather_data.get("daily_forecast", [])

        forecast = power_model.forecast_power(
            daily_weather=daily_weather,
            capacity_kw=payload.capacity_kw,
            farm_type=payload.farm_type,
        )

        return JSONResponse(
            content={
                "success": True,
                "client_id": client_id,
                "forecast": forecast,
                "weather_summary": weather_data.get("historical_summary"),
                "location": {"lat": payload.lat, "lon": payload.lon},
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating power forecast: {str(e)}") from e


@router.get(
    "/api/ai/inspect-weather/{client_id}",
    summary="Inspect weather data",
    description="Returns weather data quality checks and descriptive statistics before forecasting.",
)
async def inspect_weather_data(
    client_id: str,
    lat: float,
    lon: float,
    days_ahead: int = 7,
) -> JSONResponse:
    """Inspect weather data before running forecasting logic."""
    try:
        weather_data = weather_fetcher.get_weather_data(lat, lon, days_ahead)
        historical = weather_data.get("historical_summary", {})
        daily = weather_data.get("daily_forecast", [])

        ghi_values = [d.get("ghi_wh_m2", 0) for d in daily]
        temp_values = [d.get("temp_c", 0) for d in daily]
        precip_values = [d.get("precip_mm", 0) for d in daily]
        cloud_risks = [d.get("cloud_risk", 0) for d in daily]

        stats = {
            "ghi_stats": {
                "min": round(min(ghi_values) if ghi_values else 0, 2),
                "max": round(max(ghi_values) if ghi_values else 0, 2),
                "avg": round(sum(ghi_values) / len(ghi_values) if ghi_values else 0, 2),
            },
            "temp_stats": {
                "min": round(min(temp_values) if temp_values else 0, 1),
                "max": round(max(temp_values) if temp_values else 0, 1),
                "avg": round(sum(temp_values) / len(temp_values) if temp_values else 0, 1),
            },
            "precip_stats": {
                "total": round(sum(precip_values), 1),
                "rainy_days": sum(1 for p in precip_values if p > 1),
            },
            "cloud_risk_stats": {
                "avg": round(sum(cloud_risks) / len(cloud_risks) if cloud_risks else 0, 2),
                "high_risk_days": sum(1 for c in cloud_risks if c > 0.6),
            },
        }

        quality_checks = {
            "all_dates_present": len(daily) == days_ahead,
            "data_completeness": f"{len(daily)}/{days_ahead} days",
        }

        return JSONResponse(
            content={
                "success": True,
                "client_id": client_id,
                "location": {"lat": lat, "lon": lon},
                "historical_summary": historical,
                "statistics": stats,
                "quality_checks": quality_checks,
                "daily_forecast": daily,
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}") from e


@router.get(
    "/api/ai/historical-data/{client_id}",
    summary="Get historical weather data",
    description="Fetches historical weather data used for exploratory analysis and forecast context.",
)
async def get_historical_data(
    client_id: str,
    lat: float,
    lon: float,
    years: int = 10,
) -> JSONResponse:
    """Return historical weather data for AI analysis."""
    try:
        result = historical_fetcher.get_historical_data(lat, lon, years)
        return JSONResponse(content={"success": True, "client_id": client_id, **result})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}") from e


@router.post(
    "/api/ai/eda-analysis/{client_id}",
    summary="Run weather EDA",
    description="Performs exploratory data analysis on historical weather data for forecasting insight.",
)
async def perform_eda(
    client_id: str,
    raw_data: list[dict[str, Any]] = Body(...),
) -> JSONResponse:
    """Analyze historical weather data and return EDA insights."""
    try:
        analysis = eda_analyzer.analyze(raw_data)
        return JSONResponse(
            content={
                "success": True,
                "client_id": client_id,
                "eda_results": analysis,
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}") from e

