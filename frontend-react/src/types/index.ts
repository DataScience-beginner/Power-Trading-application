// Client types
export interface Client {
  id: number;
  entity_id: string;
  entity_name: string;
  portfolio_count: number;
  portfolios: Portfolio[];
}

// Portfolio types
export interface Portfolio {
  id: number;
  client_id: number;
  portfolio_code: string;
  portfolio_name: string;
  state?: string;
  is_active?: boolean;
}

// Transaction types
export interface Transaction {
  id: number;
  file_id: number;
  date: string;
  time_slot: string;
  transaction_type: 'buy' | 'sell' | 'scheduling';
  report_type: string;
  portfolio_code: string;
  quantity_mw: number;
  rate_per_mwh: number;
  amount: number;
  buyer_id?: string;
  seller_id?: string;
  delivery_date?: string;
  region?: string;
  station?: string;
  // Aliases for backward compatibility
  quantity?: number;  // Alias for quantity_mw
  rate?: number;      // Alias for rate_per_mwh
  type?: 'BUY' | 'SELL' | 'buy' | 'sell';  // Alias for transaction_type
}

// Daily File types
export interface DailyFile {
  id: number;
  portfolio_id: number;
  file_type: 'DOR' | 'SCH';
  market_type: string;
  upload_date: string;
  file_date: string;
  filename: string;
  parsed_data?: any;
}

// Analytics types
export interface AnalyticsSummary {
  dor_files: number;
  sch_files: number;
  total_files: number;
  total_transactions: number;
  net_amount: number;
  buy_transactions: number;
  sell_transactions: number;
  scheduling_transactions: number;
}

export interface HourlyDistribution {
  hour: number;
  avg_quantity: number;
  avg_rate?: number;
  transaction_count?: number;
}

export interface PortfolioComparison {
  portfolio_code: string;
  dor_quantity: number;
  sch_quantity: number;
  deviation: number;
  deviation_percentage: number;
}

// API Response types
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
}

export interface TransactionsResponse {
  success: boolean;
  count: number;
  transactions: Transaction[];
}

export interface ClientsResponse {
  success: boolean;
  count: number;
  clients: Client[];
}

export interface AnalyticsResponse {
  success: boolean;
  summary: AnalyticsSummary;
  hourly_distribution: HourlyDistribution[];
  portfolio_comparison: PortfolioComparison[];
}

// Filter types
export interface DateFilter {
  startDate: string;
  endDate: string;
}

export interface TransactionFilter extends DateFilter {
  portfolio?: string;
  reportType?: string;
  transactionType?: string;
}

// Upload types
export interface FileUploadResponse {
  success: boolean;
  message: string;
  file_id?: number;
  transactions_count?: number;
}
