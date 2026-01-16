import { FC } from 'react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  Cell,
} from 'recharts';
import { useAppSelector } from '../hooks/useAppStore';
import { Box, Typography } from '@mui/material';

const PortfolioComparisonChart: FC = () => {
  const { portfolioComparison } = useAppSelector((state) => state.dashboard);

  if (!portfolioComparison || portfolioComparison.length === 0) {
    return (
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%' }}>
        <Typography color="text.secondary">No comparison data available</Typography>
      </Box>
    );
  }

  const data = portfolioComparison.map((item) => ({
    portfolio: item.portfolio_code,
    dor: Number(item.dor_quantity.toFixed(2)),
    sch: Number(item.sch_quantity.toFixed(2)),
    deviation: Number(item.deviation.toFixed(2)),
  }));

  return (
    <ResponsiveContainer width="100%" height="90%">
      <BarChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="portfolio" />
        <YAxis />
        <Tooltip />
        <Legend />
        <Bar dataKey="dor" fill="#3b82f6" name="DOR Quantity" />
        <Bar dataKey="sch" fill="#10b981" name="SCH Quantity" />
        <Bar dataKey="deviation" fill="#ef4444" name="Deviation" />
      </BarChart>
    </ResponsiveContainer>
  );
};

export default PortfolioComparisonChart;
