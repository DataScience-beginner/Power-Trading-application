import { FC, useEffect, useState } from 'react';
import {
  Box,
  Typography,
  Paper,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  CircularProgress,
  Divider,
} from '@mui/material';
import EnergyScheduleSummaryCards from '../components/EnergyScheduleSummaryCards';
import MonthlyTrendChart from '../components/MonthlyTrendChart';
import EnergyScheduleDayTable from '../components/EnergyScheduleDayTable';
import { apiService } from '../services/api';
import type { EnergyScheduleMonth, EnergyScheduleDay } from '../types/energySchedule';

const EnergySchedule: FC = () => {
  const [months, setMonths] = useState<EnergyScheduleMonth[]>([]);
  const [days, setDays] = useState<EnergyScheduleDay[]>([]);
  const [selectedMonth, setSelectedMonth] = useState<number | ''>('');
  const [selectedYear, setSelectedYear] = useState<number>(2026);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch month sheets on component mount
  useEffect(() => {
    fetchMonths();
  }, []);

  // Fetch days when month/year changes
  useEffect(() => {
    if (selectedMonth !== '') {
      fetchDays(selectedYear, selectedMonth as number);
    }
  }, [selectedMonth, selectedYear]);

  const fetchMonths = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await apiService.getEnergyScheduleMonths();
      setMonths(data);

      // Auto-select first month if available
      if (data.length > 0 && selectedMonth === '') {
        setSelectedMonth(data[0].month);
        setSelectedYear(data[0].year);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to fetch energy schedule months');
      console.error('Error fetching months:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchDays = async (year: number, month: number) => {
    try {
      setLoading(true);
      setError(null);
      
      // Calculate start and end dates for the month
      const startDate = new Date(year, month - 1, 1).toISOString().split('T')[0];
      const endDate = new Date(year, month, 0).toISOString().split('T')[0];
      
      const data = await apiService.getEnergyScheduleDays({
        start_date: startDate,
        end_date: endDate,
      });
      setDays(data);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch daily energy schedule data');
      console.error('Error fetching days:', err);
    } finally {
      setLoading(false);
    }
  };

  // Get current month summary
  const currentMonthData = months.find(
    (m) => m.month === selectedMonth && m.year === selectedYear
  );

  // Available years from months data
  const availableYears = Array.from(new Set(months.map((m) => m.year))).sort((a, b) => b - a);

  // Available months for selected year
  const availableMonths = months
    .filter((m) => m.year === selectedYear)
    .sort((a, b) => a.month - b.month);

  const monthNames = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ];

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" fontWeight="bold">
            Energy Schedule Analytics
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
            Monitor CTU losses, energy savings, and cost optimization
          </Typography>
        </Box>

        <Box sx={{ display: 'flex', gap: 2 }}>
          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Year</InputLabel>
            <Select
              value={selectedYear}
              label="Year"
              onChange={(e) => {
                setSelectedYear(e.target.value as number);
                setSelectedMonth(''); // Reset month selection
              }}
            >
              {availableYears.length === 0 ? (
                <MenuItem value={2026}>2026</MenuItem>
              ) : (
                availableYears.map((year) => (
                  <MenuItem key={year} value={year}>
                    {year}
                  </MenuItem>
                ))
              )}
            </Select>
          </FormControl>

          <FormControl size="small" sx={{ minWidth: 150 }}>
            <InputLabel>Month</InputLabel>
            <Select
              value={selectedMonth}
              label="Month"
              onChange={(e) => setSelectedMonth(e.target.value as number)}
            >
              {availableMonths.length === 0 ? (
                <MenuItem value="">No data available</MenuItem>
              ) : (
                availableMonths.map((monthData) => (
                  <MenuItem key={monthData.id} value={monthData.month}>
                    {monthData.month_name} ({monthData.total_days_completed} days)
                  </MenuItem>
                ))
              )}
            </Select>
          </FormControl>
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {loading && selectedMonth === '' ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
          <CircularProgress />
        </Box>
      ) : months.length === 0 ? (
        <Paper sx={{ p: 6, textAlign: 'center' }}>
          <Typography variant="h6" color="text.secondary" gutterBottom>
            No Energy Schedule Data Available
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Upload DOR (GDAM/DAM/RTM) and SCH files to generate energy schedule analytics
          </Typography>
        </Paper>
      ) : (
        <>
          {/* Summary Cards */}
          {currentMonthData && (
            <Box sx={{ mb: 3 }}>
              <EnergyScheduleSummaryCards
                totalEnergySavings={currentMonthData.total_energy_savings}
                averageCTULosses={currentMonthData.average_ctu_losses}
                totalCost={currentMonthData.total_cost}
                daysCompleted={currentMonthData.total_days_completed}
              />
            </Box>
          )}

          {/* Monthly Trend Chart */}
          <Box sx={{ mb: 3 }}>
            <MonthlyTrendChart days={days} />
          </Box>

          {/* Day-wise Details Table */}
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Day-wise Energy Schedule
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              Detailed breakdown of daily calculations and file status
            </Typography>
            <Divider sx={{ mb: 2 }} />
            {loading ? (
              <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
                <CircularProgress />
              </Box>
            ) : (
              <EnergyScheduleDayTable days={days} />
            )}
          </Paper>
        </>
      )}
    </Box>
  );
};

export default EnergySchedule;
