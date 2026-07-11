import { FC, useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  Button,
  Card,
  CardContent,
  CardActions,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Alert,
  CircularProgress,
} from '@mui/material';
import {
  FileDownload as FileDownloadIcon,
  PictureAsPdf as PdfIcon,
  TableChart as ExcelIcon,
  Assessment as ReportIcon,
  CalendarMonth as CalendarIcon,
  TrendingUp as TrendingUpIcon,
  Schedule as ScheduleIcon,
} from '@mui/icons-material';
import { useAppSelector, useAppDispatch } from '../hooks/useAppStore';
import { fetchTransactions } from '../store/dashboardSlice';

const Reports: FC = () => {
  const dispatch = useAppDispatch();
  const { transactions, filter } = useAppSelector((state) => state.dashboard);
  const [generating, setGenerating] = useState(false);

  // Fetch transactions when component mounts
  useEffect(() => {
    dispatch(fetchTransactions(filter));
  }, [dispatch, filter]);

  const handleExport = async (type: 'excel' | 'pdf', reportType: 'daily' | 'energy-schedule') => {
    setGenerating(true);
    
    try {
      let url = '';
      const params = new URLSearchParams();
      
      // Add client filter if selected
      if (filter.portfolio) {
        params.append('portfolio_code', filter.portfolio);
      }
      
      if (reportType === 'daily') {
        // Add date filter (latest transaction date)
        if (transactions.length > 0) {
          const latestDate = transactions[0].date; // assuming sorted
          params.append('date', latestDate);
        }
        url = `http://localhost:8000/api/reports/daily-trading/${type}?${params.toString()}`;
      } else if (reportType === 'energy-schedule') {
        url = `http://localhost:8000/api/reports/energy-schedule/pdf?${params.toString()}`;
      }
      
      // Trigger download by opening URL in new window
      window.open(url, '_blank');
      
    } catch (error) {
      console.error('Error generating report:', error);
      alert('Failed to generate report. Please try again.');
    } finally {
      setGenerating(false);
    }
  };

  const reports = [
    {
      id: 'daily',
      title: 'Daily Trading Report',
      description: 'Summary of all transactions for a specific day',
      icon: <CalendarIcon sx={{ fontSize: 40, color: '#3b82f6' }} />,
      frequency: 'Daily',
      lastGenerated: 'Jan 15, 2026',
      records: transactions.length,
    },
    {
      id: 'energy-schedule',
      title: 'Energy Schedule Analysis',
      description: 'CTU losses, energy savings, and cost breakdown',
      icon: <ScheduleIcon sx={{ fontSize: 40, color: '#10b981' }} />,
      frequency: 'Monthly',
      lastGenerated: 'Jan 2026',
      records: 15,
    },
    {
      id: 'market-analysis',
      title: 'Market Analysis Report',
      description: 'GDAM, DAM, RTM comparison and trends',
      icon: <TrendingUpIcon sx={{ fontSize: 40, color: '#f59e0b' }} />,
      frequency: 'Weekly',
      lastGenerated: 'Week 2, 2026',
      records: transactions.length,
    },
    {
      id: 'financial',
      title: 'Financial Summary',
      description: 'Revenue, costs, and profit/loss statements',
      icon: <ReportIcon sx={{ fontSize: 40, color: '#8b5cf6' }} />,
      frequency: 'Monthly',
      lastGenerated: 'Dec 2025',
      records: transactions.length,
    },
  ];

  const recentReports = [
    { name: 'Daily_Trading_Report_2026-01-15.pdf', date: 'Jan 15, 2026', size: '2.4 MB', type: 'PDF' },
    { name: 'Energy_Schedule_January_2026.xlsx', date: 'Jan 15, 2026', size: '1.8 MB', type: 'Excel' },
    { name: 'Market_Analysis_Week2.pdf', date: 'Jan 14, 2026', size: '3.1 MB', type: 'PDF' },
    { name: 'Financial_Summary_Dec2025.xlsx', date: 'Jan 1, 2026', size: '2.7 MB', type: 'Excel' },
  ];

  return (
    <Box>
      <Typography variant="h4" fontWeight="bold" gutterBottom>
        Reports & Exports
      </Typography>

      <Alert severity="info" sx={{ mb: 3 }}>
        Generate and download comprehensive reports for analysis and compliance. All reports are based on your current data filters.
      </Alert>

      {/* Available Reports */}
      <Typography variant="h6" sx={{ mb: 2 }}>
        Available Reports
      </Typography>
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {reports.map((report) => (
          <Grid item xs={12} md={6} key={report.id}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'flex-start', mb: 2 }}>
                  <Box sx={{ mr: 2 }}>{report.icon}</Box>
                  <Box sx={{ flexGrow: 1 }}>
                    <Typography variant="h6" gutterBottom>
                      {report.title}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                      {report.description}
                    </Typography>
                    <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                      <Chip label={report.frequency} size="small" color="primary" />
                      <Chip label={`${report.records} records`} size="small" variant="outlined" />
                      <Chip label={`Last: ${report.lastGenerated}`} size="small" variant="outlined" />
                    </Box>
                  </Box>
                </Box>
              </CardContent>
              <CardActions sx={{ justifyContent: 'flex-end', px: 2, pb: 2 }}>
                <Button
                  startIcon={generating ? <CircularProgress size={16} /> : <ExcelIcon />}
                  variant="outlined"
                  size="small"
                  onClick={() => {
                    if (report.id === 'daily') {
                      handleExport('excel', 'daily');
                    }
                  }}
                  disabled={generating || report.id !== 'daily'}
                >
                  Export Excel
                </Button>
                <Button
                  startIcon={generating ? <CircularProgress size={16} /> : <PdfIcon />}
                  variant="contained"
                  size="small"
                  onClick={() => {
                    if (report.id === 'daily') {
                      handleExport('pdf', 'daily');
                    } else if (report.id === 'energy-schedule') {
                      handleExport('pdf', 'energy-schedule');
                    }
                  }}
                  disabled={generating || (report.id !== 'daily' && report.id !== 'energy-schedule')}
                >
                  Export PDF
                </Button>
              </CardActions>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Recent Reports */}
      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          Recently Generated Reports
        </Typography>
        <List>
          {recentReports.map((report, index) => (
            <div key={report.name}>
              <ListItem
                secondaryAction={
                  <Button startIcon={<FileDownloadIcon />} size="small">
                    Download
                  </Button>
                }
              >
                <ListItemIcon>
                  {report.type === 'PDF' ? (
                    <PdfIcon sx={{ color: '#ef4444', fontSize: 32 }} />
                  ) : (
                    <ExcelIcon sx={{ color: '#10b981', fontSize: 32 }} />
                  )}
                </ListItemIcon>
                <ListItemText
                  primary={report.name}
                  secondary={
                    <>
                      {report.date} • {report.size}
                    </>
                  }
                />
              </ListItem>
              {index < recentReports.length - 1 && <Divider />}
            </div>
          ))}
        </List>
      </Paper>

      {/* Custom Report Builder (Future) */}
      <Paper sx={{ p: 3, mt: 3, bgcolor: '#f8f9fa' }}>
        <Typography variant="h6" gutterBottom>
          Coming Soon: Custom Report Builder
        </Typography>
        <Typography variant="body2" color="text.secondary">
          • Select specific date ranges
          <br />
          • Choose custom metrics and columns
          <br />
          • Schedule automated report generation
          <br />
          • Email delivery to stakeholders
          <br />• Advanced filtering and grouping options
        </Typography>
      </Paper>
    </Box>
  );
};

export default Reports;
