import type {
  ChatResponse,
  DeleteDocumentResult,
  DocumentDetail,
  HealthStatus,
  KnowledgeDocument,
  UploadJob,
} from "./types";

async function parseResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let message = "İstek tamamlanamadı.";
    try {
      const payload = (await response.json()) as { detail?: string };
      if (payload.detail) message = payload.detail;
    } catch {
      // Sunucu JSON döndürmediyse güvenli genel mesajı kullan.
    }
    throw new Error(message);
  }
  return (await response.json()) as T;
}

export async function getHealth(): Promise<HealthStatus> {
  return parseResponse<HealthStatus>(await fetch("/api/health"));
}

export async function getDocuments(): Promise<KnowledgeDocument[]> {
  const result = await parseResponse<{ documents: KnowledgeDocument[] }>(
    await fetch("/api/documents"),
  );
  return result.documents;
}

export async function getDocument(filename: string): Promise<DocumentDetail> {
  return parseResponse<DocumentDetail>(
    await fetch(`/api/documents/${encodeURIComponent(filename)}`),
  );
}

export async function deleteDocument(filename: string): Promise<DeleteDocumentResult> {
  const result = await parseResponse<{ deleted: DeleteDocumentResult }>(
    await fetch(`/api/documents/${encodeURIComponent(filename)}`, { method: "DELETE" }),
  );
  return result.deleted;
}

export async function askQuestion(question: string): Promise<ChatResponse> {
  return parseResponse<ChatResponse>(
    await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    }),
  );
}

export function uploadPdf(
  file: File,
  onProgress: (percentage: number) => void,
): Promise<UploadJob> {
  return new Promise((resolve, reject) => {
    const request = new XMLHttpRequest();
    const form = new FormData();
    form.append("file", file);
    request.open("POST", "/api/documents");
    request.upload.addEventListener("progress", (event) => {
      if (event.lengthComputable) {
        onProgress(Math.round((event.loaded / event.total) * 100));
      }
    });
    request.addEventListener("load", () => {
      try {
        const payload = JSON.parse(request.responseText) as {
          job?: UploadJob;
          detail?: string;
        };
        if (request.status < 200 || request.status >= 300 || !payload.job) {
          reject(new Error(payload.detail || "PDF yüklenemedi."));
          return;
        }
        resolve(payload.job);
      } catch {
        reject(new Error("Sunucudan geçersiz yükleme yanıtı alındı."));
      }
    });
    request.addEventListener("error", () =>
      reject(new Error("Backend bağlantısı kurulamadı.")),
    );
    request.send(form);
  });
}

export async function getUploadJob(jobId: string): Promise<UploadJob> {
  const result = await parseResponse<{ job: UploadJob }>(
    await fetch(`/api/documents/jobs/${encodeURIComponent(jobId)}`),
  );
  return result.job;
}
