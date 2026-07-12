import { useEffect, useMemo, useState } from 'react';
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
  Stack,
  Typography,
} from '@mui/material';

type PortalType = 'client' | 'admin';

type AuthenticatedUser = {
  id: string;
  tenant_id: string | null;
  email: string;
  full_name: string;
  role_codes: string[];
};

type WorkbookListItem = {
  workbook_id: string;
  file_name: string;
  workbook_month: string | null;
  status: string;
  uploaded_at: string;
  uploaded_by_user_id: string | null;
  solar_working_rows: number;
};

type WorkbookRow = {
  reading_date: string;
  tneb_total: number;
  iex_total: number;
  solar_total: number;
  tneb_balance: number;
  banking_balance: number;
};

type WorkbookUploadResponse = {
  workbook_id: string;
  file_name: string;
  workbook_month: string | null;
  status: string;
  sheet_summaries: Array<{
    sheet_name: string;
    sheet_type: string;
    status: string;
    row_count: number | null;
    validation_summary: string | null;
  }>;
  calculation_summary: Record<string, string | number | null>;
  preview_rows: WorkbookRow[];
};

type WorkbookResultsResponse = {
  workbook_id: string;
  workbook_month: string | null;
  status: string;
  rows: WorkbookRow[];
};

function resolveApiBaseUrl(): string {
  const meta = import.meta as ImportMeta & {
    env?: Record<string, string | undefined>;
  };
  const configuredUrl = meta.env?.VITE_ENERGY_PLATFORM_API_BASE_URL?.trim();
  if (configuredUrl) {
    return configuredUrl;
  }

  return '';
}

const apiBaseUrl = resolveApiBaseUrl();

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${apiBaseUrl}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(init?.headers ?? {}),
    },
    ...init,
  });

  if (!response.ok) {
    const errorBody = await response.json().catch(() => null);
    throw new Error(errorBody?.detail ?? 'Request failed.');
  }

  return (await response.json()) as T;
}

async function fetchWorkbookHistory(token: string): Promise<WorkbookListItem[]> {
  return request<WorkbookListItem[]>('/api/v1/workbooks', {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
}

async function fetchWorkbookResults(token: string, workbookId: string): Promise<WorkbookResultsResponse> {
  return request<WorkbookResultsResponse>(`/api/v1/workbooks/${workbookId}/solar-working`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
}

async function uploadWorkbook(token: string, file: File): Promise<WorkbookUploadResponse> {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${apiBaseUrl}/api/v1/workbooks/upload`, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${token}`,
    },
    body: formData,
  });

  if (!response.ok) {
    const errorBody = await response.json().catch(() => null);
    throw new Error(errorBody?.detail ?? 'Upload failed.');
  }

  return (await response.json()) as WorkbookUploadResponse;
}

function loadSession(): { token: string; user: AuthenticatedUser; portal: PortalType } | null {
  const token = sessionStorage.getItem('innowatt_access_token');
  const rawUser = sessionStorage.getItem('innowatt_user');
  if (!token || !rawUser) {
    return null;
  }

  try {
    const identity = JSON.parse(rawUser) as { id: string; client_id: number | null; email: string; display_name: string; role: string };
    return { token, portal: identity.role === 'platform_admin' ? 'admin' : 'client', user: { id: identity.id, tenant_id: identity.client_id ? String(identity.client_id) : null, email: identity.email, full_name: identity.display_name, role_codes: identity.role === 'platform_admin' ? ['platform_admin'] : ['client_viewer'] } };
  } catch {
    return null;
  }
}

export default function WorkbookInputsPage() {
  const [session, setSession] = useState(loadSession());

  const [workbooks, setWorkbooks] = useState<WorkbookListItem[]>([]);
  const [selectedWorkbookId, setSelectedWorkbookId] = useState<string | null>(null);
  const [selectedResult, setSelectedResult] = useState<WorkbookResultsResponse | null>(null);
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [uploadResult, setUploadResult] = useState<WorkbookUploadResponse | null>(null);
  const [pageError, setPageError] = useState('');
  const [isBusy, setIsBusy] = useState(false);

  const selectedWorkbook = useMemo(
    () => workbooks.find((item) => item.workbook_id === selectedWorkbookId) ?? null,
    [selectedWorkbookId, workbooks],
  );

  useEffect(() => {
    if (!session) {
      return;
    }

    setIsBusy(true);
    setPageError('');
    fetchWorkbookHistory(session.token)
      .then((items) => {
        setWorkbooks(items);
        if (items.length > 0) {
          setSelectedWorkbookId(items[0].workbook_id);
        }
      })
      .catch((error: Error) => setPageError(error.message))
      .finally(() => setIsBusy(false));
  }, [session]);

  useEffect(() => {
    if (!session || !selectedWorkbookId) {
      return;
    }

    setIsBusy(true);
    setPageError('');
    fetchWorkbookResults(session.token, selectedWorkbookId)
      .then(setSelectedResult)
      .catch((error: Error) => setPageError(error.message))
      .finally(() => setIsBusy(false));
  }, [selectedWorkbookId, session]);

  const handleUpload = async () => {
    if (!session || !uploadFile) {
      return;
    }

    setIsBusy(true);
    setPageError('');
    try {
      const result = await uploadWorkbook(session.token, uploadFile);
      setUploadResult(result);
      const items = await fetchWorkbookHistory(session.token);
      setWorkbooks(items);
      setSelectedWorkbookId(result.workbook_id);
      const workbookResult = await fetchWorkbookResults(session.token, result.workbook_id);
      setSelectedResult(workbookResult);
    } catch (error) {
      setPageError(error instanceof Error ? error.message : 'Upload failed.');
    } finally {
      setIsBusy(false);
    }
  };

  const finalBalance = selectedResult?.rows[selectedResult.rows.length - 1]?.tneb_balance ?? 0;

  if (!session) {
    return (
      <Box sx={{ p: 3 }}>
        <Typography variant="h4" gutterBottom>
          Workbook Inputs
        </Typography>
        <Card sx={{ maxWidth: 520 }}>
          <CardContent>
            <Stack spacing={2}>
              <Alert severity="warning">Your enterprise session is missing. Return to the appropriate admin or client login portal.</Alert>
            </Stack>
          </CardContent>
        </Card>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Stack spacing={3}>
        <Box>
          <Typography variant="h4" gutterBottom>
            Workbook Inputs
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Same project, same app shell, same domain. This page stays inside the current application.
          </Typography>
        </Box>

        {pageError ? <Alert severity="error">{pageError}</Alert> : null}

        <Grid container spacing={2}>
          <Grid item xs={12} md={5}>
            <Card>
              <CardContent>
                <Stack spacing={2}>
                  <Typography variant="h6">Upload</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Upload the workbook input file and let the backend calculate Solar Working.
                  </Typography>
                  <Button variant="outlined" component="label">
                    Select workbook
                    <input
                      hidden
                      accept=".xlsx"
                      type="file"
                      onChange={(event) => setUploadFile(event.target.files?.[0] ?? null)}
                    />
                  </Button>
                  <Typography variant="body2">
                    {uploadFile?.name ?? 'No workbook selected'}
                  </Typography>
                  <Button variant="contained" onClick={handleUpload} disabled={!uploadFile || isBusy}>
                    {isBusy ? 'Processing...' : 'Upload workbook'}
                  </Button>
                </Stack>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={7}>
            <Card>
              <CardContent>
                <Stack spacing={2}>
                  <Typography variant="h6">Current Summary</Typography>
                  <Stack direction="row" spacing={1} flexWrap="wrap">
                    <Chip label={`Workbooks: ${workbooks.length}`} />
                    <Chip label={`Selected: ${selectedWorkbook?.file_name ?? 'none'}`} />
                    <Chip label={`Rows: ${selectedResult?.rows.length ?? 0}`} />
                    <Chip label={`Final balance: ${finalBalance.toFixed(2)}`} color="primary" />
                  </Stack>
                  <Divider />
                  {uploadResult ? (
                    <Box>
                      <Typography variant="subtitle2">Latest upload</Typography>
                      <Typography variant="body2">{uploadResult.file_name}</Typography>
                      <Typography variant="body2">Status: {uploadResult.status}</Typography>
                    </Box>
                  ) : null}
                </Stack>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        <Grid container spacing={2}>
          <Grid item xs={12} md={5}>
            <Card>
              <CardContent>
                <Stack spacing={2}>
                  <Typography variant="h6">Workbook History</Typography>
                  {isBusy && workbooks.length === 0 ? <CircularProgress size={24} /> : null}
                  <Stack spacing={1}>
                    {workbooks.map((item) => (
                      <Button
                        key={item.workbook_id}
                        variant={item.workbook_id === selectedWorkbookId ? 'contained' : 'text'}
                        onClick={() => setSelectedWorkbookId(item.workbook_id)}
                        sx={{ justifyContent: 'space-between' }}
                      >
                        <span>{item.file_name}</span>
                        <Chip size="small" label={item.status} />
                      </Button>
                    ))}
                    {workbooks.length === 0 ? (
                      <Typography variant="body2" color="text.secondary">
                        No workbooks uploaded yet.
                      </Typography>
                    ) : null}
                  </Stack>
                </Stack>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={7}>
            <Card>
              <CardContent>
                <Stack spacing={2}>
                  <Typography variant="h6">Results</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Selected workbook: {selectedWorkbook?.file_name ?? 'none'}
                  </Typography>
                  <Divider />
                  {selectedResult ? (
                    <Stack spacing={1}>
                      {selectedResult.rows.slice(0, 10).map((row) => (
                        <Stack key={row.reading_date} direction="row" spacing={2}>
                          <Typography variant="body2" sx={{ minWidth: 100 }}>
                            {row.reading_date}
                          </Typography>
                          <Typography variant="body2">TNEB {row.tneb_total.toFixed(2)}</Typography>
                          <Typography variant="body2">IEX {row.iex_total.toFixed(2)}</Typography>
                          <Typography variant="body2">Solar {row.solar_total.toFixed(2)}</Typography>
                          <Typography variant="body2">Balance {row.tneb_balance.toFixed(2)}</Typography>
                        </Stack>
                      ))}
                    </Stack>
                  ) : (
                    <Typography variant="body2" color="text.secondary">
                      Select a workbook to view calculated rows.
                    </Typography>
                  )}
                </Stack>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Stack>
    </Box>
  );
}
