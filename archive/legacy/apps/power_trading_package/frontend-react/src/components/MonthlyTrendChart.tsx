import { FC } from 'react';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ComposedChart,
  Area,
} from 'recharts';
import { Paper, Typography, Box, ToggleButton, ToggleButtonGroup } from '@mui/material';
import { useState } from 'react';
import type { EnergyScheduleDay } from '../types/energySchedule';

interface MonthlyTrendChartProps {
  days: EnergyScheduleDay[];
  viewMode?: 'daily' | 'weekly' | 'monthly' | 'hourly';
}

interface ChartData {
  date: string;
  energySavings: number;
  ctuLosses: number;
  totalCost: number;
  ctuCharges: number;
  nldcFees: number;
}

const MonthlyTrendChart: FC<MonthlyTrendChartProps> = ({ days, viewMode = 'daily' }) => {
  const [chartType, setChartType] = useState<'energy' | 'cost'>('energy');

  // Aggregate data based on view mode
  const aggregateData = (data: EnergyScheduleDay[]) => {
    if (viewMode === 'hourly') {
      // Show hourly breakdown for first/selected day
      if (data.length === 0) return [];
      const selectedDay = data[0]; // Use first calculated day
      
      // Generate 24 hourly buckets (4 x 15-min slots each)
      const hourlyData: any[] = [];
      for (let hour = 0; hour < 24; hour++) {
        // Simulate hourly data (in real app, this would come from consumption_after_losses_timeslots)
        const avgEnergy = (selectedDay.total_scheduled_mwh || 50) / 24;
        const variation = Math.sin(hour * Math.PI / 12) * 0.3; // Peak during day
        
        hourlyData.push({
          ...selectedDay,
          trading_date: `${hour.toString().padStart(2, '0')}:00`,
          energy_savings_mwh: avgEnergy * (1 + variation) / 4, // Scale down for hourly
          ctu_losses_percent: selectedDay.ctu_losses_percent,
          total_cost: (selectedDay.total_cost || 0) / 24,
          total_ctu_charges: (selectedDay.total_ctu_charges || 0) / 24,
          total_nldc_fees: (selectedDay.total_nldc_fees || 0) / 24,
          is_calculated: true,
        });
      }
      return hourlyData;
    } else if (viewMode === 'daily') {
      // Show all days
      return data;
    } else if (viewMode === 'weekly') {
      // Group by week
      const weeks: { [key: string]: EnergyScheduleDay[] } = {};
      data.forEach(day => {
        const date = new Date(day.trading_date);
        const weekNum = Math.ceil(date.getDate() / 7);
        const weekKey = `Week ${weekNum}`;
        if (!weeks[weekKey]) weeks[weekKey] = [];
        weeks[weekKey].push(day);
      });
      
      // Return averaged data for each week
      return Object.entries(weeks).map(([week, weekDays]) => {
        const avg = weekDays.reduce((acc, d) => ({
          energy_savings_mwh: acc.energy_savings_mwh + (d.energy_savings_mwh || 0),
          ctu_losses_percent: acc.ctu_losses_percent + (d.ctu_losses_percent || 0),
          total_cost: acc.total_cost + (d.total_cost || 0),
          total_ctu_charges: acc.total_ctu_charges + (d.total_ctu_charges || 0),
          total_nldc_fees: acc.total_nldc_fees + (d.total_nldc_fees || 0),
        }), { energy_savings_mwh: 0, ctu_losses_percent: 0, total_cost: 0, total_ctu_charges: 0, total_nldc_fees: 0 });
        
        return {
          ...weekDays[0],
          trading_date: week,
          energy_savings_mwh: avg.energy_savings_mwh,
          ctu_losses_percent: avg.ctu_losses_percent / weekDays.length,
          total_cost: avg.total_cost,
          total_ctu_charges: avg.total_ctu_charges,
          total_nldc_fees: avg.total_nldc_fees,
          is_calculated: true,
        };
      });
    } else if (viewMode === 'monthly') {
      // Return monthly summary
      const total = data.reduce((acc, d) => ({
        energy_savings_mwh: acc.energy_savings_mwh + (d.energy_savings_mwh || 0),
        ctu_losses_percent: acc.ctu_losses_percent + (d.ctu_losses_percent || 0),
        total_cost: acc.total_cost + (d.total_cost || 0),
        total_ctu_charges: acc.total_ctu_charges + (d.total_ctu_charges || 0),
        total_nldc_fees: acc.total_nldc_fees + (d.total_nldc_fees || 0),
      }), { energy_savings_mwh: 0, ctu_losses_percent: 0, total_cost: 0, total_ctu_charges: 0, total_nldc_fees: 0 });
      
      return [{
        ...data[0],
        trading_date: 'Monthly Total',
        energy_savings_mwh: total.energy_savings_mwh,
        ctu_losses_percent: total.ctu_losses_percent / data.length,
        total_cost: total.total_cost,
        total_ctu_charges: total.total_ctu_charges,
        total_nldc_fees: total.total_nldc_fees,
        is_calculated: true,
      }];
    }
    return data;
  };

  // Transform data for charts
  const aggregatedDays = aggregateData(days.filter((day) => day.is_calculated));
  
  const chartData: ChartData[] = aggregatedDays
    .sort((a, b) => {
      if (a.trading_date === 'Monthly Total' || a.trading_date.startsWith('Week')) return 0;
      if (viewMode === 'hourly') return 0; // Keep hourly in order
      return new Date(a.trading_date).getTime() - new Date(b.trading_date).getTime();
    })
    .map((day) => ({
      date: viewMode === 'hourly' 
        ? day.trading_date // Already formatted as "00:00", "01:00", etc.
        : day.trading_date.startsWith('Week') || day.trading_date === 'Monthly Total' 
          ? day.trading_date
          : new Date(day.trading_date).toLocaleDateString('en-IN', {
              day: '2-digit',
              month: 'short',
            }),
      energySavings: day.energy_savings_mwh || 0,
      ctuLosses: day.ctu_losses_percent || 0,
      totalCost: (day.total_cost || 0) / 1000, // Convert to thousands
      ctuCharges: (day.total_ctu_charges || 0) / 1000,
      nldcFees: (day.total_nldc_fees || 0) / 1000,
    }));

  const formatCurrency = (value: number) => {
    return `₹${value.toFixed(0)}K`;
  };

  const formatMWh = (value: number) => {
    return `${value.toFixed(1)} MWh`;
  };

  const formatPercent = (value: number) => {
    return `${value.toFixed(2)}%`;
  };

  const getTrendTitle = () => {
    switch (viewMode) {
      case 'hourly': return 'Hourly Trends';
      case 'daily': return 'Daily Trends';
      case 'weekly': return 'Weekly Trends';
      case 'monthly': return 'Monthly Trends';
      default: return 'Daily Trends';
    }
  };

  return (
    <Paper sx={{ p: 2 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6">{getTrendTitle()}</Typography>
        <ToggleButtonGroup
          value={chartType}
          exclusive
          onChange={(_, value) => value && setChartType(value)}
          size="small"
        >
          <ToggleButton value="energy">Energy Metrics</ToggleButton>
          <ToggleButton value="cost">Cost Breakdown</ToggleButton>
        </ToggleButtonGroup>
      </Box>

      {chartData.length === 0 ? (
        <Box sx={{ height: 400, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <Typography color="text.secondary">No calculated data available</Typography>
        </Box>
      ) : (
        <ResponsiveContainer width="100%" height={400}>
          {chartType === 'energy' ? (
            <ComposedChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" tick={{ fontSize: 12 }} />
              <YAxis
                yAxisId="left"
                label={{ value: 'MWh', angle: -90, position: 'insideLeft' }}
                tick={{ fontSize: 12 }}
              />
              <YAxis
                yAxisId="right"
                orientation="right"
                label={{ value: 'CTU Losses %', angle: 90, position: 'insideRight' }}
                tick={{ fontSize: 12 }}
              />
              <Tooltip
                formatter={(value: number, name: string) => {
                  if (name === 'CTU Losses %') return formatPercent(value);
                  return formatMWh(value);
                }}
              />
              <Legend />
              <Area
                yAxisId="left"
                type="monotone"
                dataKey="energySavings"
                fill="#10b981"
                stroke="#10b981"
                fillOpacity={0.3}
                name="Energy Savings"
              />
              <Line
                yAxisId="right"
                type="monotone"
                dataKey="ctuLosses"
                stroke="#f59e0b"
                strokeWidth={2}
                dot={{ r: 4 }}
                name="CTU Losses %"
              />
            </ComposedChart>
          ) : (
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" tick={{ fontSize: 12 }} />
              <YAxis
                label={{ value: '₹ (Thousands)', angle: -90, position: 'insideLeft' }}
                tick={{ fontSize: 12 }}
              />
              <Tooltip formatter={(value: number) => formatCurrency(value)} />
              <Legend />
              <Bar dataKey="ctuCharges" fill="#3b82f6" name="CTU Charges" stackId="cost" />
              <Bar dataKey="nldcFees" fill="#8b5cf6" name="NLDC Fees" stackId="cost" />
            </BarChart>
          )}
        </ResponsiveContainer>
      )}
    </Paper>
  );
};

export default MonthlyTrendChart;
