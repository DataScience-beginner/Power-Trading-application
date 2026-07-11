import { FC, useMemo, useState } from 'react';
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Divider,
  Grid,
  LinearProgress,
  MenuItem,
  Stack,
  TextField,
  Typography,
} from '@mui/material';
import { AutoAwesome, FactCheck, QuestionAnswer, Security } from '@mui/icons-material';
import apiService from '../services/api';
import { useAppSelector } from '../hooks/useAppStore';
import type { AssistantAnswer, MarketExplanation, QualityPolicy, QualityRun } from '../types/aiInsights';

const defaultPolicy: QualityPolicy = {
  policy_version: 'data-quality-v1',
  expected_report_types: ['DOR-GDAM', 'DOR-DAM', 'DOR-RTM', 'SCH-GDAM', 'SCH-DAM', 'SCH-RTM'],
  expected_blocks_per_file: 96,
  minimum_rate: 0,
  maximum_rate: null,
  allow_negative_quantity: false,
  require_time_block_start: true,
};

const isoDate = (date: Date) => date.toISOString().slice(0, 10);
const monthStart = () => {
  const date = new Date();
  date.setDate(1);
  return isoDate(date);
};

const severityColor = (severity: string): 'error' | 'warning' | 'info' | 'default' => {
  if (severity === 'critical' || severity === 'high') return 'error';
  if (severity === 'medium') return 'warning';
  if (severity === 'low' || severity === 'info') return 'info';
  return 'default';
};

const AIInsights: FC = () => {
  const clients = useAppSelector((state) => state.dashboard.clients);
  const [serviceKey, setServiceKey] = useState(() => sessionStorage.getItem('ai_foundation_key') || '');
  const [clientId, setClientId] = useState<number | ''>('');
  const [startDate, setStartDate] = useState(monthStart());
  const [endDate, setEndDate] = useState(isoDate(new Date()));
  const [classification, setClassification] = useState<'synthetic' | 'actual' | 'mixed' | 'unknown'>('unknown');
  const [policy, setPolicy] = useState<QualityPolicy>(defaultPolicy);
  const [qualityRun, setQualityRun] = useState<QualityRun | null>(null);
  const [explanation, setExplanation] = useState<MarketExplanation | null>(null);
  const [assistant, setAssistant] = useState<AssistantAnswer | null>(null);
  const [question, setQuestion] = useState('Explain the recorded market cost and data coverage.');
  const [loading, setLoading] = useState<string | null>(null);
  const [error, setError] = useState('');

  const canRun = Boolean(serviceKey && clientId && startDate && endDate);
  const findingTotal = useMemo(
    () => Object.values(qualityRun?.finding_counts || {}).reduce((sum, count) => sum + count, 0),
    [qualityRun]
  );

  const saveKey = () => {
    sessionStorage.setItem('ai_foundation_key', serviceKey);
    setError('');
  };

  const execute = async (name: string, operation: () => Promise<void>) => {
    setLoading(name);
    setError('');
    try {
      await operation();
    } catch (reason: any) {
      const detail = reason?.response?.data?.detail || reason?.message || 'AI insight request failed';
      setError(String(detail));
    } finally {
      setLoading(null);
    }
  };

  const runQuality = () => execute('quality', async () => {
    const result = await apiService.runDataQualityAnalysis({
      serviceKey,
      clientId: Number(clientId),
      startDate,
      endDate,
      dataClassification: classification,
      policy,
    });
    setQualityRun(result);
  });

  const runExplanation = () => execute('explanation', async () => {
    setExplanation(await apiService.explainMarket({
      serviceKey,
      clientId: Number(clientId),
      startDate,
      endDate,
      question,
    }));
  });

  const askAssistant = () => execute('assistant', async () => {
    setAssistant(await apiService.askInsightAssistant({
      serviceKey,
      clientId: Number(clientId),
      startDate,
      endDate,
      question,
      conversationId: assistant?.conversation_id,
    }));
  });

  return (
    <Stack spacing={3}>
      <Box>
        <Typography variant="h4" fontWeight={900}>AI Insights</Typography>
        <Typography color="text.secondary">
          Deterministic data quality, evidence-backed market explanations, and a bounded read-only assistant.
        </Typography>
      </Box>

      <Alert severity="info" icon={<Security />}>
        AI-1 is read-only for business data. It does not correct files, forecast prices, alter schedules, bid, or trade.
        The service key is kept in this browser session only.
      </Alert>

      <Card>
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={4}>
              <TextField fullWidth type="password" label="AI Foundation service key" value={serviceKey} onChange={(event) => setServiceKey(event.target.value)} />
            </Grid>
            <Grid item xs={12} md={2}><Button variant="outlined" onClick={saveKey}>Use for session</Button></Grid>
            <Grid item xs={12} md={3}>
              <TextField select fullWidth label="Client" value={clientId} onChange={(event) => setClientId(Number(event.target.value))}>
                {clients.map((client) => <MenuItem key={client.id} value={client.id}>{client.entity_name}</MenuItem>)}
              </TextField>
            </Grid>
            <Grid item xs={6} md={1.5}><TextField fullWidth type="date" label="From" InputLabelProps={{ shrink: true }} value={startDate} onChange={(event) => setStartDate(event.target.value)} /></Grid>
            <Grid item xs={6} md={1.5}><TextField fullWidth type="date" label="To" InputLabelProps={{ shrink: true }} value={endDate} onChange={(event) => setEndDate(event.target.value)} /></Grid>
          </Grid>
        </CardContent>
      </Card>

      {error && <Alert severity="error">{error}</Alert>}
      {loading && <LinearProgress />}

      <Grid container spacing={3}>
        <Grid item xs={12} lg={6}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Stack direction="row" spacing={1} alignItems="center"><FactCheck color="primary" /><Typography variant="h6" fontWeight={800}>Data Quality Agent</Typography></Stack>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>Policy values are configurable inputs—not permanent assumptions.</Typography>
              <Grid container spacing={2} sx={{ mt: 0.5 }}>
                <Grid item xs={6}><TextField fullWidth type="number" label="Expected blocks/file" value={policy.expected_blocks_per_file} onChange={(event) => setPolicy({ ...policy, expected_blocks_per_file: Number(event.target.value) })} /></Grid>
                <Grid item xs={6}>
                  <TextField select fullWidth label="Data classification" value={classification} onChange={(event) => setClassification(event.target.value as typeof classification)}>
                    {['unknown', 'synthetic', 'actual', 'mixed'].map((value) => <MenuItem key={value} value={value}>{value}</MenuItem>)}
                  </TextField>
                </Grid>
              </Grid>
              <Button sx={{ mt: 2 }} variant="contained" disabled={!canRun || Boolean(loading)} onClick={runQuality} startIcon={loading === 'quality' ? <CircularProgress size={16} /> : <FactCheck />}>Run Quality Analysis</Button>
              {qualityRun && (
                <Stack spacing={2} sx={{ mt: 3 }}>
                  <Stack direction="row" spacing={1} flexWrap="wrap">
                    <Chip label={`${qualityRun.files_evaluated} files`} />
                    <Chip label={`${qualityRun.transactions_evaluated} intervals`} />
                    <Chip color={findingTotal ? 'warning' : 'success'} label={`${findingTotal} findings`} />
                    <Chip variant="outlined" label={qualityRun.data_classification} />
                  </Stack>
                  {qualityRun.findings.map((item) => (
                    <Box key={item.id} sx={{ border: '1px solid', borderColor: 'divider', borderRadius: 2, p: 2 }}>
                      <Stack direction="row" spacing={1} alignItems="center"><Chip size="small" color={severityColor(item.severity)} label={item.severity} /><Typography fontWeight={700}>{item.title}</Typography></Stack>
                      <Typography variant="body2" sx={{ mt: 1 }}>{item.description}</Typography>
                      <Typography variant="caption" color="text.secondary">Action: {item.recommended_action}</Typography>
                    </Box>
                  ))}
                  {!qualityRun.findings.length && <Alert severity="success">No findings under the selected policy.</Alert>}
                </Stack>
              )}
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} lg={6}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Stack direction="row" spacing={1} alignItems="center"><AutoAwesome color="primary" /><Typography variant="h6" fontWeight={800}>Market Explanation</Typography></Stack>
              <TextField fullWidth multiline minRows={3} label="Question" value={question} onChange={(event) => setQuestion(event.target.value)} sx={{ mt: 2 }} />
              <Stack direction="row" spacing={1} sx={{ mt: 2 }}>
                <Button variant="contained" disabled={!canRun || Boolean(loading)} onClick={runExplanation}>Explain with evidence</Button>
                <Button variant="outlined" disabled={!canRun || Boolean(loading)} onClick={askAssistant} startIcon={<QuestionAnswer />}>Ask assistant</Button>
              </Stack>
              {explanation && (
                <Stack spacing={2} sx={{ mt: 3 }}>
                  <Alert severity={explanation.human_review_required ? 'warning' : 'success'}>{explanation.answer}</Alert>
                  <Grid container spacing={1}>{explanation.metrics.map((metric) => <Grid item xs={6} key={metric.name}><Box sx={{ bgcolor: 'action.hover', borderRadius: 2, p: 1.5 }}><Typography variant="caption" color="text.secondary">{metric.name}</Typography><Typography fontWeight={800}>{metric.value} {metric.unit || ''}</Typography></Box></Grid>)}</Grid>
                  <Typography variant="body2">Confidence: {Math.round(explanation.confidence * 100)}% • {explanation.engine}</Typography>
                  <Divider />
                  {explanation.limitations.map((item) => <Typography key={item} variant="caption" color="text.secondary">• {item}</Typography>)}
                </Stack>
              )}
              {assistant && (
                <Box sx={{ mt: 3, bgcolor: 'primary.50', border: '1px solid', borderColor: 'primary.light', borderRadius: 2, p: 2 }}>
                  <Typography variant="overline">Intent: {assistant.intent}</Typography>
                  <Typography>{assistant.answer}</Typography>
                  <Typography variant="caption" color="text.secondary">{assistant.safety_notice}</Typography>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Stack>
  );
};

export default AIInsights;
