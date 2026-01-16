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

export interface MonthlyTrend {
  month: string;
  energy_savings: number;
  ctu_losses_percent: number;
  total_cost: number;
  days_completed: number;
}
