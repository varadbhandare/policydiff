export type ChangeType = 'ADDED' | 'REMOVED' | 'MODIFIED' | 'UNCHANGED';
export type PriorityLevel = 'Critical' | 'High' | 'Medium' | 'Low';

export interface EntityDiffItem {
  entity_type: string;
  old_value?: string;
  new_value?: string;
  details?: string;
}

export interface PolicyChange {
  id: string;
  comparison_id: string;
  change_type: ChangeType;
  category: string;
  priority: PriorityLevel;
  priority_rationale?: string;
  old_text?: string;
  new_text?: string;
  old_section?: string;
  new_section?: string;
  old_page?: number;
  new_page?: number;
  similarity_score: number;
  alignment_confidence: number;
  explanation: string;
  reason?: string;
  entities_diff: EntityDiffItem[];
  is_reviewed: boolean;
}

export interface ComparisonSummary {
  total_changes: number;
  added_count: number;
  removed_count: number;
  modified_count: number;
  unchanged_count: number;
  high_priority_count: number;
}

export interface ComparisonResponse {
  id: string;
  title: string;
  institution?: string;
  old_filename: string;
  new_filename: string;
  old_version: string;
  new_version: string;
  created_at: string;
  status: string;
  summary: ComparisonSummary;
  nlp_engine: string;
  changes: PolicyChange[];
}

export interface ComparisonListItem {
  id: string;
  title: string;
  institution?: string;
  old_filename: string;
  new_filename: string;
  old_version: string;
  new_version: string;
  created_at: string;
  total_changes: number;
  high_priority_count: number;
  added_count: number;
  removed_count: number;
  modified_count: number;
}

export interface EvaluationMetrics {
  total_samples: number;
  accuracy: number;
  macro_precision: number;
  macro_recall: number;
  macro_f1: number;
  per_class: Record<string, { precision: number; recall: number; f1_score: number; support: number }>;
  confusion_matrix: Record<string, Record<string, number>>;
}
