export interface SolarForecastPoint {
  forecast_date: string;
  p10_kwh: number;
  p50_kwh: number;
  p90_kwh: number;
  irradiation_kwh_m2: number;
  temperature_c: number;
  cloud_cover_pct: number;
}

export interface SolarForecast {
  run_id: string;
  client_id: number;
  portfolio_id: number;
  contract_version: string;
  model_name: string;
  model_version: string;
  weather_provider: string;
  weather_source: string;
  data_classification: string;
  location: { latitude: number; longitude: number };
  capacity_kw: number;
  training_points: number;
  calibration_factor: number;
  backtest_metrics: { mae_kwh?: number | null; mape_pct?: number | null; backtest_points: number };
  confidence: number;
  limitations: string[];
  human_review_required: boolean;
  points: SolarForecastPoint[];
  created_at: string;
}

export interface DemoProvisionResult {
  status: string;
  data_classification: string;
  clients_total: number;
  records_created: Record<string, number>;
  tenants: Array<{
    client_id: number;
    entity_id: string;
    entity_name: string;
    portfolio_ids: number[];
    portfolio_codes: string[];
    user_email: string;
  }>;
  note: string;
}
