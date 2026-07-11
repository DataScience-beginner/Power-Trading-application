import { FC, useMemo } from 'react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  PieChart,
  Pie,
  Cell,
} from 'recharts';
import { Box, Typography } from '@mui/material';

interface Transaction {
  report_type?: string;
  quantity?: number;
  type?: string;
}

interface PortfolioComparisonChartProps {
  filteredData: Transaction[];
  reportType: 'all' | 'DOR' | 'SCH';
}

const COLORS = {
  GDAM: '#3b82f6',
  DAM: '#10b981',
  RTM: '#f59e0b',
  DOR: '#8b5cf6',
  SCH: '#ec4899',
  BUY: '#ef4444',
  SELL: '#22c55e',
};

const PortfolioComparisonChart: FC<PortfolioComparisonChartProps> = ({ filteredData, reportType }) => {
  
  const chartData = useMemo(() => {
    if (!filteredData || filteredData.length === 0) return [];

    // Group by market type (GDAM, DAM, RTM)
    const marketGroups: { [key: string]: { buy: number; sell: number; total: number } } = {
      GDAM: { buy: 0, sell: 0, total: 0 },
      DAM: { buy: 0, sell: 0, total: 0 },
      RTM: { buy: 0, sell: 0, total: 0 },
    };

    filteredData.forEach(txn => {
      const reportType = txn.report_type || '';
      let marketType = 'GDAM';
      if (reportType.includes('DAM') && !reportType.includes('GDAM')) marketType = 'DAM';
      if (reportType.includes('RTM')) marketType = 'RTM';

      const quantity = txn.quantity || 0;
      if (txn.type === 'BUY') {
        marketGroups[marketType].buy += quantity;
      } else {
        marketGroups[marketType].sell += quantity;
      }
      marketGroups[marketType].total += quantity;
    });

    return Object.entries(marketGroups)
      .filter(([_, data]) => data.total > 0)
      .map(([market, data]) => ({
        market,
        buy: Number(data.buy.toFixed(2)),
        sell: Number(data.sell.toFixed(2)),
        total: Number(data.total.toFixed(2)),
      }));
  }, [filteredData]);

  if (chartData.length === 0) {
    return (
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%' }}>
        <Typography color="text.secondary">No comparison data available</Typography>
      </Box>
    );
  }

  return (
    <ResponsiveContainer width="100%" height="90%">
      <BarChart data={chartData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="market" />
        <YAxis label={{ value: 'Quantity (MW)', angle: -90, position: 'insideLeft' }} />
        <Tooltip 
          formatter={(value: number, name: string) => {
            const displayName = name === 'buy' ? 'Buy' : name === 'sell' ? 'Sell' : 'Total';
            return [value.toFixed(2) + ' MW', displayName];
          }}
        />
        <Legend />
        <Bar dataKey="buy" fill={COLORS.BUY} name="Buy" stackId="a" />
        <Bar dataKey="sell" fill={COLORS.SELL} name="Sell" stackId="a" />
      </BarChart>
    </ResponsiveContainer>
  );
};

export default PortfolioComparisonChart;
