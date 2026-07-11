import { useEffect, FC, useState } from 'react';
import { 
  Grid, Box, Paper, Typography,
  FormControl, Select, MenuItem, SelectChangeEvent, Chip, Stack
} from '@mui/material';
import {
  Description as DescriptionIcon,
  Assignment as AssignmentIcon,
  Receipt as ReceiptIcon,
  AccountBalance as AccountBalanceIcon,
  TrendingUp as TrendingUpIcon,
  Schedule as ScheduleIcon,
} from '@mui/icons-material';
import StatCard from '../components/StatCard';
import TransactionsTable from '../components/TransactionsTable';
import HourlyChart from '../components/HourlyChart';
import PortfolioComparisonChart from '../components/PortfolioComparisonChart';
import { useAppDispatch, useAppSelector } from '../hooks/useAppStore';
import { fetchAnalytics, fetchTransactions } from '../store/dashboardSlice';

type ViewMode = 'hourly' | 'daily' | 'weekly' | 'monthly';
type ReportType = 'all' | 'DOR' | 'SCH';
type MarketType = 'all' | 'GDAM' | 'DAM' | 'RTM';

const Dashboard: FC = () => {
  const dispatch = useAppDispatch();
  const { summary, filter, loading, transactions } = useAppSelector((state) => state.dashboard);
  const [viewMode, setViewMode] = useState<ViewMode>('daily');
  const [reportType, setReportType] = useState<ReportType>('all');
  const [marketType, setMarketType] = useState<MarketType>('all');

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

  // Filter transactions based on report type, market type, and client selection
  const filteredTransactions = transactions.filter(txn => {
    // Client filter - check if entity_name matches the selected portfolio (which is actually entity_name)
    const clientMatch = !filter.portfolio || (txn as any).entity_name === filter.portfolio;
    const reportMatch = reportType === 'all' || txn.report_type?.includes(reportType);
    const marketMatch = marketType === 'all' || txn.report_type?.includes(marketType);
    return clientMatch && reportMatch && marketMatch;
  });

  // Calculate filtered summary
  const filteredSummary = {
    dor_files: filteredTransactions.filter(t => t.report_type?.includes('DOR')).length,
    sch_files: filteredTransactions.filter(t => t.report_type?.includes('SCH')).length,
    gdam_count: filteredTransactions.filter(t => t.report_type?.includes('GDAM')).length,
    dam_count: filteredTransactions.filter(t => t.report_type?.includes('DAM')).length,
    rtm_count: filteredTransactions.filter(t => t.report_type?.includes('RTM')).length,
    total_transactions: filteredTransactions.length,
    buy_transactions: filteredTransactions.filter(t => t.type === 'BUY').length,
    sell_transactions: filteredTransactions.filter(t => t.type === 'SELL').length,
    net_amount: filteredTransactions.reduce((sum, t) => {
      const amount = (t.quantity || 0) * (t.rate || 0);
      return t.type === 'BUY' ? sum - amount : sum + amount;
    }, 0),
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" fontWeight="bold">
          Dashboard Overview
        </Typography>
        
        <Stack direction="row" spacing={2} alignItems="center">
          {/* View Mode Toggle */}
          <FormControl size="small" sx={{ minWidth: 120 }}>
            <Select
              value={viewMode}
              onChange={(e: SelectChangeEvent) => setViewMode(e.target.value as ViewMode)}
              displayEmpty
            >
              <MenuItem value="hourly">Hourly</MenuItem>
              <MenuItem value="daily">Daily</MenuItem>
              <MenuItem value="weekly">Weekly</MenuItem>
              <MenuItem value="monthly">Monthly</MenuItem>
            </Select>
          </FormControl>

          {/* Report Type Filter */}
          <FormControl size="small" sx={{ minWidth: 100 }}>
            <Select
              value={reportType}
              onChange={(e: SelectChangeEvent) => setReportType(e.target.value as ReportType)}
              displayEmpty
            >
              <MenuItem value="all">All Reports</MenuItem>
              <MenuItem value="DOR">DOR Only</MenuItem>
              <MenuItem value="SCH">SCH Only</MenuItem>
            </Select>
          </FormControl>

          {/* Market Type Filter */}
          <FormControl size="small" sx={{ minWidth: 100 }}>
            <Select
              value={marketType}
              onChange={(e: SelectChangeEvent) => setMarketType(e.target.value as MarketType)}
              displayEmpty
            >
              <MenuItem value="all">All Markets</MenuItem>
              <MenuItem value="GDAM">GDAM</MenuItem>
              <MenuItem value="DAM">DAM</MenuItem>
              <MenuItem value="RTM">RTM</MenuItem>
            </Select>
          </FormControl>
        </Stack>
      </Box>

      {/* Active Filters Display */}
      {(filter.portfolio || reportType !== 'all' || marketType !== 'all') && (
        <Box sx={{ mb: 2 }}>
          <Stack direction="row" spacing={1}>
            <Typography variant="body2" sx={{ mr: 1, alignSelf: 'center' }}>Active Filters:</Typography>
            {filter.portfolio && <Chip label={`Client: ${filter.portfolio}`} size="small" color="primary" />}
            {reportType !== 'all' && <Chip label={`Report: ${reportType}`} size="small" color="secondary" />}
            {marketType !== 'all' && <Chip label={`Market: ${marketType}`} size="small" color="info" />}
          </Stack>
        </Box>
      )}

      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={2.4}>
          <StatCard
            title="DOR Files"
            value={filteredSummary.dor_files}
            icon={<DescriptionIcon />}
            color="#3b82f6"
            subtitle="Day of Results"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={2.4}>
          <StatCard
            title="SCH Files"
            value={filteredSummary.sch_files}
            icon={<AssignmentIcon />}
            color="#10b981"
            subtitle="Scheduled Reports"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={2.4}>
          <StatCard
            title="Total Transactions"
            value={filteredSummary.total_transactions}
            icon={<ReceiptIcon />}
            color="#f59e0b"
            subtitle={`${filteredSummary.buy_transactions} Buy / ${filteredSummary.sell_transactions} Sell`}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={2.4}>
          <StatCard
            title="Net Amount"
            value={formatCurrency(filteredSummary.net_amount)}
            icon={<AccountBalanceIcon />}
            color={filteredSummary.net_amount >= 0 ? '#10b981' : '#ef4444'}
            subtitle="Total trading value"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={2.4}>
          <StatCard
            title="Market Split"
            value={`${filteredSummary.gdam_count}/${filteredSummary.dam_count}/${filteredSummary.rtm_count}`}
            icon={<TrendingUpIcon />}
            color="#8b5cf6"
            subtitle="GDAM/DAM/RTM"
          />
        </Grid>
      </Grid>

      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2, height: 400 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6">
                {viewMode.charAt(0).toUpperCase() + viewMode.slice(1)} Distribution
              </Typography>
              <Chip 
                icon={<ScheduleIcon />} 
                label={viewMode.toUpperCase()} 
                size="small" 
                color="primary" 
                variant="outlined"
              />
            </Box>
            <HourlyChart viewMode={viewMode} filteredData={filteredTransactions} />
          </Paper>
        </Grid>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2, height: 400 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6">
                Market Type Comparison
              </Typography>
              <Stack direction="row" spacing={0.5}>
                <Chip label={`GDAM: ${filteredSummary.gdam_count}`} size="small" color="primary" />
                <Chip label={`DAM: ${filteredSummary.dam_count}`} size="small" color="secondary" />
                <Chip label={`RTM: ${filteredSummary.rtm_count}`} size="small" color="success" />
              </Stack>
            </Box>
            <PortfolioComparisonChart filteredData={filteredTransactions} reportType={reportType} />
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
