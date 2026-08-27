export type RuntimeState = "ready" | "idle" | "error";

export interface HealthStatus {
  status: "ready" | "setup_required" | "error";
  local: boolean;
  runtime: RuntimeState;
  index_ready: boolean;
  chunk_count?: number;
  message: string;
}

export type DocumentStatus =
  | "ready"
  | "pending"
  | "queued"
  | "extracting"
  | "processing"
  | "embedding"
  | "storing";

export interface KnowledgeDocument {
  filename: string;
  title: string;
  file_type: string;
  status: DocumentStatus;
  chunk_count: number;
}

export interface DocumentDetail extends KnowledgeDocument {
  character_count: number;
  content: string;
}

export interface DeleteDocumentResult {
  filename: string;
  document_count: number;
  chunk_count: number;
}

export interface SourceReference {
  filename: string;
  chunk_index: number;
  score: number;
}

export interface ChatResponse {
  answer: string;
  sources: SourceReference[];
  used_fallback: boolean;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: SourceReference[];
  usedFallback?: boolean;
}

export type UploadStatus =
  | "uploading"
  | "queued"
  | "extracting"
  | "processing"
  | "embedding"
  | "storing"
  | "completed"
  | "error";

export interface UploadJob {
  id: string;
  filename: string;
  status: Exclude<UploadStatus, "uploading">;
  message: string;
  created_at: number;
  document_count: number | null;
  chunk_count: number | null;
}
