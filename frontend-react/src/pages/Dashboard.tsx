import { useEffect, FC } from 'react';
import { Grid, Box, Paper, Typography } from '@mui/material';
import {
  Description as DescriptionIcon,
  Assignment as AssignmentIcon,
  Receipt as ReceiptIcon,
  AccountBalance as AccountBalanceIcon,
} from '@mui/icons-material';
import StatCard from '../components/StatCard';
import TransactionsTable from '../components/TransactionsTable';
import HourlyChart from '../components/HourlyChart';
import PortfolioComparisonChart from '../components/PortfolioComparisonChart';
import { useAppDispatch, useAppSelector } from '../hooks/useAppStore';
import { fetchAnalytics, fetchTransactions } from '../store/dashboardSlice';

const Dashboard: FC = () => {
  const dispatch = useAppDispatch();
  const { summary, filter, loading } = useAppSelector((state) => state.dashboard);

  useEffect(() => {
    dispatch(fetchAnalytics({ startDate: filter.startDate, endDate: filter.endDate }));
    dispatch(fetchTransactions(filter));
  }, [dispatch, filter]);

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 2,
    }).format(value);
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom fontWeight="bold">
        Dashboard Overview
      </Typography>

      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="DOR Files"
            value={summary?.dor_files || 0}
            icon={<DescriptionIcon />}
            color="#3b82f6"
            subtitle="Day of Results"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="SCH Files"
            value={summary?.sch_files || 0}
            icon={<AssignmentIcon />}
            color="#10b981"
            subtitle="Scheduled Reports"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Transactions"
            value={summary?.total_transactions || 0}
            icon={<ReceiptIcon />}
            color="#f59e0b"
            subtitle={`${summary?.buy_transactions || 0} Buy / ${summary?.sell_transactions || 0} Sell`}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Net Amount"
            value={formatCurrency(summary?.net_amount || 0)}
            icon={<AccountBalanceIcon />}
            color={summary && summary.net_amount >= 0 ? '#10b981' : '#ef4444'}
            subtitle="Total trading value"
          />
        </Grid>
      </Grid>

      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2, height: 400 }}>
            <Typography variant="h6" gutterBottom>
              Hourly Distribution
            </Typography>
            <HourlyChart />
          </Paper>
        </Grid>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2, height: 400 }}>
            <Typography variant="h6" gutterBottom>
              DOR vs SCH Comparison
            </Typography>
            <PortfolioComparisonChart />
          </Paper>
        </Grid>
      </Grid>

      <Paper sx={{ p: 2 }}>
        <Typography variant="h6" gutterBottom>
          Recent Transactions
        </Typography>
        <TransactionsTable />
      </Paper>
    </Box>
  );
};

export default Dashboard;
