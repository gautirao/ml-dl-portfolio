export interface PlannerPlan {
  intent: string;
  tool:
    | "spending_summary"
    | "top_merchants"
    | "compare_periods"
    | "recurring_payments"
    | "transaction_search"
    | "category_summary"
    | "clarification"
    | "out_of_scope";
  arguments: Record<string, any>;
  confidence: number;
  requires_clarification: boolean;
  clarification_question?: string;
  risk_level: "low" | "medium" | "high";
  reasoning_summary: string;
}

export interface ToolResult {
  tool_name: string;
  arguments: Record<string, any>;
  result: any;
  evidence: Record<string, any>;
  execution_status: "success" | "failed";
}

export interface Guardrails {
  input_allowed: boolean;
  plan_valid: boolean;
  output_verified: boolean;
}

export interface ChatResponse {
  answer: string;
  plan?: PlannerPlan;
  tool_result?: ToolResult;
  evidence?: Record<string, any>;
  guardrails: Guardrails;
}

export interface Transaction {
  id: string;
  source_bank: string;
  source_file_id: string;
  account_name: string | null;
  transaction_date: string;
  description: string;
  merchant: string | null;
  amount: number;
  currency: string;
  direction: "inflow" | "outflow";
  category: string;
  transaction_fingerprint: string;
  raw_row_json?: string;
}

export interface ImportPreview {
  filename: string;
  detected_bank: string;
  confidence: number;
  headers: string[];
  row_count: number;
  preview_rows: Record<string, any>[];
  proposed_mapping: Record<string, any>;
  warnings: string[];
}

export interface ImportSummary {
  detected_bank: string;
  filename: string;
  source_file_id: string;
  row_count: number;
  imported_count: number;
  skipped_count: number;
  duplicate_count: number;
  date_min: string | null;
  date_max: string | null;
  warnings: string[];
}

export interface SpendingSummary {
  total_outflow: number;
  total_inflow: number;
  net_amount: number;
  transaction_count: number;
}

export interface TopMerchant {
  merchant: string;
  total_amount: number;
  count: number;
}

export interface CategorySummaryItem {
  category: string;
  total_amount: number;
  count: number;
  percentage: number;
}

export interface RecurringPayment {
  merchant: string;
  frequency_days: number;
  avg_amount: number;
  count: number;
  last_date: string;
}

export interface Analytics {
  spending_summary: SpendingSummary;
  top_merchants: TopMerchant[];
  category_summary: CategorySummaryItem[];
  recurring_payments: RecurringPayment[];
}
