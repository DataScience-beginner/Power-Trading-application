export interface QualityPolicy {
  policy_version: string;
  expected_report_types: string[];
  expected_blocks_per_file: number;
  minimum_rate: number;
  maximum_rate: number | null;
  allow_negative_quantity: boolean;
  require_time_block_start: boolean;
}

export interface QualityFinding {
  id: string;
  rule_id: string;
  severity: 'critical' | 'high' | 'medium' | 'low' | 'info';
  category: string;
  title: string;
  description: string;
  evidence: Array<Record<string, unknown>>;
  recommended_action: string;
  confidence: number;
  status: string;
}

export interface QualityRun {
  id: string;
  correlation_id: string;
  client_id: number;
  portfolio_id: number | null;
  start_date: string;
  end_date: string;
  policy_version: string;
  policy_configuration: QualityPolicy;
  engine_version: string;
  files_evaluated: number;
  transactions_evaluated: number;
  finding_counts: Record<string, number>;
  data_classification: string;
  findings: QualityFinding[];
  limitations: string[];
}

export interface ExplanationMetric {
  name: string;
  value: string | number;
  unit?: string | null;
}

export interface EvidenceItem {
  source_type: string;
  source_id: string;
  metric: string;
  value: unknown;
  unit?: string | null;
}

export interface MarketExplanation {
  explanation_id: string;
  question: string;
  answer: string;
  summary: string;
  metrics: ExplanationMetric[];
  evidence: EvidenceItem[];
  confidence: number;
  limitations: string[];
  data_classification: string;
  engine: string;
  human_review_required: boolean;
}

export interface AssistantAnswer {
  conversation_id: string;
  intent: string;
  answer: string;
  suggested_questions: string[];
  explanation?: MarketExplanation | null;
  quality_summary?: Record<string, number> | null;
  safety_notice: string;
}
