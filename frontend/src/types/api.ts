export interface User {
  id: string;
  email: string;
  full_name?: string | null;
  company_name?: string | null;
  is_active: boolean;
  created_at: string;
}

export interface Token {
  access_token: string;
  token_type: string;
}

export interface CriteriaPreset {
  id: string;
  user_id: string;
  name: string;
  description: string | null;
  criteria: SearchCriteria;
  is_public: boolean;
  created_at: string;
  updated_at: string;
}

export interface SearchCriteria {
  locations?: string[];
  moq_min?: number;
  moq_max?: number;
  certifications_of_interest?: string[];
  materials?: string[];
  production_methods?: string[];
  budget_tier?: string | string[];
  additional_notes?: string;
  custom_queries?: string[];
}

export interface SearchResponse {
  id: string;
  user_id: string;
  criteria_preset_id: string | null;
  criteria: SearchCriteria;
  search_queries: Record<string, unknown> | null;
  search_mode: string;
  status: string;
  progress: number;
  current_step: string | null;
  current_detail: string | null;
  total_found: number;
  started_at: string | null;
  completed_at: string | null;
  error_message: string | null;
  created_at: string;
}

export interface SearchStatus {
  id: string;
  status: string;
  progress: number;
  current_step: string | null;
  current_detail: string | null;
  total_found: number;
  started_at: string | null;
  completed_at: string | null;
  error_message: string | null;
}

export interface Manufacturer {
  id: string;
  search_id: string;
  name: string;
  website: string;
  location: string | null;
  contact: Record<string, string> | null;
  materials: string[] | null;
  production_methods: string[] | null;
  certifications: string[] | null;
  moq: number | null;
  moq_description: string | null;
  match_score: number;
  confidence: string;
  scoring_breakdown: ScoringBreakdown | null;
  notes: string | null;
  source_url: string;
  scraped_at: string | null;
  user_notes: string | null;
  user_tags: string[] | null;
  is_favorite: boolean;
  contacted_at: string | null;
  status: string | null;
  next_followup_date: string | null;
  created_at: string;
  updated_at: string;
}

export interface ScoringBreakdown {
  location?: { score: number; max: number; reason?: string };
  moq?: { score: number; max: number; reason?: string };
  certifications?: { score: number; max: number; reason?: string };
  materials?: { score: number; max: number; reason?: string };
  production?: { score: number; max: number; reason?: string };
  bonuses?: { score: number; details?: string[] };
  deductions?: { score: number; details?: string[] };
  [key: string]: unknown;
}

export interface ManufacturerUpdate {
  user_notes?: string;
  user_tags?: string[];
  is_favorite?: boolean;
  contacted_at?: string;
  status?: string | null;
  next_followup_date?: string | null;
  // Data fields
  name?: string;
  website?: string;
  location?: string | null;
  contact?: Record<string, string> | null;
  materials?: string[] | null;
  production_methods?: string[] | null;
  certifications?: string[] | null;
  moq?: number | null;
  moq_description?: string | null;
  notes?: string | null;
}

export interface ManufacturerCreate {
  name: string;
  website?: string;
  location?: string;
  contact?: Record<string, string>;
  materials?: string[];
  production_methods?: string[];
  certifications?: string[];
  moq?: number;
  moq_description?: string;
  notes?: string;
}

export type ActivityType =
  | "email"
  | "call"
  | "meeting"
  | "quote_received"
  | "sample_requested"
  | "note";

export type ManufacturerStatus =
  | "new"
  | "contacted"
  | "quoted"
  | "negotiating"
  | "won"
  | "lost";

export interface ContactActivity {
  id: string;
  manufacturer_id: string;
  user_id: string;
  activity_type: ActivityType;
  subject: string;
  content: string | null;
  contact_date: string;
  reminder_date: string | null;
  created_at: string;
}

export interface ContactActivityCreate {
  activity_type: ActivityType;
  subject: string;
  content?: string;
  contact_date: string;
  reminder_date?: string;
}

export interface ContactActivityUpdate {
  activity_type?: ActivityType;
  subject?: string;
  content?: string | null;
  contact_date?: string;
  reminder_date?: string | null;
}
