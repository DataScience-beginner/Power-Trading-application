import { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://power-trading-application-production.up.railway.app';

export function usePowerForecast() {
  const [forecast, setForecast] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [autoRefreshEnabled, setAutoRefreshEnabled] = useState(false);

  const getForecast = async (params) => {
    setLoading(true);
    setError(null);

    try {
      const response = await axios.post(
        `${API_BASE_URL}/api/ai/forecast-power/${params.client_id}`,
        {
          lat: params.lat,
          lon: params.lon,
          capacity_kw: params.capacity_kw,
          farm_type: params.farm_type,
          days_ahead: params.days_ahead
        }
      );

      if (response.data.success) {
        setForecast(response.data.forecast);
      } else {
        setError('Failed to get forecast');
      }
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Error fetching forecast');
    } finally {
      setLoading(false);
    }
  };

  // Auto-refresh every 15 minutes
  useEffect(() => {
    if (!autoRefreshEnabled || !forecast) return;

    const interval = setInterval(() => {
      console.log('Auto-refreshing forecast...');
      // Re-fetch with last params (would need to store them)
    }, 15 * 60 * 1000); // 15 minutes

    return () => clearInterval(interval);
  }, [autoRefreshEnabled, forecast]);

  return {
    forecast,
    loading,
    error,
    getForecast,
    autoRefreshEnabled,
    setAutoRefreshEnabled
  };
}
