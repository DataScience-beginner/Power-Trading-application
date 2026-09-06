// Energy Schedule TypeScript types

export interface EnergyScheduleMonth {
  id: number;
  portfolio_id: number;
  year: number;
  month: number;
  month_name: string;
  total_days_completed: number;
  total_energy_savings: number;
  total_ctu_charges: number;
  total_nldc_fees: number;
  total_cost: number;
  average_ctu_losses: number;
  created_at: string;
  updated_at: string;
}

export interface EnergyScheduleDay {
  id: number;
  portfolio_id: number;
  trading_date: string;
  
  // File presence flags
  has_gdam_data: boolean;
  has_dam_data: boolean;
  has_rtm_data: boolean;
  has_sch_data: boolean;
  
  // DOR Data (GDAM)
  gdam_nldc_fee: number | null;
  gdam_ctu_charges: number | null;
  gdam_total_cost: number | null;
  
  // DOR Data (DAM)
  dam_nldc_fee: number | null;
  dam_ctu_charges: number | null;
  dam_total_cost: number | null;
  
  // DOR Data (RTM)
  rtm_nldc_fee: number | null;
  rtm_ctu_charges: number | null;
  rtm_total_cost: number | null;
  
  // SCH Data
  total_scheduled_mwh: number | null;
  ctu_losses_mwh: number | null;
  ctu_losses_percent: number | null;
  consumption_after_losses_mwh: number | null;
  
  // Calculated fields
  total_nldc_fees: number | null;
  total_ctu_charges: number | null;
  total_cost: number | null;
  energy_savings_mwh: number | null;
  is_calculated: boolean;
  
  created_at: string;
  updated_at: string;
}

export interface CTULossesCalculation {
  portfolio_id: number;
  trading_date: string;
  total_scheduled_mwh: number;
  ctu_losses_mwh: number;
  ctu_losses_percent: number;
  consumption_after_losses_mwh: number;
}

export interface CTUChargesCalculation {
  portfolio_id: number;
  trading_date: string;
  gdam_ctu_charges: number;
  dam_ctu_charges: number;
  rtm_ctu_charges: number;
  total_ctu_charges: number;
}

export interface NLDCFeesCalculation {
  portfolio_id: number;
  trading_date: string;
  gdam_nldc_fee: number;
  dam_nldc_fee: number;
  rtm_nldc_fee: number;
  total_nldc_fees: number;
}

export interface EnergySavingsCalculation {
  portfolio_id: number;
  trading_date: string;
  total_scheduled_mwh: number;
  ctu_losses_mwh: number;
  ctu_losses_percent: number;
  consumption_after_losses_mwh: number;
  energy_savings_mwh: number;
}

export interface EnergyScheduleFilter {
  portfolio_id?: number;
  year?: number;
  month?: number;
  start_date?: string;
  end_date?: string;
}

export interface ExcelDailyOutput {
  trading_date: string;
  day?: number;
  is_complete: boolean;
  missing_inputs: string[];
  b44_iex_price: number | string | null;
  b45_iex_price_per_unit: number | string | null;
  b46_eb_price: number | string | null;
  b47_eb_price_per_unit: number | string | null;
  cost_saving: number | string | null;
  within_tolerance?: boolean;
}

export interface ExcelSavingsSheet {
  rows: unknown[];
  totals: Record<string, number | string | null>;
}

export interface ExcelSlotWiseRow {
  slot: string;
  consumption_kwh: number;
  iex_delivered_kwh: number;
  balance_kwh: number;
}

export interface ExcelCalculationTrace {
  source_files: Array<{
    id: number;
    trading_date: string;
    report_type: string;
    main_category: string;
    sub_category: string;
    original_filename: string;
    transaction_count: number;
  }>;
  energy_schedule_days: Array<Record<string, any>>;
  consumption_inputs: Array<Record<string, any>>;
  daily_outputs: ExcelDailyOutput[];
  savings_sheet: ExcelSavingsSheet;
  slot_wise_consolidate: { rows: ExcelSlotWiseRow[] };
}

export interface ExcelCalculationTraceResponse {
  success: boolean;
  portfolio_id: number;
  year: number;
  month: number;
  day?: number | null;
  count: number;
  trace: ExcelCalculationTrace;
}

export interface ExcelCalculationRunResponse {
  success: boolean;
  mode: 'parity' | 'corrected' | 'compare';
  portfolio_id: number;
  year: number;
  month: number;
  day?: number | null;
  days_processed: number;
  results: unknown[];
}

export interface ExcelSavedCalculationRow {
  id: number;
  calculation_date: string;
  day: number;
  calculation_type?: string | null;
  calculated_at?: string | null;
  updated_at?: string | null;
  total_scheduled_mwh: number;
  total_cost: number;
  net_profit_loss: number;
  calculation_data?: Record<string, any> | null;
}

export interface ExcelSavedCalculationResultsResponse {
  success: boolean;
  portfolio_id: number;
  year: number;
  month: number;
  mode: 'parity' | 'corrected' | 'compare';
  day?: number | null;
  count: number;
  latest_calculated_at?: string | null;
  monthly_summary?: ExcelSavedCalculationRow | null;
  results: ExcelSavedCalculationRow[];
}

export interface EnergyScheduleConsumptionEntry {
  portfolio_id: number;
  consumption_date: string;
  c1_kwh: number;
  c2_kwh: number;
  c4_kwh: number;
  c5_kwh: number;
  base_tariff_per_unit?: number | null;
  source?: string;
  notes?: string | null;
}

export interface EnergyScheduleConsumptionResponse {
  success: boolean;
  count: number;
  records: EnergyScheduleConsumptionEntry[];
}

export interface MonthlyTrend {
  month: string;
  energy_savings: number;
  ctu_losses_percent: number;
  total_cost: number;
  days_completed: number;
}
