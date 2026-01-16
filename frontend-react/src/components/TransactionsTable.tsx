import { useState, FC } from 'react';
import { DataGrid, GridColDef, GridRenderCellParams } from '@mui/x-data-grid';
import { Box, Chip, IconButton, Tooltip } from '@mui/material';
import { Edit as EditIcon, Delete as DeleteIcon } from '@mui/icons-material';
import { useAppSelector } from '../hooks/useAppStore';
import type { Transaction } from '../types';

const TransactionsTable: FC = () => {
  const { transactions, loading } = useAppSelector((state) => state.dashboard);

  // Debug log to see what data we're getting
  console.log('TransactionsTable - transactions:', transactions);
  console.log('TransactionsTable - first transaction:', transactions[0]);

  const columns: GridColDef[] = [
    {
      field: 'date',
      headerName: 'Date',
      width: 120,
      renderCell: (params: GridRenderCellParams) => {
        if (!params.value) return '-';
        const date = new Date(params.value as string);
        if (isNaN(date.getTime())) return String(params.value);
        return date.toLocaleDateString('en-IN');
      },
    },
    {
      field: 'time_slot',
      headerName: 'Time Slot',
      width: 130,
    },
    {
      field: 'portfolio_code',
      headerName: 'Portfolio',
      width: 140,
    },
    {
      field: 'transaction_type',
      headerName: 'Type',
      width: 120,
      renderCell: (params: GridRenderCellParams) => {
        const type = params.value as string;
        const color =
          type === 'buy' ? 'success' : type === 'sell' ? 'error' : 'info';
        return <Chip label={type.toUpperCase()} color={color} size="small" />;
      },
    },
    {
      field: 'report_type',
      headerName: 'Report',
      width: 120,
    },
    {
      field: 'quantity_mw',
      headerName: 'Quantity (MW)',
      width: 130,
      type: 'number',
      renderCell: (params: GridRenderCellParams) => {
        const num = Number(params.value);
        if (isNaN(num) || params.value === null || params.value === undefined) return '-';
        return num.toFixed(3);
      },
    },
    {
      field: 'rate_per_mwh',
      headerName: 'Rate (₹/MWh)',
      width: 130,
      type: 'number',
      renderCell: (params: GridRenderCellParams) => {
        const num = Number(params.value);
        if (isNaN(num) || params.value === null || params.value === undefined) return '-';
        return num.toFixed(2);
      },
    },
    {
      field: 'amount',
      headerName: 'Amount (₹)',
      width: 130,
      type: 'number',
      renderCell: (params: GridRenderCellParams) => {
        const num = Number(params.value);
        if (isNaN(num) || params.value === null || params.value === undefined) return '-';
        return new Intl.NumberFormat('en-IN', {
          style: 'currency',
          currency: 'INR',
        }).format(num);
      },
    },
    {
      field: 'actions',
      headerName: 'Actions',
      width: 120,
      sortable: false,
      filterable: false,
      renderCell: (params: GridRenderCellParams) => (
        <Box>
          <Tooltip title="Edit">
            <IconButton size="small" color="primary">
              <EditIcon fontSize="small" />
            </IconButton>
          </Tooltip>
          <Tooltip title="Delete">
            <IconButton size="small" color="error">
              <DeleteIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        </Box>
      ),
    },
  ];

  return (
    <Box sx={{ height: 500, width: '100%' }}>
      <DataGrid
        rows={transactions}
        columns={columns}
        loading={loading}
        initialState={{
          pagination: {
            paginationModel: { pageSize: 10, page: 0 },
          },
        }}
        pageSizeOptions={[10, 25, 50, 100]}
        checkboxSelection
        disableRowSelectionOnClick
        sx={{
          '& .MuiDataGrid-cell:hover': {
            cursor: 'pointer',
          },
        }}
      />
    </Box>
  );
};

export default TransactionsTable;
