import React, { useEffect, useState, useCallback } from 'react';
import { TreeView, TreeItem } from '@mui/lab';
import { Typography, Box, Paper, Button, Stack, Chip, MenuItem, Select, FormControl, InputLabel, Card, CardContent, Grid } from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ChevronRightIcon from '@mui/icons-material/ChevronRight';
import { DataGrid, GridColDef } from '@mui/x-data-grid';

const API_URL = '/api/admin';

const AdminDatabase: React.FC = () => {
  const [tables, setTables] = useState<string[]>([]);
  const [selectedTable, setSelectedTable] = useState<string | null>(null);
  const [tableColumns, setTableColumns] = useState<GridColDef[]>([]);
  const [rows, setRows] = useState<any[]>([]);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [page, setPage] = useState(0);
  const [pageSize, setPageSize] = useState(10);
  const [showExcelView, setShowExcelView] = useState(false);
  const [summary, setSummary] = useState<any | null>(null);

  useEffect(() => {
    const t = localStorage.getItem('admin_jwt') || sessionStorage.getItem('admin_jwt');
    setToken(t);
  }, []);

  // Fetch table list
  useEffect(() => {
    if (!token) return;
    fetch(`${API_URL}/tables`, { headers: { Authorization: `Bearer ${token}` } })
      .then((r) => r.json())
      .then((data) => setTables(data.tables || []))
      .catch(() => setTables([]));
  }, [token]);

  // Fetch summary data
  useEffect(() => {
    if (!token) return;
    fetch(`${API_URL}/summary`, { headers: { Authorization: `Bearer ${token}` } })
      .then((r) => r.json())
      .then((data) => setSummary(data))
      .catch(() => setSummary(null));
  }, [token]);

  const fetchPage = useCallback((table: string, pageNum: number, pageSizeNum: number) => {
    if (!token) return;
    setLoading(true);
    const offset = pageNum * pageSizeNum;
    fetch(`${API_URL}/table/${table}?limit=${pageSizeNum}&offset=${offset}`, { headers: { Authorization: `Bearer ${token}` } })
      .then((r) => r.json())
      .then((data) => {
        const cols: GridColDef[] = (data.columns || []).map((c: string) => ({ field: c, headerName: c, flex: 1 }));
        const rawRows = data.rows || [];
        const normRows = rawRows.map((r: any, i: number) => ({ id: r.id ?? `r_${offset}_${i}`, ...r }));
        setTableColumns(cols);
        setRows(normRows);
      })
      .catch(() => {
        setTableColumns([]);
        setRows([]);
      })
      .finally(() => setLoading(false));
  }, [token]);

  useEffect(() => {
    if (!selectedTable) return;
    setPage(0);
    fetchPage(selectedTable, 0, pageSize);
  }, [selectedTable, fetchPage, pageSize]);

  const handlePrev = () => {
    const next = Math.max(0, page - 1);
    setPage(next);
    if (selectedTable) fetchPage(selectedTable, next, pageSize);
  };
  const handleNext = () => {
    const next = page + 1;
    setPage(next);
    if (selectedTable) fetchPage(selectedTable, next, pageSize);
  };

  const exportCSV = () => {
    if (!tableColumns || tableColumns.length === 0 || rows.length === 0) return;
    const headers = tableColumns.map((c) => c.field);
    const csvRows = [] as string[];
    csvRows.push(headers.join(','));
    for (const r of rows) {
      const line = headers.map((h) => {
        const v = r[h];
        if (v === null || v === undefined) return '';
        const s = String(v);
        return s.includes(',') || s.includes('"') || s.includes('\n') ? `"${s.replace(/"/g, '""')}"` : s;
      }).join(',');
      csvRows.push(line);
    }
    const blob = new Blob([csvRows.join('\n')], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${selectedTable || 'export'}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <Box display="flex" flexDirection="column" gap={2}>
      {summary && (
        <Grid container spacing={2} mb={2}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography variant="h6">Clients</Typography>
                <Typography variant="h4">{summary.clients}</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography variant="h6">Portfolios</Typography>
                <Typography variant="h4">{summary.portfolios}</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography variant="h6">Daily Files</Typography>
                <Typography variant="h4">{summary.dailyFiles}</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography variant="h6">Transactions</Typography>
                <Typography variant="h4">{summary.transactions}</Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      <Box display="flex" gap={2}>
        <Paper sx={{ minWidth: 250, maxHeight: 600, overflow: 'auto', p: 2 }}>
          <Typography variant="h6">Database Tables</Typography>
          <TreeView defaultCollapseIcon={<ExpandMoreIcon />} defaultExpandIcon={<ChevronRightIcon />}>
            {tables.map((table) => (
              <TreeItem key={table} nodeId={table} label={table} onClick={() => setSelectedTable(table)} />
            ))}
          </TreeView>
        </Paper>

        <Paper sx={{ flex: 1, p: 2, minHeight: 400 }}>
          {!selectedTable ? (
            <Typography>Select a table to view data.</Typography>
          ) : (
            <>
              <Stack direction="row" alignItems="center" justifyContent="space-between" mb={2}>
                <Typography variant="h6">{selectedTable} Data</Typography>
                <Stack direction="row" spacing={1} alignItems="center">
                  <FormControl size="small" sx={{ minWidth: 120 }}>
                    <InputLabel>Page Size</InputLabel>
                    <Select value={pageSize} label="Page Size" onChange={(e) => setPageSize(Number(e.target.value))}>
                      <MenuItem value={5}>5</MenuItem>
                      <MenuItem value={10}>10</MenuItem>
                      <MenuItem value={25}>25</MenuItem>
                    </Select>
                  </FormControl>
                  <Button variant="outlined" onClick={() => setShowExcelView((s) => !s)}>
                    {showExcelView ? 'Hide Excel View' : 'Excel View'}
                  </Button>
                  <Button variant="contained" onClick={exportCSV} disabled={rows.length === 0}>
                    Export CSV
                  </Button>
                  <Button variant="outlined" onClick={handlePrev} disabled={page === 0 || loading}>Prev</Button>
                  <Button variant="outlined" onClick={handleNext} disabled={rows.length < pageSize || loading}>Next</Button>
                </Stack>
              </Stack>

              <Box mb={1}>
                <Typography variant="subtitle2">Columns:</Typography>
                <Stack direction="row" spacing={1} mt={1} flexWrap="wrap">
                  {tableColumns.map((c) => (
                    <Chip key={c.field} label={c.field} size="small" />
                  ))}
                </Stack>
              </Box>

              <div style={{ width: '100%' }}>
                <DataGrid autoHeight rows={rows} columns={tableColumns} loading={loading} disableRowSelectionOnClick />
              </div>
              {showExcelView && (
                <Box mt={2} sx={{ borderTop: '1px solid rgba(0,0,0,0.12)', pt: 2 }}>
                  <Typography variant="subtitle2" gutterBottom>Excel-style view (read-only)</Typography>
                  <div style={{ overflowX: 'auto', maxHeight: 340 }}>
                    <table style={{ borderCollapse: 'collapse', width: '100%' }}>
                      <thead>
                        <tr>
                          {tableColumns.map((c) => (
                            <th key={c.field} style={{ border: '1px solid #e0e0e0', padding: '6px 8px', textAlign: 'left', background: '#fafafa' }}>{c.headerName}</th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {rows.map((r) => (
                          <tr key={r.id}>
                            {tableColumns.map((c) => (
                              <td key={c.field} style={{ border: '1px solid #eee', padding: '6px 8px' }}>{String(r[c.field] ?? '')}</td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </Box>
              )}
            </>
          )}
        </Paper>
      </Box>
    </Box>
  );
};

export default AdminDatabase;