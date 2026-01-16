import { FC } from 'react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';
import { useAppSelector } from '../hooks/useAppStore';
import { Box, Typography } from '@mui/material';

const HourlyChart: FC = () => {
  const { hourlyDistribution } = useAppSelector((state) => state.dashboard);

  if (!hourlyDistribution || hourlyDistribution.length === 0) {
    return (
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%' }}>
        <Typography color="text.secondary">No data available</Typography>
      </Box>
    );
  }

  const data = hourlyDistribution.map((item) => ({
    hour: `${item.hour}:00`,
    quantity: Number(item.avg_quantity.toFixed(3)),
    rate: item.avg_rate ? Number(item.avg_rate.toFixed(2)) : 0,
  }));

  return (
    <ResponsiveContainer width="100%" height="90%">
      <BarChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="hour" />
        <YAxis />
        <Tooltip />
        <Legend />
        <Bar dataKey="quantity" fill="#3b82f6" name="Avg Quantity (MW)" />
      </BarChart>
    </ResponsiveContainer>
  );
};

export default HourlyChart;
