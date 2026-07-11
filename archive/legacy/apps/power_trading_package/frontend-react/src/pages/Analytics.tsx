import { useEffect, FC, useState } from 'react';
import {
  Grid,
  Box,
  Paper,
  Typography,
  FormControl,
  Select,
  MenuItem,
  SelectChangeEvent,
  Chip,
  Card,
  CardContent,
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  ShowChart as ShowChartIcon,
  PieChart as PieChartIcon,
  BarChart as BarChartIcon,
} from '@mui/icons-material';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  Area,
  AreaChart,
} from 'recharts';
import { useAppDispatch, useAppSelector } from '../hooks/useAppStore';
import { fetchTransactions, fetchAnalytics } from '../store/dashboardSlice';

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'];

const Analytics: FC = () => {
  const dispatch = useAppDispatch();
  const { transactions, filter } = useAppSelector((state) => state.dashboard);
  const [timeRange, setTimeRange] = useState<'7d' | '15d' | '30d'>('15d');

  useEffect(() => {
    dispatch(fetchAnalytics({ startDate: filter.startDate, endDate: filter.endDate }));
    dispatch(fetchTransactions(filter));
  }, [dispatch, filter]);

  // Filter transactions by client if selected
  const filteredTransactions = transactions.filter(txn => {
    const clientMatch = !filter.portfolio || (txn as any).entity_name === filter.portfolio;
    return clientMatch;
  });

  // Calculate analytics from filtered transactions
  const analytics = {
    // Volume by market type
    marketVolume: [
      {
        name: 'GDAM',
        volume: filteredTransactions
          .filter((t) => t.report_type?.includes('GDAM'))
          .reduce((sum, t) => sum + (t.quantity || 0), 0),
      },
      {
        name: 'DAM',
        volume: filteredTransactions
          .filter((t) => t.report_type?.includes('DAM') && !t.report_type?.includes('GDAM'))
          .reduce((sum, t) => sum + (t.quantity || 0), 0),
      },
      {
        name: 'RTM',
        volume: filteredTransactions
          .filter((t) => t.report_type?.includes('RTM'))
          .reduce((sum, t) => sum + (t.quantity || 0), 0),
      },
    ],

    // Daily volume trend
    dailyVolume: (() => {
      const dailyData: { [key: string]: { buy: number; sell: number; schedule: number } } = {};
      filteredTransactions.forEach((t) => {
        const date = new Date(t.date).toLocaleDateString('en-IN', { day: '2-digit', month: 'short' });
        if (!dailyData[date]) dailyData[date] = { buy: 0, sell: 0, schedule: 0 };

        const quantity = t.quantity || 0;
        if (t.type === 'BUY') dailyData[date].buy += quantity;
        else if (t.type === 'SELL') dailyData[date].sell += quantity;
        else dailyData[date].schedule += quantity;
      });

      return Object.entries(dailyData)
        .map(([date, data]) => ({ date, ...data }))
        .slice(0, timeRange === '7d' ? 7 : timeRange === '15d' ? 15 : 30);
    })(),

    // Hourly patterns
    hourlyPattern: (() => {
      const hourlyData: { [key: string]: number } = {};
      filteredTransactions.forEach((t) => {
        if (t.time_slot) {
          const hour = t.time_slot.split(':')[0];
          if (!hourlyData[hour]) hourlyData[hour] = 0;
          hourlyData[hour] += t.quantity || 0;
        }
      });

      return Object.entries(hourlyData)
        .map(([hour, volume]) => ({
          hour: `${hour}:00`,
          volume: Number(volume.toFixed(2)),
        }))
        .sort((a, b) => a.hour.localeCompare(b.hour));
    })(),

    // Report type distribution
    reportDistribution: [
      {
        name: 'DOR Files',
        value: filteredTransactions.filter((t) => t.report_type?.includes('DOR')).length,
      },
      {
        name: 'SCH Files',
        value: filteredTransactions.filter((t) => t.report_type?.includes('SCH')).length,
      },
    ],

    // Price analysis by market
    priceAnalysis: [
      {
        market: 'GDAM',
        avgRate: filteredTransactions
          .filter((t) => t.report_type?.includes('GDAM') && t.rate)
          .reduce((sum, t, _, arr) => sum + (t.rate || 0) / arr.length, 0),
        minRate: Math.min(
          ...filteredTransactions.filter((t) => t.report_type?.includes('GDAM') && t.rate).map((t) => t.rate || 0)
        ),
        maxRate: Math.max(
          ...filteredTransactions.filter((t) => t.report_type?.includes('GDAM') && t.rate).map((t) => t.rate || 0)
        ),
      },
      {
        market: 'DAM',
        avgRate: filteredTransactions
          .filter((t) => t.report_type?.includes('DAM') && !t.report_type?.includes('GDAM') && t.rate)
          .reduce((sum, t, _, arr) => sum + (t.rate || 0) / arr.length, 0),
        minRate: Math.min(
          ...filteredTransactions
            .filter((t) => t.report_type?.includes('DAM') && !t.report_type?.includes('GDAM') && t.rate)
            .map((t) => t.rate || 0)
        ),
        maxRate: Math.max(
          ...filteredTransactions
            .filter((t) => t.report_type?.includes('DAM') && !t.report_type?.includes('GDAM') && t.rate)
            .map((t) => t.rate || 0)
        ),
      },
      {
        market: 'RTM',
        avgRate: filteredTransactions
          .filter((t) => t.report_type?.includes('RTM') && t.rate)
          .reduce((sum, t, _, arr) => sum + (t.rate || 0) / arr.length, 0),
        minRate: Math.min(
          ...filteredTransactions.filter((t) => t.report_type?.includes('RTM') && t.rate).map((t) => t.rate || 0)
        ),
        maxRate: Math.max(
          ...filteredTransactions.filter((t) => t.report_type?.includes('RTM') && t.rate).map((t) => t.rate || 0)
        ),
      },
    ].filter((m) => !isNaN(m.avgRate) && isFinite(m.avgRate)),
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" fontWeight="bold">
          Advanced Analytics
        </Typography>

        <FormControl size="small" sx={{ minWidth: 120 }}>
          <Select value={timeRange} onChange={(e: SelectChangeEvent) => setTimeRange(e.target.value as any)}>
            <MenuItem value="7d">Last 7 Days</MenuItem>
            <MenuItem value="15d">Last 15 Days</MenuItem>
            <MenuItem value="30d">Last 30 Days</MenuItem>
          </Select>
        </FormControl>
      </Box>

      {/* Key Metrics Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <TrendingUpIcon sx={{ color: '#3b82f6', mr: 1 }} />
                <Typography variant="h6">Total Volume</Typography>
              </Box>
              <Typography variant="h4">
                {filteredTransactions.reduce((sum, t) => sum + (t.quantity || 0), 0).toFixed(2)} MW
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Across all markets
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <ShowChartIcon sx={{ color: '#10b981', mr: 1 }} />
                <Typography variant="h6">Avg Rate</Typography>
              </Box>
              <Typography variant="h4">
                ₹
                {filteredTransactions
                  .filter((t) => t.rate && t.rate > 0)
                  .reduce((sum, t, _, arr) => sum + (t.rate || 0) / arr.length, 0)
                  .toFixed(0)}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Per MWh
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <BarChartIcon sx={{ color: '#f59e0b', mr: 1 }} />
                <Typography variant="h6">Peak Hour</Typography>
              </Box>
              <Typography variant="h4">
                {analytics.hourlyPattern.length > 0
                  ? analytics.hourlyPattern.reduce((max, curr) => (curr.volume > max.volume ? curr : max)).hour
                  : 'N/A'}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Highest trading volume
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <PieChartIcon sx={{ color: '#8b5cf6', mr: 1 }} />
                <Typography variant="h6">Market Leader</Typography>
              </Box>
              <Typography variant="h4">
                {analytics.marketVolume.length > 0
                  ? analytics.marketVolume.reduce((max, curr) => (curr.volume > max.volume ? curr : max)).name
                  : 'N/A'}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                By volume
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Charts Row 1 */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 2, height: 400 }}>
            <Typography variant="h6" gutterBottom>
              Daily Volume Trends
            </Typography>
            <ResponsiveContainer width="100%" height="90%">
              <AreaChart data={analytics.dailyVolume}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis label={{ value: 'Volume (MW)', angle: -90, position: 'insideLeft' }} />
                <Tooltip />
                <Legend />
                <Area type="monotone" dataKey="buy" stackId="1" stroke="#ef4444" fill="#ef4444" name="Buy" />
                <Area type="monotone" dataKey="sell" stackId="1" stroke="#22c55e" fill="#22c55e" name="Sell" />
                <Area
                  type="monotone"
                  dataKey="schedule"
                  stackId="1"
                  stroke="#3b82f6"
                  fill="#3b82f6"
                  name="Schedule"
                />
              </AreaChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2, height: 400 }}>
            <Typography variant="h6" gutterBottom>
              Market Volume Distribution
            </Typography>
            <ResponsiveContainer width="100%" height="90%">
              <PieChart>
                <Pie
                  data={analytics.marketVolume}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="volume"
                >
                  {analytics.marketVolume.map((_, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>
      </Grid>

      {/* Charts Row 2 */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2, height: 400 }}>
            <Typography variant="h6" gutterBottom>
              Hourly Trading Pattern
            </Typography>
            <ResponsiveContainer width="100%" height="90%">
              <LineChart data={analytics.hourlyPattern}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="hour" angle={-45} textAnchor="end" height={80} />
                <YAxis label={{ value: 'Volume (MW)', angle: -90, position: 'insideLeft' }} />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="volume" stroke="#3b82f6" strokeWidth={2} dot={{ r: 3 }} />
              </LineChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2, height: 400 }}>
            <Typography variant="h6" gutterBottom>
              Price Analysis by Market
            </Typography>
            <ResponsiveContainer width="100%" height="90%">
              <BarChart data={analytics.priceAnalysis}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="market" />
                <YAxis label={{ value: 'Rate (₹/MWh)', angle: -90, position: 'insideLeft' }} />
                <Tooltip formatter={(value: number) => `₹${value.toFixed(0)}`} />
                <Legend />
                <Bar dataKey="minRate" fill="#10b981" name="Min Rate" />
                <Bar dataKey="avgRate" fill="#3b82f6" name="Avg Rate" />
                <Bar dataKey="maxRate" fill="#ef4444" name="Max Rate" />
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Analytics;
