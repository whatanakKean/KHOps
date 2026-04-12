export interface PipelineSummary {
  id: number;
  name: string;
  version: string;
  description?: string;
  definition: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface PipelineListResponse {
  pipelines: PipelineSummary[];
  total: number;
  skip: number;
  limit: number;
}
