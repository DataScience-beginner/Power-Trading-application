import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import apiService from '../services/api';
import type {
  Client,
  Transaction,
  AnalyticsSummary,
  HourlyDistribution,
  PortfolioComparison,
  TransactionFilter,
} from '../types';

interface DashboardState {
  clients: Client[];
  transactions: Transaction[];
  summary: AnalyticsSummary | null;
  hourlyDistribution: HourlyDistribution[];
  portfolioComparison: PortfolioComparison[];
  filter: TransactionFilter;
  loading: boolean;
  error: string | null;
}

const initialState: DashboardState = {
  clients: [],
  transactions: [],
  summary: null,
  hourlyDistribution: [],
  portfolioComparison: [],
  filter: {
    startDate: new Date(new Date().setMonth(new Date().getMonth() - 1)).toISOString().split('T')[0],
    endDate: new Date().toISOString().split('T')[0],
  },
  loading: false,
  error: null,
};

// Async thunks
export const fetchClients = createAsyncThunk('dashboard/fetchClients', async () => {
  return await apiService.getClients();
});

export const fetchTransactions = createAsyncThunk(
  'dashboard/fetchTransactions',
  async (filter: TransactionFilter) => {
    return await apiService.getAllTransactions(filter);
  }
);

export const fetchAnalytics = createAsyncThunk(
  'dashboard/fetchAnalytics',
  async ({ startDate, endDate }: { startDate?: string; endDate?: string }) => {
    return await apiService.getAnalyticsSummary(startDate, endDate);
  }
);

export const updateTransaction = createAsyncThunk(
  'dashboard/updateTransaction',
  async ({ id, data }: { id: number; data: Partial<Transaction> }) => {
    await apiService.updateTransaction(id, data);
    return { id, data };
  }
);

export const deleteTransaction = createAsyncThunk(
  'dashboard/deleteTransaction',
  async (id: number) => {
    await apiService.deleteTransaction(id);
    return id;
  }
);

const dashboardSlice = createSlice({
  name: 'dashboard',
  initialState,
  reducers: {
    setFilter: (state, action: PayloadAction<Partial<TransactionFilter>>) => {
      state.filter = { ...state.filter, ...action.payload };
    },
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    // Fetch clients
    builder.addCase(fetchClients.pending, (state) => {
      state.loading = true;
    });
    builder.addCase(fetchClients.fulfilled, (state, action) => {
      state.loading = false;
      state.clients = action.payload;
    });
    builder.addCase(fetchClients.rejected, (state, action) => {
      state.loading = false;
      state.error = action.error.message || 'Failed to fetch clients';
    });

    // Fetch transactions
    builder.addCase(fetchTransactions.pending, (state) => {
      state.loading = true;
    });
    builder.addCase(fetchTransactions.fulfilled, (state, action) => {
      state.loading = false;
      state.transactions = action.payload;
    });
    builder.addCase(fetchTransactions.rejected, (state, action) => {
      state.loading = false;
      state.error = action.error.message || 'Failed to fetch transactions';
    });

    // Fetch analytics
    builder.addCase(fetchAnalytics.pending, (state) => {
      state.loading = true;
    });
    builder.addCase(fetchAnalytics.fulfilled, (state, action) => {
      state.loading = false;
      state.summary = action.payload.summary;
      state.hourlyDistribution = action.payload.hourlyDistribution;
      state.portfolioComparison = action.payload.portfolioComparison;
    });
    builder.addCase(fetchAnalytics.rejected, (state, action) => {
      state.loading = false;
      state.error = action.error.message || 'Failed to fetch analytics';
    });

    // Update transaction
    builder.addCase(updateTransaction.fulfilled, (state, action) => {
      const index = state.transactions.findIndex((t) => t.id === action.payload.id);
      if (index !== -1) {
        state.transactions[index] = { ...state.transactions[index], ...action.payload.data };
      }
    });

    // Delete transaction
    builder.addCase(deleteTransaction.fulfilled, (state, action) => {
      state.transactions = state.transactions.filter((t) => t.id !== action.payload);
    });
  },
});

export const { setFilter, clearError } = dashboardSlice.actions;
export default dashboardSlice.reducer;
