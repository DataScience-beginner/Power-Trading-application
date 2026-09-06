import { ChangeEvent, FC, useEffect, useMemo, useState } from 'react';
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Divider,
  FormControl,
  Grid,
  InputLabel,
  MenuItem,
  Paper,
  Select,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  TextField,
  Typography,
} from '@mui/material';
import { PlayArrow as PlayArrowIcon, Refresh as RefreshIcon } from '@mui/icons-material';
import { apiService } from '../services/api';
import type { Client, Portfolio } from '../types';
import type { ExcelCalculationTraceResponse, ExcelSavedCalculationResultsResponse } from '../types/energySchedule';

const fmt = (value: unknown, digits = 2) => {
  if (value === null || value === undefined || value === '') return '-';
  if (typeof value === 'number') return value.toLocaleString(undefined, { maximumFractionDigits: digits });
  return String(value);
};

const statusColor = (ok: boolean) => (ok ? 'success' : 'warning');

const EnergyCalculationReview: FC = () => {
  const [clients, setClients] = useState<Client[]>([]);
  const [portfolioId, setPortfolioId] = useState<number | ''>('');
  const [year, setYear] = useState(2026);
  const [month, setMonth] = useState(1);
  const [day, setDay] = useState<number | ''>('');
  const [trace, setTrace] = useState<ExcelCalculationTraceResponse | null>(null);
  const [savedResults, setSavedResults] = useState<ExcelSavedCalculationResultsResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [loadingSaved, setLoadingSaved] = useState(false);
  const [running, setRunning] = useState(false);
  const [exporting, setExporting] = useState(false);
  const [savingConsumption, setSavingConsumption] = useState(false);
  const [consumptionDay, setConsumptionDay] = useState<number>(1);
  const [c1Kwh, setC1Kwh] = useState(0);
  const [c2Kwh, setC2Kwh] = useState(0);
  const [c4Kwh, setC4Kwh] = useState(0);
  const [c5Kwh, setC5Kwh] = useState(0);
  const [baseTariff, setBaseTariff] = useState<number | ''>('');
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    apiService.getClients()
      .then((items) => {
        setClients(items);
        const firstPortfolio = items.flatMap((client) => client.portfolios || [])[0];
        if (firstPortfolio) setPortfolioId(firstPortfolio.id);
      })
      .catch((err) => setError(err.message || 'Could not load clients'));
  }, []);

  useEffect(() => {
    if (day) setConsumptionDay(day);
  }, [day]);

  const portfolios = useMemo<Portfolio[]>(
    () => clients.flatMap((client) => client.portfolios || []),
    [clients]
  );

  const selectedPortfolio = portfolios.find((portfolio) => portfolio.id === portfolioId);
  const selectedClient = clients.find((client) =>
    (client.portfolios || []).some((portfolio) => portfolio.id === portfolioId)
  );

  const loadTrace = async () => {
    if (!portfolioId) return;
    try {
      setLoading(true);
      setError(null);
      const response = await apiService.getExcelEnergyScheduleTrace({
        portfolioId,
        year,
        month,
        day: day || null,
      });
      setTrace(response);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Could not load calculation trace');
    } finally {
      setLoading(false);
    }
  };

  const runCalculation = async () => {
    if (!portfolioId) return;
    try {
      setRunning(true);
      setError(null);
      await apiService.runExcelEnergyScheduleCalculation({
        portfolioId,
        year,
        month,
        day: day || null,
        mode: 'compare',
      });
      await loadTrace();
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Could not run calculation');
    } finally {
      setRunning(false);
    }
  };

  const loadSavedResults = async () => {
    if (!portfolioId) return;
    try {
      setLoadingSaved(true);
      setError(null);
      const response = await apiService.getExcelEnergyScheduleSavedResults({
        portfolioId,
        year,
        month,
        day: day || null,
        mode: 'compare',
      });
      setSavedResults(response);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Could not load saved calculation results');
    } finally {
      setLoadingSaved(false);
    }
  };

  const exportSavedReport = async (format: 'excel' | 'pdf') => {
    if (!portfolioId) return;
    try {
      setExporting(true);
      setError(null);
      const params = { portfolioId, year, month, mode: 'compare' as const };
      const blob = format === 'excel'
        ? await apiService.downloadExcelEnergyScheduleReport(params)
        : await apiService.downloadPdfEnergyScheduleReport(params);
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `Energy_Schedule_Savings_${year}_${String(month).padStart(2, '0')}.${format === 'excel' ? 'xlsx' : 'pdf'}`;
      link.click();
      URL.revokeObjectURL(url);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || `Could not export saved ${format.toUpperCase()} report`);
    } finally {
      setExporting(false);
    }
  };

  const consumptionDate = `${year}-${String(month).padStart(2, '0')}-${String(consumptionDay).padStart(2, '0')}`;

  const saveConsumption = async () => {
    if (!portfolioId) return;
    try {
      setSavingConsumption(true);
      setError(null);
      await apiService.saveEnergyScheduleConsumption({
        portfolio_id: portfolioId,
        consumption_date: consumptionDate,
        c1_kwh: c1Kwh,
        c2_kwh: c2Kwh,
        c4_kwh: c4Kwh,
        c5_kwh: c5Kwh,
        base_tariff_per_unit: baseTariff === '' ? null : baseTariff,
        source: 'admin-ui',
      });
      await loadTrace();
      await loadSavedResults();
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Could not save consumption details');
    } finally {
      setSavingConsumption(false);
    }
  };

  const uploadConsumption = async (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    event.target.value = '';
    if (!portfolioId || !file) return;
    try {
      setSavingConsumption(true);
      setError(null);
      await apiService.uploadEnergyScheduleConsumption(portfolioId, file);
      await loadTrace();
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Could not upload consumption details');
    } finally {
      setSavingConsumption(false);
    }
  };

  const sourceFiles = trace?.trace.source_files || [];
  const energyDays = trace?.trace.energy_schedule_days || [];
  const consumptionInputs = trace?.trace.consumption_inputs || [];
  const dailyOutputs = trace?.trace.daily_outputs || [];
  const savingsTotals = trace?.trace.savings_sheet?.totals || {};
  const slotRows = trace?.trace.slot_wise_consolidate?.rows || [];
  const savedDailyRows = savedResults?.results || [];
  const savedSummary = savedResults?.monthly_summary;
  const savedCompletion = savedSummary?.calculation_data?.completion || {};
  const savedAudit = savedSummary?.calculation_data?.audit || {};
  const missingCount = dailyOutputs.reduce((total, item) => total + (item.missing_inputs?.length || 0), 0);
  const completeDays = dailyOutputs.filter((item) => item.is_complete).length;

  return (
    <Box>
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" fontWeight="bold">Excel Calculation Review</Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
          Internal QA view for {selectedPortfolio?.portfolio_code || 'selected portfolio'} upload coverage, Energy Schedule inputs, Consumption Details, and calculated Excel outputs.
        </Typography>
      </Box>

      {error && <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>{error}</Alert>}

      <Paper sx={{ p: 2, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={4}>
            <FormControl fullWidth size="small">
              <InputLabel>Portfolio</InputLabel>
              <Select value={portfolioId} label="Portfolio" onChange={(event) => setPortfolioId(event.target.value as number)}>
                {portfolios.map((portfolio) => (
                  <MenuItem key={portfolio.id} value={portfolio.id}>
                    {portfolio.portfolio_code} - {portfolio.portfolio_name || selectedClient?.entity_name || 'Portfolio'}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={6} md={2}>
            <TextField fullWidth size="small" label="Year" type="number" value={year} onChange={(event) => setYear(Number(event.target.value))} />
          </Grid>
          <Grid item xs={6} md={2}>
            <TextField fullWidth size="small" label="Month" type="number" inputProps={{ min: 1, max: 12 }} value={month} onChange={(event) => setMonth(Number(event.target.value))} />
          </Grid>
          <Grid item xs={6} md={2}>
            <TextField fullWidth size="small" label="Day optional" type="number" inputProps={{ min: 1, max: 31 }} value={day} onChange={(event) => setDay(event.target.value ? Number(event.target.value) : '')} />
          </Grid>
          <Grid item xs={6} md={2}>
            <Stack direction="row" spacing={1}>
              <Button variant="outlined" startIcon={<RefreshIcon />} onClick={loadTrace} disabled={!portfolioId || loading || loadingSaved || running || exporting}>Trace</Button>
              <Button variant="outlined" onClick={loadSavedResults} disabled={!portfolioId || loading || loadingSaved || running || exporting}>Saved</Button>
              <Button variant="outlined" onClick={() => exportSavedReport('excel')} disabled={!portfolioId || loading || loadingSaved || running || exporting}>Excel</Button>
              <Button variant="outlined" onClick={() => exportSavedReport('pdf')} disabled={!portfolioId || loading || loadingSaved || running || exporting}>PDF</Button>
              <Button variant="contained" startIcon={<PlayArrowIcon />} onClick={runCalculation} disabled={!portfolioId || loading || loadingSaved || running || exporting}>Run</Button>
            </Stack>
          </Grid>
        </Grid>
      </Paper>

      <Paper sx={{ p: 2, mb: 3 }}>
        <Stack direction={{ xs: 'column', md: 'row' }} justifyContent="space-between" spacing={2} sx={{ mb: 2 }}>
          <Box>
            <Typography variant="h6">Consumption Details</Typography>
            <Typography variant="body2" color="text.secondary">
              Add one day manually or upload the monthly client consumption file used by the Excel calculation.
            </Typography>
          </Box>
          <Button variant="outlined" component="label" disabled={!portfolioId || savingConsumption}>
            Upload month
            <input hidden type="file" accept=".xlsx,.xls,.csv" onChange={uploadConsumption} />
          </Button>
        </Stack>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={6} md={1.5}>
            <TextField fullWidth size="small" label="Day" type="number" inputProps={{ min: 1, max: 31 }} value={consumptionDay} onChange={(event) => setConsumptionDay(Number(event.target.value) || 1)} />
          </Grid>
          <Grid item xs={6} md={2}>
            <TextField fullWidth size="small" label="Date" value={consumptionDate} InputProps={{ readOnly: true }} />
          </Grid>
          <Grid item xs={6} md={1.5}>
            <TextField fullWidth size="small" label="C1 kWh" type="number" value={c1Kwh} onChange={(event) => setC1Kwh(Number(event.target.value))} />
          </Grid>
          <Grid item xs={6} md={1.5}>
            <TextField fullWidth size="small" label="C2 kWh" type="number" value={c2Kwh} onChange={(event) => setC2Kwh(Number(event.target.value))} />
          </Grid>
          <Grid item xs={6} md={1.5}>
            <TextField fullWidth size="small" label="C4 kWh" type="number" value={c4Kwh} onChange={(event) => setC4Kwh(Number(event.target.value))} />
          </Grid>
          <Grid item xs={6} md={1.5}>
            <TextField fullWidth size="small" label="C5 kWh" type="number" value={c5Kwh} onChange={(event) => setC5Kwh(Number(event.target.value))} />
          </Grid>
          <Grid item xs={6} md={1.5}>
            <TextField fullWidth size="small" label="Base tariff" type="number" value={baseTariff} onChange={(event) => setBaseTariff(event.target.value === '' ? '' : Number(event.target.value))} />
          </Grid>
          <Grid item xs={6} md={1}>
            <Button fullWidth variant="contained" onClick={saveConsumption} disabled={!portfolioId || savingConsumption}>
              Save
            </Button>
          </Grid>
        </Grid>
      </Paper>

      {(loading || loadingSaved || running || exporting) && (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}><CircularProgress /></Box>
      )}

      {!loading && !loadingSaved && !running && !exporting && savedResults && (
        <Paper sx={{ p: 2, mb: 3 }}>
          <Stack direction={{ xs: 'column', md: 'row' }} justifyContent="space-between" spacing={2} sx={{ mb: 2 }}>
            <Box>
              <Typography variant="h6">Saved backend results</Typography>
              <Typography variant="body2" color="text.secondary">
                Latest persisted Excel-conversion rows for {savedResults.month}/{savedResults.year}; loading this does not recalculate.
              </Typography>
            </Box>
            <Chip
              color={savedSummary ? 'success' : 'warning'}
              label={savedSummary ? `Monthly summary saved: ${fmt(savedResults.latest_calculated_at)}` : 'No monthly summary saved'}
            />
          </Stack>
          <Grid container spacing={2} sx={{ mb: 2 }}>
            <Grid item xs={12} md={3}><Card><CardContent><Typography color="text.secondary">Saved daily rows</Typography><Typography variant="h5">{savedResults.count}</Typography></CardContent></Card></Grid>
            <Grid item xs={12} md={3}><Card><CardContent><Typography color="text.secondary">Saved complete days</Typography><Typography variant="h5">{fmt(savedCompletion.days_complete, 0)}/{fmt(savedCompletion.days_total, 0)}</Typography></CardContent></Card></Grid>
            <Grid item xs={12} md={3}><Card><CardContent><Typography color="text.secondary">Saved source files</Typography><Typography variant="h5">{savedAudit.source_files?.length || 0}</Typography></CardContent></Card></Grid>
            <Grid item xs={12} md={3}><Card><CardContent><Typography color="text.secondary">Saved saving</Typography><Typography variant="h5">{fmt(savedSummary?.net_profit_loss)}</Typography></CardContent></Card></Grid>
          </Grid>
          <Table size="small">
            <TableHead><TableRow><TableCell>Date</TableCell><TableCell>Type</TableCell><TableCell align="right">Scheduled MWh</TableCell><TableCell align="right">IEX cost</TableCell><TableCell align="right">Saving</TableCell></TableRow></TableHead>
            <TableBody>
              {savedDailyRows.map((row) => (
                <TableRow key={row.id}>
                  <TableCell>{row.calculation_date}</TableCell>
                  <TableCell>{row.calculation_type}</TableCell>
                  <TableCell align="right">{fmt(row.total_scheduled_mwh)}</TableCell>
                  <TableCell align="right">{fmt(row.total_cost)}</TableCell>
                  <TableCell align="right">{fmt(row.net_profit_loss)}</TableCell>
                </TableRow>
              ))}
              {!savedDailyRows.length && (
                <TableRow><TableCell colSpan={5}>No saved daily rows found. Run the calculation to persist results.</TableCell></TableRow>
              )}
            </TableBody>
          </Table>
        </Paper>
      )}

      {!loading && !loadingSaved && !running && !exporting && trace && (
        <>
          <Grid container spacing={2} sx={{ mb: 3 }}>
            <Grid item xs={12} md={3}><Card><CardContent><Typography color="text.secondary">Source files</Typography><Typography variant="h5">{sourceFiles.length}</Typography></CardContent></Card></Grid>
            <Grid item xs={12} md={3}><Card><CardContent><Typography color="text.secondary">Energy days</Typography><Typography variant="h5">{energyDays.length}</Typography></CardContent></Card></Grid>
            <Grid item xs={12} md={3}><Card><CardContent><Typography color="text.secondary">Complete outputs</Typography><Typography variant="h5">{completeDays}/{dailyOutputs.length}</Typography></CardContent></Card></Grid>
            <Grid item xs={12} md={3}><Card><CardContent><Typography color="text.secondary">Missing inputs</Typography><Typography variant="h5">{missingCount}</Typography></CardContent></Card></Grid>
          </Grid>

          <Paper sx={{ p: 2, mb: 3 }}>
            <Typography variant="h6">Daily calculated outputs</Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>Primary daily sheet outputs used by Savings Sheet.</Typography>
            <Divider sx={{ mb: 2 }} />
            <Table size="small">
              <TableHead><TableRow><TableCell>Date</TableCell><TableCell>Status</TableCell><TableCell>Missing inputs</TableCell><TableCell align="right">B44 IEX</TableCell><TableCell align="right">B45 IEX/unit</TableCell><TableCell align="right">B46 EB</TableCell><TableCell align="right">B47 EB/unit</TableCell><TableCell align="right">Saving</TableCell></TableRow></TableHead>
              <TableBody>
                {dailyOutputs.map((row) => (
                  <TableRow key={row.trading_date}>
                    <TableCell>{row.trading_date}</TableCell>
                    <TableCell><Chip size="small" color={statusColor(row.is_complete)} label={row.is_complete ? 'Complete' : 'Incomplete'} /></TableCell>
                    <TableCell>{row.missing_inputs.length ? row.missing_inputs.join(', ') : '-'}</TableCell>
                    <TableCell align="right">{fmt(row.b44_iex_price)}</TableCell>
                    <TableCell align="right">{fmt(row.b45_iex_price_per_unit, 4)}</TableCell>
                    <TableCell align="right">{fmt(row.b46_eb_price)}</TableCell>
                    <TableCell align="right">{fmt(row.b47_eb_price_per_unit, 4)}</TableCell>
                    <TableCell align="right">{fmt(row.cost_saving)}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </Paper>

          <Grid container spacing={2} sx={{ mb: 3 }}>
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 2 }}>
                <Typography variant="h6">Savings Sheet totals</Typography>
                <Table size="small"><TableBody>
                  {Object.entries(savingsTotals).map(([key, value]) => (
                    <TableRow key={key}><TableCell>{key.replace(/_/g, ' ')}</TableCell><TableCell align="right">{fmt(value, 4)}</TableCell></TableRow>
                  ))}
                </TableBody></Table>
              </Paper>
            </Grid>
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 2 }}>
                <Typography variant="h6">Slot Wise Consolidate</Typography>
                <Table size="small">
                  <TableHead><TableRow><TableCell>Slot</TableCell><TableCell align="right">Consumption kWh</TableCell><TableCell align="right">IEX delivered kWh</TableCell><TableCell align="right">Balance kWh</TableCell></TableRow></TableHead>
                  <TableBody>
                    {slotRows.map((row) => (
                      <TableRow key={row.slot}><TableCell>{row.slot}</TableCell><TableCell align="right">{fmt(row.consumption_kwh)}</TableCell><TableCell align="right">{fmt(row.iex_delivered_kwh)}</TableCell><TableCell align="right">{fmt(row.balance_kwh)}</TableCell></TableRow>
                    ))}
                  </TableBody>
                </Table>
              </Paper>
            </Grid>
          </Grid>

          <Paper sx={{ p: 2 }}>
            <Typography variant="h6">Input trace</Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              Upload coverage and Consumption Details used by the backend calculation.
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <Typography fontWeight={600} sx={{ mb: 1 }}>Source files</Typography>
                <Table size="small">
                  <TableHead><TableRow><TableCell>Date</TableCell><TableCell>Type</TableCell><TableCell align="right">Rows</TableCell></TableRow></TableHead>
                  <TableBody>{sourceFiles.map((file) => <TableRow key={file.id}><TableCell>{file.trading_date}</TableCell><TableCell>{file.report_type}</TableCell><TableCell align="right">{file.transaction_count}</TableCell></TableRow>)}</TableBody>
                </Table>
              </Grid>
              <Grid item xs={12} md={6}>
                <Typography fontWeight={600} sx={{ mb: 1 }}>Consumption Details</Typography>
                <Table size="small">
                  <TableHead><TableRow><TableCell>Date</TableCell><TableCell>Source</TableCell><TableCell align="right">C1</TableCell><TableCell align="right">C2</TableCell><TableCell align="right">C4</TableCell><TableCell align="right">C5</TableCell></TableRow></TableHead>
                  <TableBody>{consumptionInputs.map((item) => <TableRow key={item.trading_date}><TableCell>{item.trading_date}</TableCell><TableCell>{item.source || '-'}</TableCell><TableCell align="right">{fmt(item.c1_kwh)}</TableCell><TableCell align="right">{fmt(item.c2_kwh)}</TableCell><TableCell align="right">{fmt(item.c4_kwh)}</TableCell><TableCell align="right">{fmt(item.c5_kwh)}</TableCell></TableRow>)}</TableBody>
                </Table>
              </Grid>
            </Grid>
          </Paper>
        </>
      )}

      {!loading && !loadingSaved && !exporting && !trace && !savedResults && (
        <Alert severity="info">Select a portfolio and click Trace to inspect existing data, Saved to load persisted results, Export to download the saved monthly report, or Run to calculate and refresh both views.</Alert>
      )}
    </Box>
  );
};

export default EnergyCalculationReview;
