import { FC, useMemo } from 'react';
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';
import { Box, Typography } from '@mui/material';

interface Transaction {
  time_slot?: string;
  quantity?: number;
  rate?: number;
  date?: string;
  report_type?: string;
}

interface HourlyChartProps {
  viewMode: 'hourly' | 'daily' | 'weekly' | 'monthly';
  filteredData: Transaction[];
}

const HourlyChart: FC<HourlyChartProps> = ({ viewMode, filteredData }) => {
  
  const chartData = useMemo(() => {
    if (!filteredData || filteredData.length === 0) return [];

    if (viewMode === 'hourly') {
      // Group by hour (00:00-00:15 → 00:00)
      const hourlyGroups: { [key: string]: { quantity: number; count: number } } = {};
      filteredData.forEach(txn => {
        if (txn.time_slot) {
          const hour = txn.time_slot.split('-')[0].split(':')[0];
          const hourKey = `${hour}:00`;
          if (!hourlyGroups[hourKey]) hourlyGroups[hourKey] = { quantity: 0, count: 0 };
          hourlyGroups[hourKey].quantity += txn.quantity || 0;
          hourlyGroups[hourKey].count += 1;
        }
      });
      
      return Object.entries(hourlyGroups).map(([hour, data]) => ({
        label: hour,
        quantity: data.quantity / data.count,
        count: data.count,
      })).sort((a, b) => a.label.localeCompare(b.label));
      
    } else if (viewMode === 'daily') {
      // Group by date
      const dailyGroups: { [key: string]: { quantity: number; count: number } } = {};
      filteredData.forEach(txn => {
        if (txn.date) {
          const dateKey = new Date(txn.date).toLocaleDateString('en-IN', { day: '2-digit', month: 'short' });
          if (!dailyGroups[dateKey]) dailyGroups[dateKey] = { quantity: 0, count: 0 };
          dailyGroups[dateKey].quantity += txn.quantity || 0;
          dailyGroups[dateKey].count += 1;
        }
      });
      
      return Object.entries(dailyGroups).map(([date, data]) => ({
        label: date,
        quantity: data.quantity,
        count: data.count,
      }));
      
    } else if (viewMode === 'weekly') {
      // Group by week number
      const weeklyGroups: { [key: string]: { quantity: number; count: number } } = {};
      filteredData.forEach(txn => {
        if (txn.date) {
          const date = new Date(txn.date);
          const weekNum = Math.ceil(date.getDate() / 7);
          const weekKey = `Week ${weekNum}`;
          if (!weeklyGroups[weekKey]) weeklyGroups[weekKey] = { quantity: 0, count: 0 };
          weeklyGroups[weekKey].quantity += txn.quantity || 0;
          weeklyGroups[weekKey].count += 1;
        }
      });
      
      return Object.entries(weeklyGroups).map(([week, data]) => ({
        label: week,
        quantity: data.quantity,
        count: data.count,
      }));
      
    } else if (viewMode === 'monthly') {
      // Group by month
      const monthlyGroups: { [key: string]: { quantity: number; count: number } } = {};
      filteredData.forEach(txn => {
        if (txn.date) {
          const monthKey = new Date(txn.date).toLocaleDateString('en-IN', { month: 'short', year: 'numeric' });
          if (!monthlyGroups[monthKey]) monthlyGroups[monthKey] = { quantity: 0, count: 0 };
          monthlyGroups[monthKey].quantity += txn.quantity || 0;
          monthlyGroups[monthKey].count += 1;
        }
      });
      
      return Object.entries(monthlyGroups).map(([month, data]) => ({
        label: month,
        quantity: data.quantity,
        count: data.count,
      }));
    }
    
    return [];
  }, [filteredData, viewMode]);

  if (chartData.length === 0) {
    return (
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%' }}>
        <Typography color="text.secondary">No data available</Typography>
      </Box>
    );
  }

  return (
    <ResponsiveContainer width="100%" height="90%">
      <LineChart data={chartData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="label" angle={viewMode === 'hourly' ? -45 : 0} textAnchor={viewMode === 'hourly' ? 'end' : 'middle'} height={60} />
        <YAxis label={{ value: 'Avg Quantity (MW)', angle: -90, position: 'insideLeft' }} />
        <Tooltip 
          formatter={(value: number, name: string) => {
            if (name === 'quantity') return [value.toFixed(3) + ' MW', 'Avg Quantity'];
            if (name === 'count') return [value, 'Transactions'];
            return value;
          }}
        />
        <Legend />
        <Line dataKey="quantity" stroke="#3b82f6" strokeWidth={2} dot={{ r: 4 }} activeDot={{ r: 6 }} name="Avg Quantity (MW)" />
      </LineChart>
    </ResponsiveContainer>
  );
};

export default HourlyChart;
