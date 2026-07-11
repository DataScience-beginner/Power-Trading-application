import axios, { AxiosInstance, AxiosError } from 'axios';
import type {
  Client,
  Transaction,
  AnalyticsSummary,
  HourlyDistribution,
  PortfolioComparison,
  TransactionFilter,
  FileUploadResponse,
} from '../types';
import type {
  EnergyScheduleMonth,
  EnergyScheduleDay,
  EnergyScheduleFilter,
  CTULossesCalculation,
  CTUChargesCalculation,
  NLDCFeesCalculation,
  EnergySavingsCalculation,
} from '../types/energySchedule';

class ApiService {
  private api: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: '/api',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Response interceptor for error handling
    this.api.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        console.error('API Error:', error.response?.data || error.message);
        return Promise.reject(error);
      }
    );
  }

  // Client endpoints
  async getClients(): Promise<Client[]> {
    const response = await this.api.get<{ success: boolean; clients: Client[] }>('/clients');
    return response.data.clients || [];
  }

  // Transaction endpoints
  async getAllTransactions(filter?: TransactionFilter): Promise<Transaction[]> {
    const params = new URLSearchParams();
    if (filter?.portfolio) params.append('portfolio', filter.portfolio);
    if (filter?.startDate) params.append('start_date', filter.startDate);
    if (filter?.endDate) params.append('end_date', filter.endDate);
    if (filter?.reportType) params.append('report_type', filter.reportType);
    if (filter?.transactionType) params.append('transaction_type', filter.transactionType);

    const response = await this.api.get<{ success: boolean; transactions: Transaction[] }>(
      `/transactions/all?${params.toString()}`
    );
    return response.data.transactions || [];
  }

  async updateTransaction(id: number, data: Partial<Transaction>): Promise<boolean> {
    const response = await this.api.put(`/transactions/${id}`, data);
    return response.data.success;
  }

  async deleteTransaction(id: number): Promise<boolean> {
    const response = await this.api.delete(`/transactions/${id}`);
    return response.data.success;
  }

  // Analytics endpoints
  async getAnalyticsSummary(startDate?: string, endDate?: string): Promise<{
    summary: AnalyticsSummary;
    hourlyDistribution: HourlyDistribution[];
    portfolioComparison: PortfolioComparison[];
  }> {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);

    const response = await this.api.get(`/analytics/summary?${params.toString()}`);
    return {
      summary: response.data.summary || {},
      hourlyDistribution: response.data.hourly_distribution || [],
      portfolioComparison: response.data.portfolio_comparison || [],
    };
  }

  // File upload endpoints
  async uploadFile(file: File, fileType: 'DOR' | 'SCH'): Promise<FileUploadResponse> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('file_type', fileType);

    const response = await this.api.post<FileUploadResponse>('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  // Health check
  async healthCheck(): Promise<boolean> {
    try {
      const response = await this.api.get('/health');
      return response.data.status === 'healthy';
    } catch {
      return false;
    }
  }

  // Energy Schedule endpoints
  async calculateEnergySchedule(calculationDate?: string): Promise<any> {
    const params = new URLSearchParams();
    if (calculationDate) {
      params.append('calculation_date', calculationDate);
    }
    
    const response = await this.api.post(`/calculate/energy-schedule?${params.toString()}`);
    return response.data;
  }

  async getEnergyScheduleStatus(startDate?: string, endDate?: string): Promise<any> {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);

    const response = await this.api.get(`/energy-schedule/status?${params.toString()}`);
    return response.data;
  }

  // Get all month sheets
  async getEnergyScheduleMonths(filter?: EnergyScheduleFilter): Promise<EnergyScheduleMonth[]> {
    const params = new URLSearchParams();
    if (filter?.portfolio_id) params.append('portfolio_id', filter.portfolio_id.toString());
    if (filter?.year) params.append('year', filter.year.toString());
    if (filter?.month) params.append('month', filter.month.toString());

    const response = await this.api.get<EnergyScheduleMonth[]>(
      `/energy-schedule/months?${params.toString()}`
    );
    return response.data;
  }

  // Get daily entries
  async getEnergyScheduleDays(filter?: EnergyScheduleFilter): Promise<EnergyScheduleDay[]> {
    const params = new URLSearchParams();
    if (filter?.portfolio_id) params.append('portfolio_id', filter.portfolio_id.toString());
    if (filter?.start_date) params.append('start_date', filter.start_date);
    if (filter?.end_date) params.append('end_date', filter.end_date);

    const response = await this.api.get<EnergyScheduleDay[]>(
      `/energy-schedule/days?${params.toString()}`
    );
    return response.data;
  }

  // Get specific day entry
  async getEnergyScheduleDay(portfolioId: number, tradingDate: string): Promise<EnergyScheduleDay> {
    const response = await this.api.get<EnergyScheduleDay>(
      `/energy-schedule/day/${portfolioId}/${tradingDate}`
    );
    return response.data;
  }

  // Calculation endpoints
  async getCTULosses(portfolioId: number, tradingDate: string): Promise<CTULossesCalculation> {
    const response = await this.api.get<CTULossesCalculation>(
      `/energy-schedule/calculations/ctu-losses?portfolio_id=${portfolioId}&trading_date=${tradingDate}`
    );
    return response.data;
  }

  async getCTUCharges(portfolioId: number, tradingDate: string): Promise<CTUChargesCalculation> {
    const response = await this.api.get<CTUChargesCalculation>(
      `/energy-schedule/calculations/ctu-charges?portfolio_id=${portfolioId}&trading_date=${tradingDate}`
    );
    return response.data;
  }

  async getNLDCFees(portfolioId: number, tradingDate: string): Promise<NLDCFeesCalculation> {
    const response = await this.api.get<NLDCFeesCalculation>(
      `/energy-schedule/calculations/nldc-fees?portfolio_id=${portfolioId}&trading_date=${tradingDate}`
    );
    return response.data;
  }

  async getEnergySavings(portfolioId: number, tradingDate: string): Promise<EnergySavingsCalculation> {
    const response = await this.api.get<EnergySavingsCalculation>(
      `/energy-schedule/calculations/energy-savings?portfolio_id=${portfolioId}&trading_date=${tradingDate}`
    );
    return response.data;
  }
}

export const apiService = new ApiService();
export default apiService;
