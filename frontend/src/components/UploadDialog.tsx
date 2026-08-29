import {
  Check,
  FileUp,
  LoaderCircle,
  UploadCloud,
  X,
  XCircle,
} from "../icons";
import { useEffect, useRef, useState } from "react";
import { getUploadJob, uploadPdf } from "../api";
import type { UploadJob, UploadStatus } from "../types";

interface UploadDialogProps {
  open: boolean;
  onClose: () => void;
  onComplete: () => void;
}

const stageOrder: UploadStatus[] = [
  "uploading",
  "extracting",
  "processing",
  "embedding",
  "storing",
  "completed",
];

const stageLabels: Record<UploadStatus, string> = {
  uploading: "Yükleniyor",
  queued: "İşlem sırası bekleniyor",
  extracting: "Metin çıkarılıyor",
  processing: "Parçalara ayrılıyor",
  embedding: "Embedding oluşturuluyor",
  storing: "Knowledge base güncelleniyor",
  completed: "Knowledge base'e eklendi",
  error: "Hata oluştu",
};

export function UploadDialog({ open, onClose, onComplete }: UploadDialogProps) {
  const [file, setFile] = useState<File | null>(null);
  const [dragging, setDragging] = useState(false);
  const [status, setStatus] = useState<UploadStatus | null>(null);
  const [progress, setProgress] = useState(0);
  const [message, setMessage] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);
  const closeRef = useRef<HTMLButtonElement>(null);
  const dialogRef = useRef<HTMLElement>(null);

  const busy = status !== null && !["completed", "error"].includes(status);

  useEffect(() => {
    if (!open) return;
    closeRef.current?.focus();
    const onKey = (event: KeyboardEvent) => {
      if (event.key === "Escape" && !busy) onClose();
      if (event.key === "Tab") {
        const focusable = Array.from(
          dialogRef.current?.querySelectorAll<HTMLElement>(
            'button:not([disabled]), input:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])',
          ) ?? [],
        );
        if (!focusable.length) return;
        const first = focusable[0];
        const last = focusable[focusable.length - 1];
        if (event.shiftKey && document.activeElement === first) {
          event.preventDefault();
          last.focus();
        } else if (!event.shiftKey && document.activeElement === last) {
          event.preventDefault();
          first.focus();
        }
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [busy, onClose, open]);

  useEffect(() => {
    if (!open) {
      setFile(null);
      setStatus(null);
      setProgress(0);
      setMessage("");
    }
  }, [open]);

  if (!open) return null;

  const chooseFile = (candidate?: File) => {
    if (!candidate) return;
    if (candidate.type !== "application/pdf" && !candidate.name.toLowerCase().endsWith(".pdf")) {
      setStatus("error");
      setMessage("Yalnızca PDF dosyaları desteklenir.");
      return;
    }
    if (candidate.size > 20 * 1024 * 1024) {
      setStatus("error");
      setMessage("PDF dosyası 20 MB sınırını aşıyor.");
      return;
    }
    setFile(candidate);
    setStatus(null);
    setMessage("");
  };

  const pollJob = async (initialJob: UploadJob) => {
    let job = initialJob;
    while (!['completed', 'error'].includes(job.status)) {
      setStatus(job.status);
      setMessage(job.message);
      await new Promise((resolve) => window.setTimeout(resolve, 700));
      job = await getUploadJob(job.id);
    }
    setStatus(job.status);
    setMessage(job.message);
    if (job.status === "completed") onComplete();
  };

  const startUpload = async () => {
    if (!file || busy) return;
    setStatus("uploading");
    setMessage("PDF yerel sunucuya aktarılıyor.");
    setProgress(0);
    try {
      const job = await uploadPdf(file, setProgress);
      setProgress(100);
      await pollJob(job);
    } catch (error) {
      setStatus("error");
      setMessage(error instanceof Error ? error.message : "PDF işlenemedi.");
    }
  };

  const currentIndex = status ? stageOrder.indexOf(status) : -1;

  return (
    <div className="fixed inset-0 z-[70] grid place-items-center bg-slate-950/25 p-4 backdrop-blur-[3px]" onMouseDown={(event) => {
      if (event.target === event.currentTarget && !busy) onClose();
    }}>
      <section
        ref={dialogRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby="upload-title"
        className="animate-dialog w-full max-w-[540px] overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-2xl shadow-slate-950/15"
      >
        <header className="flex items-start justify-between border-b border-slate-200 px-6 py-5">
          <div>
            <p className="text-[10px] font-bold uppercase tracking-[0.15em] text-blue-700">
              Bilgi Kütüphanesi
            </p>
            <h2 id="upload-title" className="mt-1 text-lg font-semibold tracking-[-0.02em] text-slate-950">
              PDF dokümanı ekle
            </h2>
            <p className="mt-1 text-xs leading-5 text-slate-500">
              Metin çıkarılır, parçalara ayrılır ve yerel olarak indekslenir.
            </p>
          </div>
          <button
            ref={closeRef}
            type="button"
            onClick={onClose}
            disabled={busy}
            className="focus-ring grid size-9 place-items-center rounded-xl text-slate-500 hover:bg-slate-100 hover:text-slate-950 disabled:opacity-40"
            aria-label="Pencereyi kapat"
          >
            <X className="size-5" />
          </button>
        </header>

        <div className="p-6">
          {!busy && status !== "completed" && (
            <div
              onDragEnter={(event) => {
                event.preventDefault();
                setDragging(true);
              }}
              onDragOver={(event) => event.preventDefault()}
              onDragLeave={() => setDragging(false)}
              onDrop={(event) => {
                event.preventDefault();
                setDragging(false);
                chooseFile(event.dataTransfer.files[0]);
              }}
              className={`rounded-2xl border border-dashed px-6 py-8 text-center transition ${
                dragging
                  ? "border-blue-400 bg-blue-50"
                  : "border-slate-300 bg-slate-50/70"
              }`}
            >
              <span className="mx-auto grid size-12 place-items-center rounded-2xl border border-blue-100 bg-blue-50 text-blue-700">
                <UploadCloud className="size-5" aria-hidden="true" />
              </span>
              <p className="mt-4 text-sm font-semibold text-slate-800">
                PDF'yi buraya sürükleyip bırakın
              </p>
              <p className="mt-1 text-xs text-slate-500">veya bilgisayarınızdan seçin • en fazla 20 MB</p>
              <input
                ref={inputRef}
                type="file"
                accept="application/pdf,.pdf"
                className="sr-only"
                onChange={(event) => chooseFile(event.target.files?.[0])}
              />
              <button
                type="button"
                onClick={() => inputRef.current?.click()}
                className="focus-ring mt-5 min-h-10 rounded-xl border border-slate-300 bg-white px-4 text-xs font-semibold text-slate-700 shadow-sm transition hover:border-blue-300 hover:text-blue-700"
              >
                Dosya Seç
              </button>
            </div>
          )}

          {file && !busy && status !== "completed" && (
            <div className="mt-4 flex items-center gap-3 rounded-xl border border-slate-200 bg-slate-50 p-3">
              <span className="grid size-9 shrink-0 place-items-center rounded-lg bg-red-50 text-red-600">
                <FileUp className="size-4" aria-hidden="true" />
              </span>
              <div className="min-w-0 flex-1">
                <p className="truncate text-xs font-semibold text-slate-800">{file.name}</p>
                <p className="mt-0.5 text-[10px] text-slate-500">
                  {(file.size / 1024 / 1024).toFixed(2)} MB
                </p>
              </div>
              <button
                type="button"
                onClick={() => setFile(null)}
                className="focus-ring grid size-8 place-items-center rounded-lg text-slate-500 hover:bg-slate-200 hover:text-slate-950"
                aria-label="Seçili dosyayı kaldır"
              >
                <X className="size-4" />
              </button>
            </div>
          )}

          {status && status !== "error" && (
            <div className="py-3" aria-live="polite">
              <div className="mb-5 flex items-center gap-3">
                {status === "completed" ? (
                  <span className="grid size-10 place-items-center rounded-full bg-emerald-50 text-emerald-700">
                    <Check className="size-5" />
                  </span>
                ) : (
                  <span className="grid size-10 place-items-center rounded-full bg-blue-50 text-blue-700">
                    <LoaderCircle className="size-5 animate-spin" />
                  </span>
                )}
                <div>
                  <p className="text-sm font-semibold text-slate-800">{stageLabels[status]}</p>
                  <p className="mt-0.5 text-xs text-slate-500">{message}</p>
                </div>
              </div>
              {status === "uploading" && (
                <div className="mb-5 h-1 overflow-hidden rounded-full bg-slate-100">
                  <div
                    className="h-full rounded-full bg-blue-600 transition-[width]"
                    style={{ width: `${progress}%` }}
                  />
                </div>
              )}
              <ol className="grid grid-cols-6 gap-1" aria-label="Belge işleme adımları">
                {stageOrder.map((stage, index) => (
                  <li key={stage} className="min-w-0 text-center">
                    <span className={`mx-auto block h-1 rounded-full transition-colors ${
                      index <= currentIndex ? "bg-blue-600" : "bg-slate-200"
                    }`} />
                    <span className="mt-2 hidden truncate text-[9px] text-slate-500 sm:block">
                      {stageLabels[stage]}
                    </span>
                  </li>
                ))}
              </ol>
            </div>
          )}

          {status === "error" && (
            <div className="mt-4 flex gap-3 rounded-xl border border-amber-200 bg-amber-50 p-4" role="alert">
              <XCircle className="mt-0.5 size-4 shrink-0 text-amber-600" aria-hidden="true" />
              <div>
                <p className="text-xs font-semibold text-amber-950">Belge eklenemedi</p>
                <p className="mt-1 text-xs leading-5 text-amber-800">{message}</p>
              </div>
            </div>
          )}
        </div>

        <footer className="flex items-center justify-end gap-2 border-t border-slate-200 bg-slate-50/50 px-6 py-4">
          <button
            type="button"
            onClick={onClose}
            disabled={busy}
            className="focus-ring min-h-10 rounded-xl px-4 text-xs font-semibold text-slate-600 hover:bg-slate-100 hover:text-slate-950 disabled:opacity-40"
          >
            {status === "completed" ? "Kapat" : "Vazgeç"}
          </button>
          {status !== "completed" && (
            <button
              type="button"
              onClick={startUpload}
              disabled={!file || busy}
              className="focus-ring min-h-10 rounded-xl bg-blue-700 px-5 text-xs font-semibold text-white transition hover:bg-blue-800 disabled:cursor-not-allowed disabled:bg-slate-200 disabled:text-slate-400"
            >
              {busy ? "İşleniyor…" : "Yükle ve İndeksle"}
            </button>
          )}
        </footer>
      </section>
    </div>
  );
}
