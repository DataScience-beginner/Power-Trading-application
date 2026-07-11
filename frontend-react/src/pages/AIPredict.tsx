import { useEffect, useMemo, useState } from 'react';
import { Alert, Box, Button, Card, CardContent, Chip, CircularProgress, Grid, MenuItem, Stack, TextField, Typography } from '@mui/material';
import { CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';

import apiService from '../services/api';
import type { Client } from '../types';
import type { DemoProvisionResult, SolarForecast } from '../types/forecasting';
import type { ChatUser } from '../types/chatbot';

const errorMessage = (reason: any) => String(reason?.response?.data?.detail || reason?.message || 'Request failed');

export default function AIPredict() {
  const storedUser = sessionStorage.getItem('innowatt_user');
  const user: ChatUser | null = storedUser ? JSON.parse(storedUser) : null;
  const [clients, setClients] = useState<Client[]>([]);
  const [clientId, setClientId] = useState<number | ''>('');
  const [portfolioId, setPortfolioId] = useState<number | ''>('');
  const [horizon, setHorizon] = useState(7);
  const [forecast, setForecast] = useState<SolarForecast | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [demoPassword, setDemoPassword] = useState('');
  const [provisioned, setProvisioned] = useState<DemoProvisionResult | null>(null);

  const loadClients = async () => {
    const available = await apiService.getClients();
    setClients(available);
    const selected = available.find((item) => item.id === clientId) || available[0];
    if (selected) {
      setClientId(selected.id);
      setPortfolioId(selected.portfolios?.[0]?.id || '');
    }
  };

  useEffect(() => {
    loadClients().catch((reason) => setError(errorMessage(reason)));
  }, []);

  const selectedClient = useMemo(() => clients.find((item) => item.id === clientId), [clients, clientId]);

  const runForecast = async () => {
    if (!clientId || !portfolioId) return;
    setLoading(true); setError('');
    try {
      setForecast(await apiService.runSolarForecast(clientId, portfolioId, horizon));
    } catch (reason) { setError(errorMessage(reason)); }
    finally { setLoading(false); }
  };

  const provisionDemo = async () => {
    setLoading(true); setError('');
    try {
      const result = await apiService.provisionDemoTenants(demoPassword);
      setProvisioned(result);
      setDemoPassword('');
      await loadClients();
    } catch (reason) { setError(errorMessage(reason)); }
    finally { setLoading(false); }
  };

  return <Box sx={{ p: { xs: 1, md: 3 } }}>
    <Typography variant="h4" fontWeight={900}>Solar Generation Forecast</Typography>
    <Typography color="text.secondary" sx={{ mb: 3 }}>Coordinate-aware, history-calibrated P10/P50/P90 forecasts with backtesting, lineage, and tenant isolation.</Typography>

    {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
    {user?.role === 'platform_admin' && <Card sx={{ mb: 3, border: '1px solid', borderColor: 'primary.light' }}>
      <CardContent><Typography variant="h6" fontWeight={800}>Demo tenant provisioning</Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>Idempotently creates five synthetic clients, two portfolios each, scoped users, generation history, and trading fixtures.</Typography>
        <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
          <TextField label="Shared demo-user password" type="password" value={demoPassword} onChange={(event) => setDemoPassword(event.target.value)} helperText="Minimum 12 characters; existing passwords are not reset" fullWidth />
          <Button variant="outlined" onClick={provisionDemo} disabled={loading || demoPassword.length < 12}>Provision five clients</Button>
        </Stack>
        {provisioned && <Alert severity="success" sx={{ mt: 2 }}>Ready: {provisioned.clients_total} clients. Created this run: {Object.entries(provisioned.records_created).map(([key, value]) => `${key}=${value}`).join(', ')}.</Alert>}
      </CardContent>
    </Card>}

    <Card sx={{ mb: 3 }}><CardContent><Grid container spacing={2}>
      <Grid item xs={12} md={4}><TextField select fullWidth label="Client" value={clientId} onChange={(event) => {
        const id = Number(event.target.value); const client = clients.find((item) => item.id === id);
        setClientId(id); setPortfolioId(client?.portfolios?.[0]?.id || ''); setForecast(null);
      }}>{clients.map((client) => <MenuItem key={client.id} value={client.id}>{client.entity_name}</MenuItem>)}</TextField></Grid>
      <Grid item xs={12} md={4}><TextField select fullWidth label="Portfolio" value={portfolioId} onChange={(event) => { setPortfolioId(Number(event.target.value)); setForecast(null); }}>
        {(selectedClient?.portfolios || []).map((portfolio) => <MenuItem key={portfolio.id} value={portfolio.id}>{portfolio.portfolio_name || portfolio.portfolio_code}</MenuItem>)}
      </TextField></Grid>
      <Grid item xs={12} md={2}><TextField select fullWidth label="Horizon" value={horizon} onChange={(event) => setHorizon(Number(event.target.value))}>{[3, 7, 14].map((days) => <MenuItem key={days} value={days}>{days} days</MenuItem>)}</TextField></Grid>
      <Grid item xs={12} md={2}><Button fullWidth variant="contained" sx={{ height: 56 }} onClick={runForecast} disabled={loading || !portfolioId}>{loading ? <CircularProgress size={22} /> : 'Run forecast'}</Button></Grid>
    </Grid></CardContent></Card>

    {forecast && <>
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={6} md={3}><Card><CardContent><Typography color="text.secondary">P50 total</Typography><Typography variant="h5" fontWeight={800}>{Math.round(forecast.points.reduce((sum, item) => sum + item.p50_kwh, 0)).toLocaleString()} kWh</Typography></CardContent></Card></Grid>
        <Grid item xs={6} md={3}><Card><CardContent><Typography color="text.secondary">Confidence</Typography><Typography variant="h5" fontWeight={800}>{Math.round(forecast.confidence * 100)}%</Typography></CardContent></Card></Grid>
        <Grid item xs={6} md={3}><Card><CardContent><Typography color="text.secondary">Backtest MAPE</Typography><Typography variant="h5" fontWeight={800}>{forecast.backtest_metrics.mape_pct ?? 'N/A'}%</Typography></CardContent></Card></Grid>
        <Grid item xs={6} md={3}><Card><CardContent><Typography color="text.secondary">Training history</Typography><Typography variant="h5" fontWeight={800}>{forecast.training_points} days</Typography></CardContent></Card></Grid>
      </Grid>
      <Card sx={{ mb: 3 }}><CardContent>
        <Stack direction="row" spacing={1} flexWrap="wrap" sx={{ mb: 2 }}><Chip label={`${forecast.model_name} ${forecast.model_version}`} /><Chip color={forecast.weather_source === 'actual_api' ? 'success' : 'warning'} label={`${forecast.weather_provider}: ${forecast.weather_source}`} /><Chip color="info" label={`${forecast.data_classification} history`} /><Chip color="warning" label="Human review required" /></Stack>
        <Box sx={{ height: 360 }}><ResponsiveContainer width="100%" height="100%"><LineChart data={forecast.points}><CartesianGrid strokeDasharray="3 3" /><XAxis dataKey="forecast_date" /><YAxis /><Tooltip formatter={(value: number) => `${Math.round(value).toLocaleString()} kWh`} /><Legend /><Line type="monotone" dataKey="p10_kwh" name="P10" stroke="#f59e0b" /><Line type="monotone" dataKey="p50_kwh" name="P50" stroke="#2563eb" strokeWidth={3} /><Line type="monotone" dataKey="p90_kwh" name="P90" stroke="#10b981" /></LineChart></ResponsiveContainer></Box>
      </CardContent></Card>
      {forecast.limitations.length > 0 && <Alert severity="warning">{forecast.limitations.join(' ')}</Alert>}
    </>}
  </Box>;
}
