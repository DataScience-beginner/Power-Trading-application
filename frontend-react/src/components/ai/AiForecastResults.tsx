import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Chip,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper
} from '@mui/material';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import BoltIcon from '@mui/icons-material/Bolt';
import CloudIcon from '@mui/icons-material/Cloud';

export default function AiForecastResults({ forecast, clientId }) {
  if (!forecast) return null;

  const handleUseBid = () => {
    // TODO: Integrate with existing BidForm component
    alert(`Recommended Bid: ${forecast.recommended_bid} kWh\nTotal Week: ${forecast.total_week_kwh} kWh`);
  };

  return (
    <Box>
      {/* Summary Cards */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                <BoltIcon sx={{ fontSize: 16 }} /> Total Week
              </Typography>
              <Typography variant="h5">
                {forecast.total_week_kwh?.toLocaleString()} kWh
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                <TrendingUpIcon sx={{ fontSize: 16 }} /> Recommended Bid
              </Typography>
              <Typography variant="h5" color="primary">
                {forecast.recommended_bid?.toLocaleString()} kWh
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                <CloudIcon sx={{ fontSize: 16 }} /> Confidence
              </Typography>
              <Chip
                label={forecast.confidence?.toUpperCase()}
                color={
                  forecast.confidence === 'high' ? 'success' :
                  forecast.confidence === 'medium' ? 'warning' : 'error'
                }
              />
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Farm Type
              </Typography>
              <Typography variant="h6">
                {forecast.farm_type === 'solar' ? '☀️ Solar' : '💨 Wind'}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {forecast.capacity_kw?.toLocaleString()} kW
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Use Recommended Bid Button */}
      <Box sx={{ mb: 3 }}>
        <Button
          variant="contained"
          color="success"
          size="large"
          onClick={handleUseBid}
          fullWidth
        >
          ✅ Use Recommended Bid ({forecast.recommended_bid?.toLocaleString()} kWh)
        </Button>
      </Box>

      {/* Daily Forecast Table */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Daily Forecast Details
          </Typography>
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Date</TableCell>
                  <TableCell align="right">Expected (P50)</TableCell>
                  <TableCell align="right">Pessimistic (P10)</TableCell>
                  <TableCell align="right">Optimistic (P90)</TableCell>
                  <TableCell align="right">Cloud Risk</TableCell>
                  {forecast.farm_type === 'solar' && (
                    <>
                      <TableCell align="right">GHI (Wh/m²)</TableCell>
                      <TableCell align="right">Temp (°C)</TableCell>
                    </>
                  )}
                  {forecast.farm_type === 'wind' && (
                    <TableCell align="right">Wind (m/s)</TableCell>
                  )}
                </TableRow>
              </TableHead>
              <TableBody>
                {forecast.daily_forecast?.map((day, index) => (
                  <TableRow key={index}>
                    <TableCell>
                      {new Date(day.date).toLocaleDateString('en-US', {
                        month: 'short',
                        day: 'numeric',
                        year: 'numeric'
                      })}
                    </TableCell>
                    <TableCell align="right">
                      <strong>{day.p50?.toLocaleString()} kWh</strong>
                    </TableCell>
                    <TableCell align="right">{day.p10?.toLocaleString()} kWh</TableCell>
                    <TableCell align="right">{day.p90?.toLocaleString()} kWh</TableCell>
                    <TableCell align="right">
                      <Chip
                        label={`${(day.cloud_risk_score * 100).toFixed(0)}%`}
                        size="small"
                        color={day.cloud_risk_score < 0.3 ? 'success' : day.cloud_risk_score < 0.6 ? 'warning' : 'error'}
                      />
                    </TableCell>
                    {forecast.farm_type === 'solar' && (
                      <>
                        <TableCell align="right">{day.ghi_wh_m2?.toLocaleString()}</TableCell>
                        <TableCell align="right">{day.temp_c?.toFixed(1)}</TableCell>
                      </>
                    )}
                    {forecast.farm_type === 'wind' && (
                      <TableCell align="right">{day.wind_speed_ms?.toFixed(1)}</TableCell>
                    )}
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>
    </Box>
  );
}
