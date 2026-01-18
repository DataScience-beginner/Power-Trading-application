import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Grid,
  Alert,
  CircularProgress,
  MenuItem,
  Select,
  FormControl,
  InputLabel
} from '@mui/material';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { usePowerForecast } from './usePowerForecast';
import AiForecastResults from './AiForecastResults';

export default function AIBidOptimizer() {
  // Form state
  const [clientId, setClientId] = useState('chennai_solar');
  const [lat, setLat] = useState(12.97);
  const [lon, setLon] = useState(80.22);
  const [capacityKw, setCapacityKw] = useState(5000);
  const [farmType, setFarmType] = useState('solar');
  const [daysAhead, setDaysAhead] = useState(7);

  // Use custom hook for forecast
  const { forecast, loading, error, getForecast } = usePowerForecast();

  const handleGetForecast = () => {
    getForecast({
      client_id: clientId,
      lat,
      lon,
      capacity_kw: capacityKw,
      farm_type: farmType,
      days_ahead: daysAhead
    });
  };

  // Prepare chart data
  const chartData = forecast?.daily_forecast?.map(day => ({
    date: new Date(day.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
    P10: day.p10,
    P50: day.p50,
    P90: day.p90,
    'Cloud Risk': day.cloud_risk_score * 100
  })) || [];

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        🤖 AI Power Forecast
      </Typography>
      <Typography variant="body2" color="text.secondary" gutterBottom>
        Get AI-powered solar/wind generation predictions with confidence intervals for optimal TNEB bidding
      </Typography>

      {/* Input Form */}
      <Card sx={{ mt: 3, mb: 3 }}>
        <CardContent>
          <Grid container spacing={2}>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Client ID"
                value={clientId}
                onChange={(e) => setClientId(e.target.value)}
                placeholder="e.g., chennai_solar"
              />
            </Grid>
            <Grid item xs={12} md={3}>
              <TextField
                fullWidth
                label="Latitude"
                type="number"
                value={lat}
                onChange={(e) => setLat(parseFloat(e.target.value))}
                placeholder="12.97"
              />
            </Grid>
            <Grid item xs={12} md={3}>
              <TextField
                fullWidth
                label="Longitude"
                type="number"
                value={lon}
                onChange={(e) => setLon(parseFloat(e.target.value))}
                placeholder="80.22"
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                label="Capacity (kW)"
                type="number"
                value={capacityKw}
                onChange={(e) => setCapacityKw(parseInt(e.target.value))}
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <FormControl fullWidth>
                <InputLabel>Farm Type</InputLabel>
                <Select
                  value={farmType}
                  label="Farm Type"
                  onChange={(e) => setFarmType(e.target.value)}
                >
                  <MenuItem value="solar">☀️ Solar</MenuItem>
                  <MenuItem value="wind">💨 Wind</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                label="Days Ahead"
                type="number"
                value={daysAhead}
                onChange={(e) => setDaysAhead(parseInt(e.target.value))}
                inputProps={{ min: 1, max: 14 }}
              />
            </Grid>
            <Grid item xs={12}>
              <Button
                variant="contained"
                color="primary"
                onClick={handleGetForecast}
                disabled={loading}
                fullWidth
                sx={{ height: 56 }}
              >
                {loading ? <CircularProgress size={24} /> : '⚡ Get AI Forecast'}
              </Button>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Error Display */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Forecast Results */}
      {forecast && !loading && (
        <>
          <AiForecastResults forecast={forecast} clientId={clientId} />

          {/* Chart */}
          <Card sx={{ mt: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                7-Day Power Forecast (P10/P50/P90)
              </Typography>
              <ResponsiveContainer width="100%" height={400}>
                <BarChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis yAxisId="left" label={{ value: 'kWh', angle: -90, position: 'insideLeft' }} />
                  <YAxis yAxisId="right" orientation="right" label={{ value: 'Cloud Risk %', angle: 90, position: 'insideRight' }} />
                  <Tooltip />
                  <Legend />
                  <Bar yAxisId="left" dataKey="P10" fill="#ff6b6b" name="P10 (Pessimistic)" />
                  <Bar yAxisId="left" dataKey="P50" fill="#4ecdc4" name="P50 (Expected)" />
                  <Bar yAxisId="left" dataKey="P90" fill="#95e1d3" name="P90 (Optimistic)" />
                  <Bar yAxisId="right" dataKey="Cloud Risk" fill="#f38181" name="Cloud Risk %" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </>
      )}
    </Box>
  );
}
