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
  Step,
  StepLabel,
  Stepper,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  TextField,
  Typography,
} from '@mui/material';
import {
  ArrowBack as ArrowBackIcon,
  ArrowForward as ArrowForwardIcon,
  CloudUpload as CloudUploadIcon,
  Download as DownloadIcon,
  PlayArrow as PlayArrowIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import { apiService } from '../services/api';
import type { Client, Portfolio } from '../types';
import type { EnergyScheduleMonth, EnergyWorkflowStatus, ExcelCalculationTraceResponse, ExcelSavedCalculationResultsResponse } from '../types/energySchedule';

const labels = ['Upload files', 'Validate data', 'Consumption', 'Calculate', 'Review & export'];

const fmt = (value: unknown, digits = 2) => {
  if (value === null || value === undefined || value === '') return '-';
  if (typeof value === 'number') return value.toLocaleString(undefined, { maximumFractionDigits: digits });
  return String(value);
};

const chipColor = (status?: string) => {
  if (status === 'complete' || status === 'ready') return 'success';
  if (status === 'partial') return 'warning';
  return 'default';
};

const EnergyWorkflow: FC = () => {
  const [clients, setClients] = useState<Client[]>([]);
  const [portfolioId, setPortfolioId] = useState<number | ''>('');
  const [monthPortfolios, setMonthPortfolios] = useState<Portfolio[]>([]);
  const [year, setYear] = useState(2026);
  const [month, setMonth] = useState(1);
  const [activeStep, setActiveStep] = useState(0);
  const [status, setStatus] = useState<EnergyWorkflowStatus | null>(null);
  const [trace, setTrace] = useState<ExcelCalculationTraceResponse | null>(null);
  const [saved, setSaved] = useState<ExcelSavedCalculationResultsResponse | null>(null);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [consumptionDay, setConsumptionDay] = useState(1);
  const [c1Kwh, setC1Kwh] = useState(0);
  const [c2Kwh, setC2Kwh] = useState(0);
  const [c4Kwh, setC4Kwh] = useState(0);
  const [c5Kwh, setC5Kwh] = useState(0);
  const [baseTariff, setBaseTariff] = useState<number | ''>('');

  useEffect(() => {
    const loadPortfolioOptions = async () => {
      try {
        const [clientItems, monthItems] = await Promise.all([
          apiService.getClients(),
          apiService.getEnergyScheduleMonths(),
        ]);
        setClients(clientItems);
        const clientPortfolios = clientItems.flatMap((client) => client.portfolios || []);
        const fallbackPortfolios = Array.from(
          new Map(
            (monthItems as EnergyScheduleMonth[]).map((item) => [
              item.portfolio_id,
              {
                id: item.portfolio_id,
                client_id: 0,
                portfolio_code: `Portfolio ${item.portfolio_id}`,
                portfolio_name: `${item.month_name || 'Energy Schedule'} data`,
              } as Portfolio,
            ])
          ).values()
        );
        setMonthPortfolios(fallbackPortfolios);
        const firstPortfolio = clientPortfolios[0] || fallbackPortfolios[0];
        if (firstPortfolio) setPortfolioId(firstPortfolio.id);
      } catch (err: any) {
        setError(err.message || 'Could not load portfolio options');
      }
    };
    loadPortfolioOptions();
  }, []);

  const portfolios = useMemo<Portfolio[]>(() => {
    const byId = new Map<number, Portfolio>();
    clients.flatMap((client) => client.portfolios || []).forEach((portfolio) => byId.set(portfolio.id, portfolio));
    monthPortfolios.forEach((portfolio) => { if (!byId.has(portfolio.id)) byId.set(portfolio.id, portfolio); });
    return Array.from(byId.values());
  }, [clients, monthPortfolios]);
  const selectedPortfolio = portfolios.find((portfolio) => portfolio.id === portfolioId);
  const selectedClient = clients.find((client) => (client.portfolios || []).some((portfolio) => portfolio.id === portfolioId));
  const consumptionDate = `${year}-${String(month).padStart(2, '0')}-${String(consumptionDay).padStart(2, '0')}`;

  const refresh = async () => {
    if (!portfolioId) return;
    setBusy(true);
    setError(null);
    try {
      const [workflowResult, traceResult, savedResult] = await Promise.all([
        apiService.getEnergyScheduleWorkflowStatus({ portfolioId, year, month, mode: 'compare' }),
        apiService.getExcelEnergyScheduleTrace({ portfolioId, year, month }),
        apiService.getExcelEnergyScheduleSavedResults({ portfolioId, year, month, mode: 'compare' }),
      ]);
      setStatus(workflowResult);
      setTrace(traceResult);
      setSaved(savedResult);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Could not refresh workflow');
    } finally {
      setBusy(false);
    }
  };

  useEffect(() => {
    if (portfolioId) refresh();
  }, [portfolioId, year, month]);

  const uploadMarketFile = async (event: ChangeEvent<HTMLInputElement>, fileType: 'DOR' | 'SCH') => {
    const file = event.target.files?.[0];
    event.target.value = '';
    if (!file || !portfolioId) return;
    setBusy(true);
    setError(null);
    try {
      await apiService.uploadFile(file, fileType);
      setMessage(`${fileType} file uploaded. You can upload again if you need to replace or correct data.`);
      await refresh();
    } catch (err: any) {
      setError(err.response?.data?.detail || err.response?.data?.message || err.message || 'Upload failed');
    } finally {
      setBusy(false);
    }
  };

  const rebuildSchedule = async () => {
    if (!portfolioId) return;
    setBusy(true);
    setError(null);
    try {
      const result = await apiService.rebuildEnergySchedule({ portfolioId, year, month });
      setMessage(`Energy Schedule refreshed: ${result.complete_days || 0}/${result.days_processed || 0} uploaded days complete.`);
      await refresh();
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Could not validate Energy Schedule');
    } finally {
      setBusy(false);
    }
  };

  const seedMockWorkflow = async () => {
    if (!portfolioId) return;
    setBusy(true);
    setError(null);
    try {
      const result = await apiService.seedEnergyScheduleWorkflowDemo({ portfolioId, year, month, days: 3 });
      setMessage(`Mock workflow data ready: ${result.days_seeded || 0} day(s), ${result.daily_files_created || 0} new file records, ${result.transactions_created || 0} new rows.`);
      await refresh();
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Could not create mock workflow data');
    } finally {
      setBusy(false);
    }
  };

  const uploadConsumption = async (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    event.target.value = '';
    if (!file || !portfolioId) return;
    setBusy(true);
    setError(null);
    try {
      const result = await apiService.uploadEnergyScheduleConsumption(portfolioId, file);
      setMessage(`Consumption uploaded: ${result.count} day(s) saved.`);
      await refresh();
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Could not upload consumption');
    } finally {
      setBusy(false);
    }
  };

  const saveConsumption = async () => {
    if (!portfolioId) return;
    setBusy(true);
    setError(null);
    try {
      await apiService.saveEnergyScheduleConsumption({
        portfolio_id: portfolioId,
        consumption_date: consumptionDate,
        c1_kwh: c1Kwh,
        c2_kwh: c2Kwh,
        c4_kwh: c4Kwh,
        c5_kwh: c5Kwh,
        base_tariff_per_unit: baseTariff === '' ? null : baseTariff,
        source: 'admin-workflow',
      });
      setMessage(`Consumption saved for ${consumptionDate}.`);
      await refresh();
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Could not save consumption');
    } finally {
      setBusy(false);
    }
  };

  const submitCalculation = async () => {
    if (!portfolioId) return;
    setBusy(true);
    setError(null);
    try {
      await apiService.runExcelEnergyScheduleCalculation({ portfolioId, year, month, mode: 'compare' });
      setMessage('Calculation submitted and saved. Review the outputs, then export Excel or PDF.');
      await refresh();
      setActiveStep(4);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Calculation failed');
    } finally {
      setBusy(false);
    }
  };

  const exportReport = async (format: 'excel' | 'pdf') => {
    if (!portfolioId) return;
    setBusy(true);
    setError(null);
    try {
      const blob = format === 'excel'
        ? await apiService.downloadExcelEnergyScheduleReport({ portfolioId, year, month, mode: 'compare' })
        : await apiService.downloadPdfEnergyScheduleReport({ portfolioId, year, month, mode: 'compare' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `Energy_Schedule_Savings_${year}_${String(month).padStart(2, '0')}.${format === 'excel' ? 'xlsx' : 'pdf'}`;
      link.click();
      URL.revokeObjectURL(url);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || `Could not export ${format.toUpperCase()}`);
    } finally {
      setBusy(false);
    }
  };

  const uploadRows = status?.steps.uploads?.rows || [];
  const energyRows = status?.steps.energy_schedule?.rows || [];
  const dailyOutputs = trace?.trace.daily_outputs || [];
  const sourceFiles = trace?.trace.source_files || [];
  const consumptionInputs = trace?.trace.consumption_inputs || [];
  const summary = saved?.monthly_summary;
  const completion = summary?.calculation_data?.completion || {};
  const savingsTotals = trace?.trace.savings_sheet?.totals || {};
  const stepStatuses = [
    status?.steps.uploads?.status,
    status?.steps.energy_schedule?.status,
    status?.steps.consumption?.status,
    status?.steps.calculation?.status,
    status?.steps.reports?.status,
  ];

  return (
    <Box>
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" fontWeight="bold">Calculation Workflow</Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
          Guided admin flow: upload, validate, enter consumption, calculate, review, then export.
        </Typography>
      </Box>

      {error && <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>{error}</Alert>}
      {message && <Alert severity="success" sx={{ mb: 2 }} onClose={() => setMessage(null)}>{message}</Alert>}
      {!portfolioId && <Alert severity="info" sx={{ mb: 2 }}>Select a portfolio first. Upload, validate, calculate, and export actions unlock after a portfolio is selected.</Alert>}

      <Paper sx={{ p: 2, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={4}>
            <FormControl fullWidth size="small">
              <InputLabel>Portfolio</InputLabel>
              <Select value={portfolioId} label="Portfolio" onChange={(event) => setPortfolioId(event.target.value as number)}>
                {portfolios.map((portfolio) => (
                  <MenuItem key={portfolio.id} value={portfolio.id}>{portfolio.portfolio_code} - {portfolio.portfolio_name || selectedClient?.entity_name || 'Portfolio'}</MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={6} md={2}><TextField fullWidth size="small" label="Year" type="number" value={year} onChange={(event) => setYear(Number(event.target.value))} /></Grid>
          <Grid item xs={6} md={2}><TextField fullWidth size="small" label="Month" type="number" inputProps={{ min: 1, max: 12 }} value={month} onChange={(event) => setMonth(Number(event.target.value))} /></Grid>
          <Grid item xs={12} md={4}>
            <Stack direction="row" spacing={1} justifyContent="flex-end">
              <Button variant="outlined" startIcon={<RefreshIcon />} onClick={refresh} disabled={!portfolioId || busy}>Refresh</Button>
              {busy && <CircularProgress size={28} />}
            </Stack>
          </Grid>
        </Grid>
      </Paper>

      <Paper sx={{ p: 3, mb: 3 }}>
        <Stepper activeStep={activeStep} alternativeLabel>
          {labels.map((label, index) => (
            <Step key={label} completed={stepStatuses[index] === 'complete' || stepStatuses[index] === 'ready'}>
              <StepLabel optional={<Chip size="small" label={stepStatuses[index] || 'waiting'} color={chipColor(stepStatuses[index]) as any} sx={{ mt: 1 }} />}>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>
      </Paper>

      {activeStep === 0 && (
        <Paper sx={{ p: 2, mb: 3 }}>
          <Typography variant="h6">Step 1: Upload files</Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Upload DOR market files and SCH schedule files here. If a wrong file was uploaded, upload the corrected file again for the same date/type.
          </Typography>
          <Stack direction={{ xs: 'column', md: 'row' }} spacing={1} sx={{ mb: 2 }}>
            <Button variant="contained" component="label" startIcon={<CloudUploadIcon />} disabled={!portfolioId || busy}>Upload DOR<input hidden type="file" accept=".xlsx,.xls,.csv" onChange={(event) => uploadMarketFile(event, 'DOR')} /></Button>
            <Button variant="contained" component="label" startIcon={<CloudUploadIcon />} disabled={!portfolioId || busy}>Upload SCH<input hidden type="file" accept=".xlsx,.xls,.csv" onChange={(event) => uploadMarketFile(event, 'SCH')} /></Button>
            <Button variant="outlined" onClick={seedMockWorkflow} disabled={!portfolioId || busy}>Create mock days 1-3</Button>
          </Stack>
          <Table size="small">
            <TableHead><TableRow><TableCell>Date</TableCell><TableCell>Available groups</TableCell><TableCell>Missing</TableCell><TableCell>Status</TableCell></TableRow></TableHead>
            <TableBody>{uploadRows.map((row: any) => <TableRow key={row.date}><TableCell>{row.date}</TableCell><TableCell>{(row.present_groups || []).join(', ') || '-'}</TableCell><TableCell>{(row.missing_groups || []).join(', ') || '-'}</TableCell><TableCell><Chip size="small" label={row.ready ? 'ready' : 'needs files'} color={row.ready ? 'success' : 'warning'} /></TableCell></TableRow>)}</TableBody>
          </Table>
        </Paper>
      )}

      {activeStep === 1 && (
        <Paper sx={{ p: 2, mb: 3 }}>
          <Typography variant="h6">Step 2: Validate Energy Schedule</Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>Build the backend Energy Schedule from uploaded files and inspect the generated day rows.</Typography>
          <Button variant="contained" startIcon={<RefreshIcon />} onClick={rebuildSchedule} disabled={!portfolioId || busy} sx={{ mb: 2 }}>Validate / rebuild Energy Schedule</Button>
          <Table size="small">
            <TableHead><TableRow><TableCell>Date</TableCell><TableCell>GDAM</TableCell><TableCell>DAM</TableCell><TableCell>RTM</TableCell><TableCell>SCH</TableCell><TableCell align="right">Scheduled MWh</TableCell><TableCell align="right">Cost</TableCell></TableRow></TableHead>
            <TableBody>{energyRows.map((row: any) => <TableRow key={row.date}><TableCell>{row.date}</TableCell><TableCell>{row.has_gdam ? 'Yes' : 'No'}</TableCell><TableCell>{row.has_dam ? 'Yes' : 'No'}</TableCell><TableCell>{row.has_rtm ? 'Yes' : 'No'}</TableCell><TableCell>{row.has_sch ? 'Yes' : 'No'}</TableCell><TableCell align="right">{fmt(row.total_scheduled_mwh)}</TableCell><TableCell align="right">{fmt(row.total_cost)}</TableCell></TableRow>)}</TableBody>
          </Table>
        </Paper>
      )}

      {activeStep === 2 && (
        <Paper sx={{ p: 2, mb: 3 }}>
          <Typography variant="h6">Step 3: Consumption Details</Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>Upload monthly client consumption or add/update one day manually.</Typography>
          <Button variant="outlined" component="label" disabled={!portfolioId || busy} sx={{ mb: 2 }}>Upload monthly consumption<input hidden type="file" accept=".xlsx,.xls,.csv" onChange={uploadConsumption} /></Button>
          <Grid container spacing={2} alignItems="center" sx={{ mb: 2 }}>
            <Grid item xs={6} md={1.5}><TextField fullWidth size="small" label="Day" type="number" inputProps={{ min: 1, max: 31 }} value={consumptionDay} onChange={(event) => setConsumptionDay(Number(event.target.value) || 1)} /></Grid>
            <Grid item xs={6} md={2}><TextField fullWidth size="small" label="Date" value={consumptionDate} InputProps={{ readOnly: true }} /></Grid>
            <Grid item xs={6} md={1.5}><TextField fullWidth size="small" label="C1 kWh" type="number" value={c1Kwh} onChange={(event) => setC1Kwh(Number(event.target.value))} /></Grid>
            <Grid item xs={6} md={1.5}><TextField fullWidth size="small" label="C2 kWh" type="number" value={c2Kwh} onChange={(event) => setC2Kwh(Number(event.target.value))} /></Grid>
            <Grid item xs={6} md={1.5}><TextField fullWidth size="small" label="C4 kWh" type="number" value={c4Kwh} onChange={(event) => setC4Kwh(Number(event.target.value))} /></Grid>
            <Grid item xs={6} md={1.5}><TextField fullWidth size="small" label="C5 kWh" type="number" value={c5Kwh} onChange={(event) => setC5Kwh(Number(event.target.value))} /></Grid>
            <Grid item xs={6} md={1.5}><TextField fullWidth size="small" label="Base tariff" type="number" value={baseTariff} onChange={(event) => setBaseTariff(event.target.value === '' ? '' : Number(event.target.value))} /></Grid>
            <Grid item xs={6} md={1}><Button fullWidth variant="contained" onClick={saveConsumption} disabled={!portfolioId || busy}>Save</Button></Grid>
          </Grid>
          <Alert severity={status?.steps.consumption?.status === 'complete' ? 'success' : 'warning'} sx={{ mb: 2 }}>
            Consumption present for {status?.steps.consumption?.stored_days || 0}/{status?.period.workflow_days || 0} workflow days.
          </Alert>
          <Table size="small">
            <TableHead><TableRow><TableCell>Date</TableCell><TableCell>Source</TableCell><TableCell align="right">C1</TableCell><TableCell align="right">C2</TableCell><TableCell align="right">C4</TableCell><TableCell align="right">C5</TableCell></TableRow></TableHead>
            <TableBody>{consumptionInputs.map((row: any) => <TableRow key={row.trading_date}><TableCell>{row.trading_date}</TableCell><TableCell>{row.source || '-'}</TableCell><TableCell align="right">{fmt(row.c1_kwh)}</TableCell><TableCell align="right">{fmt(row.c2_kwh)}</TableCell><TableCell align="right">{fmt(row.c4_kwh)}</TableCell><TableCell align="right">{fmt(row.c5_kwh)}</TableCell></TableRow>)}</TableBody>
          </Table>
        </Paper>
      )}

      {activeStep === 3 && (
        <Paper sx={{ p: 2, mb: 3 }}>
          <Typography variant="h6">Step 4: Calculate and validate</Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>Press Submit only after uploads and consumption are ready. The result is saved for report export.</Typography>
          <Button variant="contained" size="large" startIcon={<PlayArrowIcon />} onClick={submitCalculation} disabled={!portfolioId || busy}>Submit calculation</Button>
          <Divider sx={{ my: 2 }} />
          <Grid container spacing={2}>
            <Grid item xs={12} md={3}><Card><CardContent><Typography color="text.secondary">Uploaded files</Typography><Typography variant="h6">{status?.steps.uploads?.file_count || 0}</Typography></CardContent></Card></Grid>
            <Grid item xs={12} md={3}><Card><CardContent><Typography color="text.secondary">Schedule days</Typography><Typography variant="h6">{status?.steps.energy_schedule?.ready_days || 0}/{status?.period.workflow_days || 0}</Typography></CardContent></Card></Grid>
            <Grid item xs={12} md={3}><Card><CardContent><Typography color="text.secondary">Consumption days</Typography><Typography variant="h6">{status?.steps.consumption?.stored_days || 0}/{status?.period.workflow_days || 0}</Typography></CardContent></Card></Grid>
            <Grid item xs={12} md={3}><Card><CardContent><Typography color="text.secondary">Saved results</Typography><Typography variant="h6">{status?.steps.calculation?.saved_daily_rows || 0}</Typography></CardContent></Card></Grid>
          </Grid>
        </Paper>
      )}

      {activeStep === 4 && (
        <Paper sx={{ p: 2, mb: 3 }}>
          <Stack direction={{ xs: 'column', md: 'row' }} justifyContent="space-between" spacing={2} sx={{ mb: 2 }}>
            <Box><Typography variant="h6">Step 5: Review & export</Typography><Typography variant="body2" color="text.secondary">Review totals and download the saved report.</Typography></Box>
            <Stack direction="row" spacing={1}><Button variant="outlined" startIcon={<DownloadIcon />} onClick={() => exportReport('excel')} disabled={!summary || busy}>Excel</Button><Button variant="outlined" startIcon={<DownloadIcon />} onClick={() => exportReport('pdf')} disabled={!summary || busy}>PDF</Button></Stack>
          </Stack>
          <Grid container spacing={2} sx={{ mb: 2 }}>
            <Grid item xs={12} md={3}><Card><CardContent><Typography color="text.secondary">Completed days</Typography><Typography variant="h6">{completion.complete_days ?? '-'}/{completion.days_total ?? '-'}</Typography></CardContent></Card></Grid>
            <Grid item xs={12} md={3}><Card><CardContent><Typography color="text.secondary">IEX price</Typography><Typography variant="h6">{fmt(savingsTotals.iex_price)}</Typography></CardContent></Card></Grid>
            <Grid item xs={12} md={3}><Card><CardContent><Typography color="text.secondary">Equivalent EB price</Typography><Typography variant="h6">{fmt(savingsTotals.equivalent_eb_price)}</Typography></CardContent></Card></Grid>
            <Grid item xs={12} md={3}><Card><CardContent><Typography color="text.secondary">Savings</Typography><Typography variant="h6">{fmt(savingsTotals.total_cost_saving)}</Typography></CardContent></Card></Grid>
          </Grid>
          <Table size="small">
            <TableHead><TableRow><TableCell>Date</TableCell><TableCell>Status</TableCell><TableCell align="right">IEX price</TableCell><TableCell align="right">IEX/unit</TableCell><TableCell align="right">EB price</TableCell><TableCell align="right">Savings</TableCell></TableRow></TableHead>
            <TableBody>{dailyOutputs.map((row: any) => <TableRow key={row.trading_date}><TableCell>{row.trading_date}</TableCell><TableCell><Chip size="small" label={row.is_complete ? 'complete' : 'needs input'} color={row.is_complete ? 'success' : 'warning'} /></TableCell><TableCell align="right">{fmt(row.b44_iex_price)}</TableCell><TableCell align="right">{fmt(row.b45_iex_price_per_unit)}</TableCell><TableCell align="right">{fmt(row.b46_eb_price)}</TableCell><TableCell align="right">{fmt(row.cost_saving)}</TableCell></TableRow>)}</TableBody>
          </Table>
        </Paper>
      )}

      <Paper sx={{ p: 2 }}>
        <Stack direction="row" justifyContent="space-between" alignItems="center">
          <Button startIcon={<ArrowBackIcon />} disabled={activeStep === 0 || busy} onClick={() => setActiveStep((value) => Math.max(0, value - 1))}>Back</Button>
          <Typography variant="body2" color="text.secondary">{selectedPortfolio?.portfolio_code || 'Select portfolio'} ? {year}-{String(month).padStart(2, '0')} ? move back and forth anytime before final submit</Typography>
          <Button endIcon={<ArrowForwardIcon />} disabled={activeStep === labels.length - 1 || busy} onClick={() => setActiveStep((value) => Math.min(labels.length - 1, value + 1))}>Next</Button>
        </Stack>
      </Paper>
    </Box>
  );
};

export default EnergyWorkflow;
