export type PortalType = "admin" | "client";

export type LoginPayload = {
  email: string;
  password: string;
  portal: PortalType;
};

export type AuthenticatedUser = {
  id: string;
  tenant_id: string | null;
  email: string;
  full_name: string;
  role_codes: string[];
};

export type LoginResult = {
  access_token: string;
  token_type: string;
  user: AuthenticatedUser;
};

export type AuthSession = {
  portal: PortalType;
  token: string;
  user: AuthenticatedUser;
};

export type PortalSummary = {
  portal: PortalType;
  user: AuthenticatedUser;
  capabilities: string[];
};

export type WorkbookListItem = {
  workbook_id: string;
  file_name: string;
  workbook_month: string | null;
  status: string;
  uploaded_at: string;
  uploaded_by_user_id: string | null;
  solar_working_rows: number;
};

export type WorkbookRow = {
  reading_date: string;
  tneb_total: number;
  iex_total: number;
  solar_total: number;
  tneb_balance: number;
  banking_balance: number;
};

export type WorkbookUploadResponse = {
  workbook_id: string;
  file_name: string;
  workbook_month: string | null;
  status: string;
  sheet_summaries: Array<{
    sheet_name: string;
    sheet_type: string;
    status: string;
    row_count: number | null;
    validation_summary: string | null;
  }>;
  calculation_summary: Record<string, string | number | null>;
  preview_rows: WorkbookRow[];
};

export type WorkbookResultsResponse = {
  workbook_id: string;
  workbook_month: string | null;
  status: string;
  rows: WorkbookRow[];
};

export type AdminOverviewMetric = {
  label: string;
  value: number;
};

export type AdminOverviewResponse = {
  metrics: AdminOverviewMetric[];
  recent_workbooks: WorkbookListItem[];
  tenant_codes: string[];
  user_emails: string[];
};
