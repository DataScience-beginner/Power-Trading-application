import React, { useEffect, useState } from 'react';
import { TreeView, TreeItem } from '@mui/lab';
import { Typography, Box, Paper } from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ChevronRightIcon from '@mui/icons-material/ChevronRight';

const API_URL = '/api/admin';

const AdminDatabase: React.FC = () => {
  const [tables, setTables] = useState<string[]>([]);
  const [selectedTable, setSelectedTable] = useState<string | null>(null);
  const [tableData, setTableData] = useState<any>(null);
  const [token, setToken] = useState<string | null>(null);

  // Fetch JWT from localStorage/sessionStorage (to be set by admin login page)
  useEffect(() => {
    const t = localStorage.getItem('admin_jwt') || sessionStorage.getItem('admin_jwt');
    setToken(t);
  }, []);

  // Fetch tables
  useEffect(() => {
    if (!token) return;
    fetch(`${API_URL}/tables`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then(res => res.json())
      .then(data => setTables(data.tables || []));
  }, [token]);

  // Fetch table data
  useEffect(() => {
    if (!token || !selectedTable) return;
    fetch(`${API_URL}/table/${selectedTable}?limit=100`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then(res => res.json())
      .then(data => setTableData(data));
  }, [token, selectedTable]);

  return (
    <Box display="flex" gap={2}>
      <Paper sx={{ minWidth: 250, maxHeight: 600, overflow: 'auto', p: 2 }}>
        <Typography variant="h6">Database Tables</Typography>
        <TreeView
          defaultCollapseIcon={<ExpandMoreIcon />}
          defaultExpandIcon={<ChevronRightIcon />}
        >
          {tables.map(table => (
            <TreeItem
              key={table}
              nodeId={table}
              label={table}
              onClick={() => setSelectedTable(table)}
            />
          ))}
        </TreeView>
      </Paper>
      <Paper sx={{ flex: 1, p: 2, minHeight: 400 }}>
        {selectedTable ? (
          <>
            <Typography variant="h6">{selectedTable} Data</Typography>
            {tableData ? (
              <Box component="pre" sx={{ whiteSpace: 'pre-wrap', fontSize: 14 }}>
                {JSON.stringify(tableData, null, 2)}
              </Box>
            ) : (
              <Typography>Loading...</Typography>
            )}
          </>
        ) : (
          <Typography>Select a table to view data.</Typography>
        )}
      </Paper>
    </Box>
  );
};

export default AdminDatabase;