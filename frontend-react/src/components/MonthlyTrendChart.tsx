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
}

interface ChartData {
  date: string;
  energySavings: number;
  ctuLosses: number;
  totalCost: number;
  ctuCharges: number;
  nldcFees: number;
}

const MonthlyTrendChart: FC<MonthlyTrendChartProps> = ({ days }) => {
  const [chartType, setChartType] = useState<'energy' | 'cost'>('energy');

  // Transform data for charts
  const chartData: ChartData[] = days
    .filter((day) => day.is_calculated)
    .sort((a, b) => new Date(a.trading_date).getTime() - new Date(b.trading_date).getTime())
    .map((day) => ({
      date: new Date(day.trading_date).toLocaleDateString('en-IN', {
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

  return (
    <Paper sx={{ p: 2 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6">Monthly Trends</Typography>
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
