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
  InputLabel,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip
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
  
  // Add inspection state
  const [inspectionData, setInspectionData] = useState<any>(null);
  const [inspecting, setInspecting] = useState(false);
  
  // Add historical data state
  const [historicalData, setHistoricalData] = useState<any>(null);
  const [fetchingHistory, setFetchingHistory] = useState(false);
  const [logs, setLogs] = useState<string[]>([]);
  
  // Add EDA state
  const [edaResults, setEdaResults] = useState<any>(null);
  const [analyzingEDA, setAnalyzingEDA] = useState(false);

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
  
  const handleInspectData = async () => {
    setInspecting(true);
    try {
      const API_BASE = 'http://localhost:8000';
      const response = await fetch(
        `${API_BASE}/api/ai/inspect-weather/${clientId}?lat=${lat}&lon=${lon}&days_ahead=${daysAhead}`
      );
      const data = await response.json();
      if (data.success) {
        setInspectionData(data);
      }
    } catch (err) {
      console.error('Inspection error:', err);
    } finally {
      setInspecting(false);
    }
  };
  
  const handleFetchHistoricalData = async () => {
    setFetchingHistory(true);
    setLogs(['🚀 Starting data pipeline...']);
    try {
      const API_BASE = 'http://localhost:8000';
      const response = await fetch(
        `${API_BASE}/api/ai/historical-data/${clientId}?lat=${lat}&lon=${lon}&years=10`
      );
      const data = await response.json();
      if (data.success) {
        setHistoricalData(data);
        setLogs(data.logs || []);
        // Auto-trigger EDA after data fetch
        if (data.raw_data && data.raw_data.length > 0) {
          performEDA(data.raw_data);
        }
      }
    } catch (err) {
      console.error('Historical data error:', err);
      setLogs(prev => [...prev, `❌ Error: ${err}`]);
    } finally {
      setFetchingHistory(false);
    }
  };
  
  const performEDA = async (rawData: any[]) => {
    setAnalyzingEDA(true);
    setLogs(prev => [...prev, '📊 Starting EDA analysis...']);
    try {
      const API_BASE = 'http://localhost:8000';
      const response = await fetch(
        `${API_BASE}/api/ai/eda-analysis/${clientId}`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(rawData)
        }
      );
      const data = await response.json();
      if (data.success) {
        setEdaResults(data.eda_results);
        setLogs(prev => [...prev, '✅ EDA complete! Patterns identified.']);
      }
    } catch (err) {
      console.error('EDA error:', err);
      setLogs(prev => [...prev, `❌ EDA Error: ${err}`]);
    } finally {
      setAnalyzingEDA(false);
    }
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
            <Grid item xs={12} md={6}>
              <Button
                variant="contained"
                color="success"
                onClick={handleFetchHistoricalData}
                disabled={fetchingHistory}
                fullWidth
                sx={{ height: 56 }}
              >
                {fetchingHistory ? <CircularProgress size={24} /> : '📦 STEP 1: Fetch 10-Year Historical Data'}
              </Button>
            </Grid>
            <Grid item xs={12} md={6}>
              <Button
                variant="outlined"
                color="secondary"
                onClick={handleInspectData}
                disabled={inspecting}
                fullWidth
                sx={{ height: 56 }}
              >
                {inspecting ? <CircularProgress size={24} /> : '🔍 Inspect 7-Day Forecast'}
              </Button>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Progress Logs */}
      {logs.length > 0 && (
        <Card sx={{ mb: 3, bgcolor: '#1e1e1e', color: '#00ff00' }}>
          <CardContent>
            <Typography variant="h6" gutterBottom sx={{ color: '#00ff00' }}>
              🖥️ Processing Logs
            </Typography>
            <Box sx={{ fontFamily: 'monospace', fontSize: '0.875rem' }}>
              {logs.map((log, idx) => (
                <div key={idx} style={{ marginBottom: '4px' }}>
                  {log}
                </div>
              ))}
            </Box>
          </CardContent>
        </Card>
      )}

      {/* Historical Data Table */}
      {historicalData && historicalData.raw_data && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              📋 Historical Weather Data ({historicalData.summary_stats?.total_days} days)
            </Typography>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              {historicalData.cached ? 
                `✅ Loaded from cache (fetched: ${new Date(historicalData.cache_date).toLocaleString()})` :
                '🆕 Fresh data fetched and cached'
              }
            </Typography>
            
            {/* Summary Stats */}
            <Grid container spacing={2} sx={{ mb: 2 }}>
              <Grid item xs={6} md={3}>
                <Chip label={`Avg GHI: ${historicalData.summary_stats?.avg_ghi?.toFixed(0)} Wh/m²`} color="primary" />
              </Grid>
              <Grid item xs={6} md={3}>
                <Chip label={`Avg Temp: ${historicalData.summary_stats?.avg_temp?.toFixed(1)}°C`} color="secondary" />
              </Grid>
              <Grid item xs={6} md={3}>
                <Chip label={`Total Rain: ${historicalData.summary_stats?.total_precip?.toFixed(0)} mm`} color="info" />
              </Grid>
              <Grid item xs={6} md={3}>
                <Chip label={`Rainy Days: ${historicalData.summary_stats?.rainy_days}`} color="warning" />
              </Grid>
            </Grid>
            
            {/* Data Table (first 100 rows) */}
            <TableContainer component={Paper} sx={{ maxHeight: 400 }}>
              <Table stickyHeader size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Date</TableCell>
                    <TableCell align="right">GHI (Wh/m²)</TableCell>
                    <TableCell align="right">Temp Max (°C)</TableCell>
                    <TableCell align="right">Temp Min (°C)</TableCell>
                    <TableCell align="right">Precipitation (mm)</TableCell>
                    <TableCell align="right">Wind (m/s)</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {historicalData.raw_data.slice(0, 100).map((row: any, idx: number) => (
                    <TableRow key={idx}>
                      <TableCell>{row.date}</TableCell>
                      <TableCell align="right">{row.ghi_wh_m2?.toFixed(0)}</TableCell>
                      <TableCell align="right">{row.temp_max_c?.toFixed(1)}</TableCell>
                      <TableCell align="right">{row.temp_min_c?.toFixed(1)}</TableCell>
                      <TableCell align="right">{row.precip_mm?.toFixed(1)}</TableCell>
                      <TableCell align="right">{row.wind_speed_ms?.toFixed(1)}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
            <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
              Showing first 100 of {historicalData.raw_data.length} records
            </Typography>
          </CardContent>
        </Card>
      )}

      {/* EDA Results */}
      {edaResults && (
        <Card sx={{ mb: 3, bgcolor: '#fff3e0' }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              🔬 STEP 2: EDA Results - Pattern Analysis
            </Typography>
            
            {/* Insights */}
            <Box sx={{ mb: 2 }}>
              <Typography variant="subtitle2" gutterBottom>Key Insights:</Typography>
              {edaResults.insights?.map((insight: string, idx: number) => (
                <Alert severity="info" key={idx} sx={{ mb: 1 }}>
                  {insight}
                </Alert>
              ))}
            </Box>
            
            {/* Data Quality */}
            <Typography variant="subtitle2" gutterBottom>Data Quality:</Typography>
            <Grid container spacing={1}>
              <Grid item xs={6} md={3}>
                <Chip label={`Total: ${edaResults.data_quality?.total_records} records`} size="small" />
              </Grid>
              <Grid item xs={6} md={3}>
                <Chip label={`Completeness: ${edaResults.data_quality?.data_completeness}`} size="small" color="success" />
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      )}

      {/* Now proceed with forecast */}
      {edaResults && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Button
              variant="contained"
              color="primary"
              onClick={handleGetForecast}
              disabled={loading}
              fullWidth
              size="large"
            >
              {loading ? <CircularProgress size={24} /> : '⚡ STEP 3: Generate AI Forecast (with trained patterns)'}
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Inspection Results */}
      {inspectionData && (
        <Card sx={{ mb: 3, bgcolor: '#f5f5f5' }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>📊 Weather Data Inspection (EDA)</Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} md={3}>
                <Typography variant="body2" color="text.secondary">GHI (Solar Radiation)</Typography>
                <Typography variant="h6">{inspectionData.statistics?.ghi_stats?.avg} Wh/m²</Typography>
                <Typography variant="caption">Range: {inspectionData.statistics?.ghi_stats?.min} - {inspectionData.statistics?.ghi_stats?.max}</Typography>
              </Grid>
              <Grid item xs={12} md={3}>
                <Typography variant="body2" color="text.secondary">Temperature</Typography>
                <Typography variant="h6">{inspectionData.statistics?.temp_stats?.avg}°C</Typography>
                <Typography variant="caption">Range: {inspectionData.statistics?.temp_stats?.min}°C - {inspectionData.statistics?.temp_stats?.max}°C</Typography>
              </Grid>
              <Grid item xs={12} md={3}>
                <Typography variant="body2" color="text.secondary">Precipitation</Typography>
                <Typography variant="h6">{inspectionData.statistics?.precip_stats?.total} mm</Typography>
                <Typography variant="caption">{inspectionData.statistics?.precip_stats?.rainy_days} rainy days</Typography>
              </Grid>
              <Grid item xs={12} md={3}>
                <Typography variant="body2" color="text.secondary">Cloud Risk</Typography>
                <Typography variant="h6">{(inspectionData.statistics?.cloud_risk_stats?.avg * 100).toFixed(0)}%</Typography>
                <Typography variant="caption">{inspectionData.statistics?.cloud_risk_stats?.high_risk_days} high-risk days</Typography>
              </Grid>
              <Grid item xs={12}>
                <Alert severity={inspectionData.quality_checks?.all_dates_present ? "success" : "warning"}>
                  Data Quality: {inspectionData.quality_checks?.data_completeness} | 
                  {inspectionData.quality_checks?.all_dates_present ? ' ✅ All data present' : ' ⚠️ Incomplete data'}
                </Alert>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      )}

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
