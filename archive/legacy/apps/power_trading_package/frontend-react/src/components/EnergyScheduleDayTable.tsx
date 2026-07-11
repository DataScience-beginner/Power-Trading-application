import { FC } from 'react';
import {
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Typography,
  Box,
  Tooltip,
  IconButton,
} from '@mui/material';
import {
  CheckCircle as CheckCircleIcon,
  Cancel as CancelIcon,
  Info as InfoIcon,
} from '@mui/icons-material';
import type { EnergyScheduleDay } from '../types/energySchedule';

interface EnergyScheduleDayTableProps {
  days: EnergyScheduleDay[];
  onDayClick?: (day: EnergyScheduleDay) => void;
}

const EnergyScheduleDayTable: FC<EnergyScheduleDayTableProps> = ({ days, onDayClick }) => {
  const formatCurrency = (value: number | null) => {
    if (value === null) return '-';
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 2,
    }).format(value);
  };

  const formatMWh = (value: number | null) => {
    if (value === null) return '-';
    return `${value.toFixed(2)} MWh`;
  };

  const formatPercent = (value: number | null) => {
    if (value === null) return '-';
    return `${value.toFixed(2)}%`;
  };

  const FileStatusIcon: FC<{ present: boolean }> = ({ present }) => {
    return present ? (
      <CheckCircleIcon sx={{ fontSize: 16, color: 'success.main' }} />
    ) : (
      <CancelIcon sx={{ fontSize: 16, color: 'error.main' }} />
    );
  };

  return (
    <TableContainer component={Paper} sx={{ maxHeight: 600 }}>
      <Table stickyHeader size="small">
        <TableHead>
          <TableRow>
            <TableCell>Trading Date</TableCell>
            <TableCell align="center">
              <Tooltip title="File Status: GDAM / DAM / RTM / SCH">
                <Box>Files</Box>
              </Tooltip>
            </TableCell>
            <TableCell align="right">Total Scheduled</TableCell>
            <TableCell align="right">CTU Losses</TableCell>
            <TableCell align="right">Energy Savings</TableCell>
            <TableCell align="right">NLDC Fees</TableCell>
            <TableCell align="right">CTU Charges</TableCell>
            <TableCell align="right">Total Cost</TableCell>
            <TableCell align="center">Status</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {days.length === 0 ? (
            <TableRow>
              <TableCell colSpan={9} align="center">
                <Typography variant="body2" color="text.secondary" sx={{ py: 4 }}>
                  No energy schedule data available
                </Typography>
              </TableCell>
            </TableRow>
          ) : (
            days.map((day) => (
              <TableRow
                key={day.id}
                hover
                onClick={() => onDayClick?.(day)}
                sx={{ cursor: onDayClick ? 'pointer' : 'default' }}
              >
                <TableCell>
                  <Typography variant="body2" fontWeight="medium">
                    {new Date(day.trading_date).toLocaleDateString('en-IN', {
                      day: '2-digit',
                      month: 'short',
                      year: 'numeric',
                    })}
                  </Typography>
                </TableCell>
                <TableCell align="center">
                  <Box sx={{ display: 'flex', gap: 0.5, justifyContent: 'center' }}>
                    <Tooltip title="GDAM">
                      <Box>
                        <FileStatusIcon present={day.has_gdam_data} />
                      </Box>
                    </Tooltip>
                    <Tooltip title="DAM">
                      <Box>
                        <FileStatusIcon present={day.has_dam_data} />
                      </Box>
                    </Tooltip>
                    <Tooltip title="RTM">
                      <Box>
                        <FileStatusIcon present={day.has_rtm_data} />
                      </Box>
                    </Tooltip>
                    <Tooltip title="SCH">
                      <Box>
                        <FileStatusIcon present={day.has_sch_data} />
                      </Box>
                    </Tooltip>
                  </Box>
                </TableCell>
                <TableCell align="right">
                  <Typography variant="body2">{formatMWh(day.total_scheduled_mwh)}</Typography>
                </TableCell>
                <TableCell align="right">
                  <Box>
                    <Typography variant="body2">{formatMWh(day.ctu_losses_mwh)}</Typography>
                    <Typography variant="caption" color="text.secondary">
                      ({formatPercent(day.ctu_losses_percent)})
                    </Typography>
                  </Box>
                </TableCell>
                <TableCell align="right">
                  <Typography
                    variant="body2"
                    color={
                      day.energy_savings_mwh && day.energy_savings_mwh > 0
                        ? 'success.main'
                        : 'text.primary'
                    }
                    fontWeight={day.energy_savings_mwh && day.energy_savings_mwh > 0 ? 'bold' : 'normal'}
                  >
                    {formatMWh(day.energy_savings_mwh)}
                  </Typography>
                </TableCell>
                <TableCell align="right">
                  <Typography variant="body2">{formatCurrency(day.total_nldc_fees)}</Typography>
                </TableCell>
                <TableCell align="right">
                  <Typography variant="body2">{formatCurrency(day.total_ctu_charges)}</Typography>
                </TableCell>
                <TableCell align="right">
                  <Typography variant="body2" fontWeight="medium">
                    {formatCurrency(day.total_cost)}
                  </Typography>
                </TableCell>
                <TableCell align="center">
                  {day.is_calculated ? (
                    <Chip label="Complete" color="success" size="small" />
                  ) : (
                    <Chip label="Pending" color="warning" size="small" />
                  )}
                </TableCell>
              </TableRow>
            ))
          )}
        </TableBody>
      </Table>
    </TableContainer>
  );
};

export default EnergyScheduleDayTable;
