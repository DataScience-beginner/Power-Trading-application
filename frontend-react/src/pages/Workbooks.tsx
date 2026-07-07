import { useState, useEffect, FC } from 'react';
import {
  Box,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Button,
  Card,
  CardContent,
  Grid,
  Alert,
  AlertTitle,
} from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import axios from 'axios';

const API_BASE = '/api/v1';
const DEMO_LOGIN = {
  email: 'admin@demo.local',
  password: 'Admin123!',
  portal: 'admin',
};

const Workbooks: FC = () => {
  const [workbooks, setWorkbooks] = useState<any[]>([]);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const ensureToken = async (): Promise<string | null> => {
    const existing = localStorage.getItem('token');
    if (existing && existing.trim().length > 0) {
      return existing;
    }

    try {
      const res = await axios.post(`${API_BASE}/auth/login`, DEMO_LOGIN);
      const accessToken = res.data?.access_token as string | undefined;
      if (accessToken) {
        localStorage.setItem('token', accessToken);
        return accessToken;
      }
    } catch {
      return null;
    }

    return null;
  };

  const fetchWorkbooks = async () => {
    try {
      const token = await ensureToken();
      const headers: any = {};
      if (token) headers['Authorization'] = `Bearer ${token}`;
      
      const res = await axios.get(`${API_BASE}/workbooks`, { headers });
      setWorkbooks(res.data || []);
    } catch (err: any) {
      setError('Failed to load workbooks. Login may be required.');
    }
  };

  useEffect(() => {
    fetchWorkbooks();
  }, []);

  const handleLogin = async () => {
    try {
      const res = await axios.post(`${API_BASE}/auth/login`, DEMO_LOGIN);
      localStorage.setItem('token', res.data.access_token);
      setSuccess('Login successful! You can now upload workbooks.');
      fetchWorkbooks();
    } catch (err: any) {
      setError('Login failed. Please verify backend auth setup.');
    }
  };

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    setError(null);
    setSuccess(null);

    try {
      const token = await ensureToken();
      const formData = new FormData();
      formData.append('file', file);

      const headers: any = { 'Content-Type': 'multipart/form-data' };
      if (token) headers['Authorization'] = `Bearer ${token}`;

      const res = await axios.post(`${API_BASE}/workbooks/upload`, formData, { headers });
      setSuccess(`Workbook uploaded successfully! Calculated ${res.data.preview_rows?.length || 0} solar working rows.`);
      fetchWorkbooks();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Upload failed. Please login first.');
    } finally {
      setUploading(false);
    }
  };

  const handleViewResults = async (workbookId: string) => {
    try {
      const token = await ensureToken();
      const headers: any = {};
      if (token) headers['Authorization'] = `Bearer ${token}`;
      
      const res = await axios.get(`${API_BASE}/workbooks/${workbookId}/solar-working`, { headers });
      const resultData = res.data;
      const rows = resultData.rows || [];
      
      if (rows.length === 0) {
        setSuccess('No solar working results found for this workbook.');
      } else {
        const totalTneb = rows.reduce((sum: number, r: any) => sum + (r.tneb_total || 0), 0);
        const totalIex = rows.reduce((sum: number, r: any) => sum + (r.iex_total || 0), 0);
        const totalSolar = rows.reduce((sum: number, r: any) => sum + (r.solar_total || 0), 0);
        setSuccess(
          `Solar Working Results for ${resultData.workbook_month || 'unknown month'}:\n` +
          `  Days: ${rows.length}\n` +
          `  Total TNEB: ${totalTneb.toFixed(2)} MWh\n` +
          `  Total IEX: ${totalIex.toFixed(2)} MWh\n` +
          `  Total Solar: ${totalSolar.toFixed(2)} MWh`
        );
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load results.');
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ fontWeight: 700 }}>
        Client Workbook Uploads
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
        Upload Excel workbooks with DAM, RTM, and TNEB sheets to calculate Solar Working results.
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          <AlertTitle>Error</AlertTitle>
          {error}
        </Alert>
      )}
      
      {success && (
        <Alert severity="success" sx={{ mb: 2, whiteSpace: 'pre-line' }} onClose={() => setSuccess(null)}>
          <AlertTitle>Success</AlertTitle>
          {success}
        </Alert>
      )}

      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent sx={{ textAlign: 'center', py: 4 }}>
              <CloudUploadIcon sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
              <Typography variant="h6" gutterBottom>
                Upload Workbook
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Select an Excel file with DAM, RTM, TNEB sheets
              </Typography>
              <Button
                variant="contained"
                component="label"
                disabled={uploading}
                fullWidth
              >
                {uploading ? 'Uploading...' : 'Choose File'}
                <input type="file" hidden accept=".xlsx,.xls" onChange={handleUpload} />
              </Button>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">Uploaded Workbooks</Typography>
                <Box>
                  <Button 
                    variant="outlined" 
                    size="small" 
                    onClick={handleLogin}
                    sx={{ mr: 1 }}
                  >
                    Login
                  </Button>
                  <Button variant="outlined" size="small" onClick={fetchWorkbooks}>
                    Refresh
                  </Button>
                </Box>
              </Box>
              
              {workbooks.length === 0 ? (
                <Typography variant="body2" color="text.secondary" sx={{ py: 4, textAlign: 'center' }}>
                  No workbooks uploaded yet. Click "Choose File" to upload your first workbook.
                </Typography>
              ) : (
                <TableContainer>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>File Name</TableCell>
                        <TableCell>Month</TableCell>
                        <TableCell>Status</TableCell>
                        <TableCell>Actions</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {workbooks.map((wb: any) => (
                        <TableRow key={wb.id}>
                          <TableCell>{wb.original_file_name || wb.file_name}</TableCell>
                          <TableCell>{wb.workbook_month || '-'}</TableCell>
                          <TableCell>
                            <Typography
                              variant="body2"
                              sx={{
                                color: wb.status === 'calculated' ? 'success.main' : 'warning.main',
                                fontWeight: 600,
                              }}
                            >
                              {wb.status}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            {wb.status === 'calculated' && (
                              <Button
                                size="small"
                                variant="text"
                                onClick={() => handleViewResults(wb.id)}
                              >
                                View Results
                              </Button>
                            )}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Workbooks;