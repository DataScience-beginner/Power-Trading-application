import React, { useState, useMemo } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  ToggleButtonGroup,
  ToggleButton,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Button,
  Paper,
  Chip,
  Stack
} from '@mui/material';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';
import { Download, TrendingUp, CalendarMonth } from '@mui/icons-material';

interface WeatherData {
  date: string;
  ghi_wh_m2: number;
  temp_max_c: number;
  temp_min_c: number;
  precip_mm: number;
  wind_speed_ms: number;
}

interface EnhancedEDAProps {
  rawData: WeatherData[];
  summaryStats: any;
}

export default function EnhancedEDACharts({ rawData, summaryStats }: EnhancedEDAProps) {
  const [viewMode, setViewMode] = useState<'time-series' | 'yoy' | 'qoq' | 'monthly'>('time-series');
  const [selectedMetric, setSelectedMetric] = useState<string>('ghi_wh_m2');
  const [chartType, setChartType] = useState<'line' | 'bar' | 'area'>('line');

  // Process data for different views
  const processedData = useMemo(() => {
    if (!rawData || rawData.length === 0) return [];

    const dataWithDates = rawData.map(d => ({
      ...d,
      dateObj: new Date(d.date),
      year: new Date(d.date).getFullYear(),
      month: new Date(d.date).getMonth(),
      quarter: Math.floor(new Date(d.date).getMonth() / 3) + 1,
      monthYear: new Date(d.date).toLocaleDateString('en-US', { month: 'short', year: 'numeric' })
    }));

    switch (viewMode) {
      case 'time-series':
        // Last year with formatted dates
        return dataWithDates.slice(-365).map(d => ({
          ...d,
          displayDate: d.dateObj.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: '2-digit' })
        }));

      case 'monthly':
        // Aggregate by month with year
        const monthlyMap = new Map();
        dataWithDates.forEach(d => {
          const key = `${d.year}-${String(d.month + 1).padStart(2, '0')}`;
          if (!monthlyMap.has(key)) {
            monthlyMap.set(key, { 
              date: key, 
              displayDate: d.monthYear,
              count: 0, 
              sum_ghi: 0, 
              sum_temp_max: 0, 
              sum_temp_min: 0, 
              sum_precip: 0, 
              sum_wind: 0 
            });
          }
          const agg = monthlyMap.get(key);
          agg.count++;
          agg.sum_ghi += d.ghi_wh_m2;
          agg.sum_temp_max += d.temp_max_c;
          agg.sum_temp_min += d.temp_min_c;
          agg.sum_precip += d.precip_mm;
          agg.sum_wind += d.wind_speed_ms;
        });
        return Array.from(monthlyMap.values()).map(agg => ({
          date: agg.displayDate,
          ghi_wh_m2: agg.sum_ghi / agg.count,
          temp_max_c: agg.sum_temp_max / agg.count,
          temp_min_c: agg.sum_temp_min / agg.count,
          precip_mm: agg.sum_precip,
          wind_speed_ms: agg.sum_wind / agg.count
        }));

      case 'yoy':
        // Year-over-year comparison by month
        const yoyMap = new Map();
        dataWithDates.forEach(d => {
          const monthKey = d.month;
          if (!yoyMap.has(monthKey)) {
            yoyMap.set(monthKey, {});
          }
          const yearData = yoyMap.get(monthKey);
          if (!yearData[d.year]) {
            yearData[d.year] = { count: 0, sum_ghi: 0, sum_temp: 0, sum_precip: 0, sum_wind: 0 };
          }
          yearData[d.year].count++;
          yearData[d.year].sum_ghi += d.ghi_wh_m2;
          yearData[d.year].sum_temp += (d.temp_max_c + d.temp_min_c) / 2;
          yearData[d.year].sum_precip += d.precip_mm;
          yearData[d.year].sum_wind += d.wind_speed_ms;
        });

        const yoyData: any[] = [];
        const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
        yoyMap.forEach((yearData, monthIdx) => {
          const row: any = { month: months[monthIdx] };
          Object.keys(yearData).forEach(year => {
            const data = yearData[year];
            row[`${year}_ghi`] = data.sum_ghi / data.count;
            row[`${year}_temp`] = data.sum_temp / data.count;
            row[`${year}_precip`] = data.sum_precip;
            row[`${year}_wind`] = data.sum_wind / data.count;
          });
          yoyData.push(row);
        });
        return yoyData;

      case 'qoq':
        // Quarter-over-quarter comparison with better labels
        const qoqMap = new Map();
        dataWithDates.forEach(d => {
          const key = `${d.year}-Q${d.quarter}`;
          if (!qoqMap.has(key)) {
            qoqMap.set(key, { 
              quarter: key, 
              year: d.year,
              quarterNum: d.quarter,
              count: 0, 
              sum_ghi: 0, 
              sum_temp_max: 0, 
              sum_temp_min: 0, 
              sum_precip: 0, 
              sum_wind: 0 
            });
          }
          const agg = qoqMap.get(key);
          agg.count++;
          agg.sum_ghi += d.ghi_wh_m2;
          agg.sum_temp_max += d.temp_max_c;
          agg.sum_temp_min += d.temp_min_c;
          agg.sum_precip += d.precip_mm;
          agg.sum_wind += d.wind_speed_ms;
        });

        const qoqData = Array.from(qoqMap.values()).map((agg, idx, arr) => {
          const prevQuarter = arr[idx - 1];
          const ghi_avg = agg.sum_ghi / agg.count;
          const ghi_change = prevQuarter ? ((ghi_avg - (prevQuarter.sum_ghi / prevQuarter.count)) / (prevQuarter.sum_ghi / prevQuarter.count)) * 100 : 0;

          return {
            quarter: agg.quarter, // Already formatted as "2024-Q1"
            ghi_wh_m2: ghi_avg,
            temp_max_c: agg.sum_temp_max / agg.count,
            temp_min_c: agg.sum_temp_min / agg.count,
            precip_mm: agg.sum_precip,
            wind_speed_ms: agg.sum_wind / agg.count,
            ghi_change: ghi_change.toFixed(1)
          };
        });
        return qoqData;

      default:
        return dataWithDates;
    }
  }, [rawData, viewMode]);

  // Export to CSV
  const handleExportCSV = () => {
    if (!rawData || rawData.length === 0) return;

    const headers = ['Date', 'GHI (Wh/m²)', 'Temp Max (°C)', 'Temp Min (°C)', 'Precipitation (mm)', 'Wind Speed (m/s)'];
    const csvData = rawData.map(row => [
      row.date,
      row.ghi_wh_m2.toFixed(2),
      row.temp_max_c.toFixed(1),
      row.temp_min_c.toFixed(1),
      row.precip_mm.toFixed(1),
      row.wind_speed_ms.toFixed(1)
    ]);

    const csv = [headers, ...csvData].map(row => row.join(',')).join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `weather_data_${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
  };

  const metricLabels: Record<string, string> = {
    ghi_wh_m2: 'GHI (Wh/m²)',
    temp_max_c: 'Temperature Max (°C)',
    temp_min_c: 'Temperature Min (°C)',
    precip_mm: 'Precipitation (mm)',
    wind_speed_ms: 'Wind Speed (m/s)'
  };

  return (
    <Card>
      <CardContent>
        <Grid container spacing={2} alignItems="center" sx={{ mb: 3 }}>
          <Grid item xs={12} md={4}>
            <Typography variant="h6">
              📊 Advanced Weather Analytics
            </Typography>
          </Grid>
          <Grid item xs={12} md={8}>
            <Stack direction="row" spacing={2} flexWrap="wrap">
              <ToggleButtonGroup
                value={viewMode}
                exclusive
                onChange={(_, value) => value && setViewMode(value)}
                size="small"
              >
                <ToggleButton value="time-series">Time Series</ToggleButton>
                <ToggleButton value="monthly">Monthly</ToggleButton>
                <ToggleButton value="yoy"><TrendingUp fontSize="small" /> YoY</ToggleButton>
                <ToggleButton value="qoq"><CalendarMonth fontSize="small" /> QoQ</ToggleButton>
              </ToggleButtonGroup>

              <FormControl size="small" sx={{ minWidth: 150 }}>
                <InputLabel>Metric</InputLabel>
                <Select value={selectedMetric} label="Metric" onChange={(e) => setSelectedMetric(e.target.value)}>
                  <MenuItem value="ghi_wh_m2">GHI (Solar)</MenuItem>
                  <MenuItem value="temp_max_c">Temperature Max</MenuItem>
                  <MenuItem value="temp_min_c">Temperature Min</MenuItem>
                  <MenuItem value="precip_mm">Precipitation</MenuItem>
                  <MenuItem value="wind_speed_ms">Wind Speed</MenuItem>
                </Select>
              </FormControl>

              <ToggleButtonGroup
                value={chartType}
                exclusive
                onChange={(_, value) => value && setChartType(value)}
                size="small"
              >
                <ToggleButton value="line">Line</ToggleButton>
                <ToggleButton value="bar">Bar</ToggleButton>
                <ToggleButton value="area">Area</ToggleButton>
              </ToggleButtonGroup>

              <Button
                variant="outlined"
                size="small"
                startIcon={<Download />}
                onClick={handleExportCSV}
              >
                Export CSV
              </Button>
            </Stack>
          </Grid>
        </Grid>

        {/* Chart */}
        <ResponsiveContainer width="100%" height={400}>
          {chartType === 'line' && (
            <LineChart data={processedData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey={viewMode === 'yoy' ? 'month' : viewMode === 'qoq' ? 'quarter' : viewMode === 'time-series' ? 'displayDate' : 'date'}
                angle={viewMode === 'time-series' ? -45 : 0}
                textAnchor={viewMode === 'time-series' ? 'end' : 'middle'}
                height={viewMode === 'time-series' ? 80 : 60}
                interval={viewMode === 'time-series' ? 'preserveStartEnd' : 0}
              />
              <YAxis label={{ value: metricLabels[selectedMetric], angle: -90, position: 'insideLeft' }} />
              <Tooltip />
              <Legend />
              {viewMode === 'yoy' ? (
                // Multiple lines for each year
                <>
                  {Object.keys(processedData[0] || {}).filter(k => k.endsWith('_ghi') && selectedMetric === 'ghi_wh_m2').map((key, idx) => (
                    <Line key={key} type="monotone" dataKey={key} stroke={`hsl(${idx * 60}, 70%, 50%)`} name={key.split('_')[0]} />
                  ))}
                </>
              ) : (
                <Line type="monotone" dataKey={selectedMetric} stroke="#8884d8" strokeWidth={2} dot={{ r: 3 }} />
              )}
            </LineChart>
          )}
          
          {chartType === 'bar' && (
            <BarChart data={processedData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey={viewMode === 'yoy' ? 'month' : viewMode === 'qoq' ? 'quarter' : viewMode === 'time-series' ? 'displayDate' : 'date'}
                angle={viewMode === 'time-series' ? -45 : 0}
                textAnchor={viewMode === 'time-series' ? 'end' : 'middle'}
                height={viewMode === 'time-series' ? 80 : 60}
              />
              <YAxis label={{ value: metricLabels[selectedMetric], angle: -90, position: 'insideLeft' }} />
              <Tooltip />
              <Legend />
              <Bar dataKey={selectedMetric} fill="#82ca9d" />
            </BarChart>
          )}

          {chartType === 'area' && (
            <AreaChart data={processedData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey={viewMode === 'yoy' ? 'month' : viewMode === 'qoq' ? 'quarter' : viewMode === 'time-series' ? 'displayDate' : 'date'}
                angle={viewMode === 'time-series' ? -45 : 0}
                textAnchor={viewMode === 'time-series' ? 'end' : 'middle'}
                height={viewMode === 'time-series' ? 80 : 60}
              />
              <YAxis label={{ value: metricLabels[selectedMetric], angle: -90, position: 'insideLeft' }} />
              <Tooltip />
              <Legend />
              <Area type="monotone" dataKey={selectedMetric} stroke="#8884d8" fill="#8884d8" fillOpacity={0.3} />
            </AreaChart>
          )}
        </ResponsiveContainer>

        {/* QoQ Growth Indicators */}
        {viewMode === 'qoq' && (
          <Box sx={{ mt: 2 }}>
            <Typography variant="subtitle2" gutterBottom>Quarter-over-Quarter Growth:</Typography>
            <Stack direction="row" spacing={1} flexWrap="wrap">
              {processedData.slice(-4).map((q: any) => (
                <Chip
                  key={q.quarter}
                  label={`${q.quarter}: ${q.ghi_change > 0 ? '+' : ''}${q.ghi_change}%`}
                  color={parseFloat(q.ghi_change) > 0 ? 'success' : 'error'}
                  size="small"
                />
              ))}
            </Stack>
          </Box>
        )}
      </CardContent>
    </Card>
  );
}
