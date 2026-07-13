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
import type { AssistantAnswer, MarketExplanation, QualityPolicy, QualityRun } from '../types/aiInsights';
import type { AuthToken, ChatAnswer, ChatConversation, ChatUser } from '../types/chatbot';
import type { DemoProvisionResult, SolarForecast } from '../types/forecasting';
import { clearAuthSession } from '../security/session';

class ApiService {
  private api: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: import.meta.env.VITE_API_URL || '/api',
      withCredentials: true,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Response interceptor for error handling
    this.api.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        console.error('API Error:', error.response?.data || error.message);
        if (error.response?.status === 401 && sessionStorage.getItem('innowatt_access_token')) {
          clearAuthSession();
          if (!window.location.pathname.includes('/login')) window.location.assign('/client/login?reason=session-expired');
        }
        return Promise.reject(error);
      }
    );

    this.api.interceptors.request.use((config) => {
      const token = sessionStorage.getItem('innowatt_access_token');
      if (token && token !== 'cookie-session') config.headers.Authorization = `Bearer ${token}`;
      return config;
    });
  }

  private normalizeEnergyScheduleDay(day: any): EnergyScheduleDay {
    return {
      ...day,
      gdam_total_cost: day.gdam_total_cost ?? day.gdam_cost ?? 0,
      dam_total_cost: day.dam_total_cost ?? day.dam_cost ?? 0,
      rtm_total_cost: day.rtm_total_cost ?? day.rtm_cost ?? 0,
      consumption_after_losses_mwh:
        day.consumption_after_losses_mwh ?? day.total_consumption_after_losses_mwh ?? 0,
      total_nldc_fees: day.total_nldc_fees ?? day.total_nldc_fee ?? 0,
      is_calculated: day.is_calculated ?? day.is_complete ?? false,
    };
  }

  private aiHeaders(serviceKey: string) {
    return { 'X-AI-Foundation-Key': serviceKey };
  }

  private authHeaders() {
    const token = sessionStorage.getItem('innowatt_access_token');
    // In cookie-only mode this is a marker, not a JWT. Sending it as a
    // bearer token prevents the API from falling back to the HttpOnly cookie.
    if (!token || token === 'cookie-session') return {};
    return { Authorization: `Bearer ${token}` };
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

    const response = await this.api.get<EnergyScheduleDay[] | { days?: EnergyScheduleDay[] }>(
      `/energy-schedule/days?${params.toString()}`
    );
    const payload = response.data;
    const days = Array.isArray(payload) ? payload : payload.days || [];
    return days.map((day) => this.normalizeEnergyScheduleDay(day));
  }

  // Get specific day entry
  async getEnergyScheduleDay(portfolioId: number, tradingDate: string): Promise<EnergyScheduleDay> {
    const response = await this.api.get<EnergyScheduleDay[] | { days?: EnergyScheduleDay[] }>(
      `/energy-schedule/days?portfolio_id=${portfolioId}&start_date=${tradingDate}&end_date=${tradingDate}`
    );
    const payload = response.data;
    const days = Array.isArray(payload) ? payload : payload.days || [];
    const day = days[0];
    if (!day) {
      throw new Error(`Energy schedule day not found for portfolio ${portfolioId} on ${tradingDate}`);
    }
    return this.normalizeEnergyScheduleDay(day);
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

  async runDataQualityAnalysis(params: {
    serviceKey: string;
    clientId: number;
    portfolioId?: number;
    startDate: string;
    endDate: string;
    dataClassification: 'synthetic' | 'actual' | 'mixed' | 'unknown';
    policy: QualityPolicy;
  }): Promise<QualityRun> {
    const response = await this.api.post<QualityRun>(
      '/v1/ai-insights/quality/analyze',
      {
        client_id: params.clientId,
        portfolio_id: params.portfolioId,
        start_date: params.startDate,
        end_date: params.endDate,
        correlation_id: crypto.randomUUID(),
        data_classification: params.dataClassification,
        policy: params.policy,
      },
      { headers: this.aiHeaders(params.serviceKey) }
    );
    return response.data;
  }

  async explainMarket(params: {
    serviceKey: string;
    clientId: number;
    portfolioId?: number;
    startDate: string;
    endDate: string;
    question: string;
  }): Promise<MarketExplanation> {
    const response = await this.api.post<MarketExplanation>(
      '/v1/ai-insights/market/explain',
      {
        client_id: params.clientId,
        portfolio_id: params.portfolioId,
        start_date: params.startDate,
        end_date: params.endDate,
        question: params.question,
        correlation_id: crypto.randomUUID(),
      },
      { headers: this.aiHeaders(params.serviceKey) }
    );
    return response.data;
  }

  async askInsightAssistant(params: {
    serviceKey: string;
    clientId: number;
    portfolioId?: number;
    startDate: string;
    endDate: string;
    question: string;
    conversationId?: string;
  }): Promise<AssistantAnswer> {
    const response = await this.api.post<AssistantAnswer>(
      '/v1/ai-insights/assistant/query',
      {
        client_id: params.clientId,
        portfolio_id: params.portfolioId,
        start_date: params.startDate,
        end_date: params.endDate,
        question: params.question,
        correlation_id: crypto.randomUUID(),
        conversation_id: params.conversationId,
      },
      { headers: this.aiHeaders(params.serviceKey) }
    );
    return response.data;
  }

  async login(email: string, password: string): Promise<AuthToken> {
    const response = await this.api.post<AuthToken>('/v1/auth/login', { email, password });
    sessionStorage.setItem('innowatt_access_token', (import.meta.env.VITE_COOKIE_AUTH_ONLY ?? 'true') === 'true' ? 'cookie-session' : response.data.access_token);
    sessionStorage.setItem('innowatt_user', JSON.stringify(response.data.user));
    return response.data;
  }

  async identityLogin(email: string, password: string, portal: 'admin' | 'client', mfaCode?: string): Promise<AuthToken> {
    const response = await this.api.post<AuthToken>('/v1/identity/login', { email, password, portal, mfa_code: mfaCode || null });
    sessionStorage.setItem('innowatt_access_token', (import.meta.env.VITE_COOKIE_AUTH_ONLY ?? 'true') === 'true' ? 'cookie-session' : response.data.access_token);
    sessionStorage.setItem('innowatt_user', JSON.stringify(response.data.user));
    return response.data;
  }

  async logout(): Promise<void> {
    await this.api.post('/v1/auth/logout');
  }

  async beginMfaEnrollment(): Promise<{ factor_id: string; secret: string; provisioning_uri: string; message: string }> {
    const response = await this.api.post('/v1/identity/mfa/enroll');
    return response.data;
  }

  async verifyMfaEnrollment(code: string): Promise<{ enabled: boolean; recovery_codes: string[]; message: string }> {
    const response = await this.api.post('/v1/identity/mfa/verify', { code });
    return response.data;
  }

  async requestPasswordRecovery(identifier: string, channel: 'email' | 'sms', portal: 'admin' | 'client'): Promise<string> {
    const response = await this.api.post<{ accepted: boolean; message: string }>('/v1/identity/recovery/request', {
      identifier, channel, portal, correlation_id: crypto.randomUUID(),
    });
    return response.data.message;
  }

  async confirmPasswordRecovery(identifier: string, code: string, newPassword: string, portal: 'admin' | 'client'): Promise<string> {
    const response = await this.api.post<{ success: boolean; message: string }>('/v1/identity/recovery/confirm', {
      identifier, code, new_password: newPassword, portal, correlation_id: crypto.randomUUID(),
    });
    return response.data.message;
  }

  async bootstrapAdmin(serviceKey: string, email: string, password: string, displayName: string): Promise<ChatUser> {
    const response = await this.api.post<ChatUser>(
      '/v1/auth/bootstrap-admin',
      { email, password, display_name: displayName },
      { headers: this.aiHeaders(serviceKey) }
    );
    return response.data;
  }

  async recoverAdmin(serviceKey: string, email: string, newPassword: string): Promise<string> {
    const response = await this.api.post<{ success: boolean; message: string }>(
      '/v1/auth/recover-admin',
      { email, new_password: newPassword },
      { headers: this.aiHeaders(serviceKey) }
    );
    return response.data.message;
  }

  async changePassword(currentPassword: string, newPassword: string): Promise<string> {
    const response = await this.api.post<{ success: boolean; message: string }>('/v1/auth/change-password', {
      current_password: currentPassword,
      new_password: newPassword,
    });
    return response.data.message;
  }

  async getCurrentUser(): Promise<ChatUser> {
    const response = await this.api.get<ChatUser>('/v1/auth/me', { headers: this.authHeaders() });
    return response.data;
  }

  async runSolarForecast(clientId: number, portfolioId: number, horizonDays: number): Promise<SolarForecast> {
    const response = await this.api.post<SolarForecast>('/v1/forecasts/solar/run', {
      client_id: clientId,
      portfolio_id: portfolioId,
      horizon_days: horizonDays,
      correlation_id: crypto.randomUUID(),
    });
    return response.data;
  }

  async provisionDemoTenants(defaultPassword: string): Promise<DemoProvisionResult> {
    const response = await this.api.post<DemoProvisionResult>('/v1/admin/demo/provision', {
      default_password: defaultPassword,
      days_of_history: 30,
      portfolios_per_client: 2,
      reset_existing_passwords: true,
    });
    return response.data;
  }

  async createChatConversation(clientId: number, portfolioId?: number): Promise<ChatConversation> {
    const response = await this.api.post<ChatConversation>(
      '/v1/chat/conversations',
      { client_id: clientId, portfolio_id: portfolioId, title: 'Energy assistant' },
      { headers: this.authHeaders() }
    );
    return response.data;
  }

  async sendChatMessage(
    conversationId: string,
    question: string,
    startDate?: string,
    endDate?: string
  ): Promise<ChatAnswer> {
    const response = await this.api.post<ChatAnswer>(
      `/v1/chat/conversations/${conversationId}/messages`,
      {
        question,
        start_date: startDate ? `${startDate}T00:00:00` : null,
        end_date: endDate ? `${endDate}T23:59:59` : null,
      },
      { headers: this.authHeaders() }
    );
    return response.data;
  }
}

export const apiService = new ApiService();
export default apiService;
