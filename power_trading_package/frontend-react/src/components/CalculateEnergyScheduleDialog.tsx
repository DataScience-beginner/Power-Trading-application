import { useState, FC } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Alert,
  Box,
  LinearProgress,
  Typography,
  List,
  ListItem,
  ListItemText,
  Chip,
} from '@mui/material';
import { Calculate as CalculateIcon, CheckCircle, Error, Info } from '@mui/icons-material';
import apiService from '../services/api';

interface CalculateDialogProps {
  open: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

const CalculateEnergyScheduleDialog: FC<CalculateDialogProps> = ({ open, onClose, onSuccess }) => {
  const [calculationDate, setCalculationDate] = useState<string>(
    new Date().toISOString().split('T')[0]
  );
  const [calculating, setCalculating] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleCalculate = async () => {
    setCalculating(true);
    setError(null);
    setResult(null);

    try {
      const response = await apiService.calculateEnergySchedule(calculationDate);
      setResult(response);

      if (response.status === 'ready' || response.status === 'calculation_ready') {
        setTimeout(() => {
          onSuccess();
        }, 2000);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to calculate energy schedule');
    } finally {
      setCalculating(false);
    }
  };

  const handleClose = () => {
    setResult(null);
    setError(null);
    onClose();
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'ready':
      case 'calculation_ready':
        return 'success';
      case 'missing_dor':
      case 'missing_sch':
      case 'missing_all':
        return 'warning';
      default:
        return 'info';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'ready':
      case 'calculation_ready':
        return <CheckCircle />;
      case 'missing_dor':
      case 'missing_sch':
      case 'missing_all':
        return <Error />;
      default:
        return <Info />;
    }
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <CalculateIcon color="primary" />
          Calculate Energy Schedule
        </Box>
      </DialogTitle>
      <DialogContent>
        <Box sx={{ pt: 2, display: 'flex', flexDirection: 'column', gap: 2 }}>
          <TextField
            label="Calculation Date"
            type="date"
            value={calculationDate}
            onChange={(e) => setCalculationDate(e.target.value)}
            fullWidth
            disabled={calculating}
            InputLabelProps={{ shrink: true }}
            helperText="System will use DOR from previous day and SCH from this date"
          />

          {calculating && <LinearProgress />}

          {error && <Alert severity="error">{error}</Alert>}

          {result && (
            <Box>
              <Alert
                severity={getStatusColor(result.status)}
                icon={getStatusIcon(result.status)}
                sx={{ mb: 2 }}
              >
                {result.message}
              </Alert>

              <Box sx={{ mb: 2 }}>
                <Typography variant="subtitle2" gutterBottom>
                  File Availability:
                </Typography>
                <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                  <Chip
                    label={`DOR Date: ${result.dor_date}`}
                    size="small"
                    color="primary"
                    variant="outlined"
                  />
                  <Chip
                    label={`SCH Date: ${result.sch_date}`}
                    size="small"
                    color="primary"
                    variant="outlined"
                  />
                  <Chip
                    label={`Files: ${result.files_found?.count_summary || '0+0'}`}
                    size="small"
                    color={result.status === 'ready' ? 'success' : 'warning'}
                  />
                </Box>
              </Box>

              {result.dor_files && result.dor_files.length > 0 && (
                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle2" gutterBottom>
                    DOR Files ({result.dor_files.length}):
                  </Typography>
                  <List dense>
                    {result.dor_files.map((file: any, idx: number) => (
                      <ListItem key={idx}>
                        <ListItemText
                          primary={file.filename}
                          secondary={`${file.market_type} - ${file.report_type}`}
                        />
                      </ListItem>
                    ))}
                  </List>
                </Box>
              )}

              {result.sch_files && result.sch_files.length > 0 && (
                <Box>
                  <Typography variant="subtitle2" gutterBottom>
                    SCH Files ({result.sch_files.length}):
                  </Typography>
                  <List dense>
                    {result.sch_files.map((file: any, idx: number) => (
                      <ListItem key={idx}>
                        <ListItemText
                          primary={file.filename}
                          secondary={`${file.market_type} - ${file.report_type}`}
                        />
                      </ListItem>
                    ))}
                  </List>
                </Box>
              )}

              {result.excel_file && (
                <Alert severity="info" sx={{ mt: 2 }}>
                  Excel File: {result.excel_file}
                </Alert>
              )}
            </Box>
          )}
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={handleClose} disabled={calculating}>
          Close
        </Button>
        <Button
          onClick={handleCalculate}
          variant="contained"
          disabled={calculating}
          startIcon={<CalculateIcon />}
        >
          {calculating ? 'Validating...' : 'Calculate'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default CalculateEnergyScheduleDialog;
