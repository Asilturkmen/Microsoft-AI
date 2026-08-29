import {
  AlertTriangle,
  BookOpen,
  CheckCircle2,
  FileText,
  LoaderCircle,
  Trash2,
  X,
} from "../icons";
import { useEffect, useRef, useState } from "react";
import { deleteDocument, getDocument } from "../api";
import type { DocumentDetail, KnowledgeDocument } from "../types";

interface DocumentViewerProps {
  document: KnowledgeDocument | null;
  onClose: () => void;
  onDeleted: (filename: string) => void;
}

export function DocumentViewer({ document, onClose, onDeleted }: DocumentViewerProps) {
  const [detail, setDetail] = useState<DocumentDetail | null>(null);
  const [loading, setLoading] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [confirming, setConfirming] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const closeRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    if (!document) return;
    let active = true;
    setDetail(null);
    setError(null);
    setConfirming(false);
    setLoading(true);
    void getDocument(document.filename)
      .then((result) => {
        if (active) setDetail(result);
      })
      .catch((requestError: unknown) => {
        if (active) {
          setError(requestError instanceof Error ? requestError.message : "Belge açılamadı.");
        }
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    window.setTimeout(() => closeRef.current?.focus(), 0);
    return () => {
      active = false;
    };
  }, [document]);

  useEffect(() => {
    if (!document) return;
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape" && !deleting) onClose();
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [deleting, document, onClose]);

  if (!document) return null;

  const remove = async () => {
    setDeleting(true);
    setError(null);
    try {
      await deleteDocument(document.filename);
      onDeleted(document.filename);
      onClose();
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Belge silinemedi.");
      setConfirming(false);
    } finally {
      setDeleting(false);
    }
  };

  return (
    <div
      className="fixed inset-0 z-[65] flex justify-end bg-slate-950/20 backdrop-blur-[2px]"
      onMouseDown={(event) => {
        if (event.target === event.currentTarget && !deleting) onClose();
      }}
    >
      <section
        role="dialog"
        aria-modal="true"
        aria-labelledby="document-title"
        className="animate-panel flex h-full w-full max-w-[680px] flex-col border-l border-slate-200 bg-white shadow-[-24px_0_70px_rgba(15,23,42,0.12)]"
      >
        <header className="flex shrink-0 items-start gap-4 border-b border-slate-200/80 px-5 py-5 sm:px-7">
          <span className="grid size-11 shrink-0 place-items-center rounded-2xl bg-blue-50 text-blue-700">
            <FileText className="size-5" aria-hidden="true" />
          </span>
          <div className="min-w-0 flex-1">
            <div className="flex items-center gap-2 text-[11px] font-semibold uppercase tracking-[0.12em] text-blue-700">
              <BookOpen className="size-3.5" aria-hidden="true" />
              Belge önizleme
            </div>
            <h2 id="document-title" className="mt-1 truncate text-lg font-semibold tracking-[-0.025em] text-slate-950">
              {document.title}
            </h2>
            <p className="mt-1 truncate text-xs text-slate-500">{document.filename}</p>
          </div>
          <button
            ref={closeRef}
            type="button"
            onClick={onClose}
            disabled={deleting}
            className="focus-ring grid size-10 shrink-0 place-items-center rounded-xl text-slate-500 transition hover:bg-slate-100 hover:text-slate-900 disabled:opacity-40"
            aria-label="Belge önizlemesini kapat"
          >
            <X className="size-5" />
          </button>
        </header>

        <div className="flex items-center gap-2 border-b border-slate-100 bg-slate-50/70 px-5 py-3 text-[11px] font-medium text-slate-500 sm:px-7">
          <span className="rounded-md border border-slate-200 bg-white px-2 py-1 font-semibold text-slate-700">
            {document.file_type}
          </span>
          <span>{document.chunk_count} parça</span>
          {detail && <><span className="text-slate-300">•</span><span>{detail.character_count.toLocaleString("tr-TR")} karakter</span></>}
          <span className="ml-auto inline-flex items-center gap-1.5 text-emerald-700">
            <CheckCircle2 className="size-3.5" /> İndekslendi
          </span>
        </div>

        <div className="document-scroll min-h-0 flex-1 overflow-y-auto px-5 py-6 sm:px-8 sm:py-8">
          {loading && (
            <div className="flex h-48 flex-col items-center justify-center text-slate-500" role="status">
              <LoaderCircle className="size-6 animate-spin text-blue-600" />
              <p className="mt-3 text-sm">Belge içeriği hazırlanıyor…</p>
            </div>
          )}
          {error && (
            <div className="flex gap-3 rounded-2xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900" role="alert">
              <AlertTriangle className="mt-0.5 size-4 shrink-0" />
              <p>{error}</p>
            </div>
          )}
          {detail && (
            <article className="whitespace-pre-wrap break-words font-serif text-[15px] leading-7 text-slate-700">
              {detail.content}
            </article>
          )}
        </div>

        <footer className="shrink-0 border-t border-slate-200 bg-white px-5 py-4 sm:px-7">
          {confirming ? (
            <div className="flex flex-col gap-3 rounded-2xl border border-red-200 bg-red-50 p-4 sm:flex-row sm:items-center">
              <div className="min-w-0 flex-1">
                <p className="text-sm font-semibold text-red-950">Bu belgeyi kalıcı olarak silmek istiyor musun?</p>
                <p className="mt-1 text-xs leading-5 text-red-700">Dosya kaldırılacak ve knowledge base yeniden indekslenecek.</p>
              </div>
              <div className="flex shrink-0 gap-2">
                <button type="button" onClick={() => setConfirming(false)} disabled={deleting} className="focus-ring min-h-10 rounded-xl px-3 text-xs font-semibold text-slate-600 hover:bg-white">
                  Vazgeç
                </button>
                <button type="button" onClick={() => void remove()} disabled={deleting} className="focus-ring inline-flex min-h-10 items-center gap-2 rounded-xl bg-red-600 px-4 text-xs font-semibold text-white hover:bg-red-700 disabled:opacity-60">
                  {deleting ? <LoaderCircle className="size-4 animate-spin" /> : <Trash2 className="size-4" />}
                  {deleting ? "Siliniyor…" : "Evet, sil"}
                </button>
              </div>
            </div>
          ) : (
            <div className="flex items-center justify-between gap-3">
              <p className="hidden text-xs text-slate-500 sm:block">İçerik yalnızca bu cihazdaki yerel dosyadan okunur.</p>
              <button type="button" onClick={() => setConfirming(true)} className="focus-ring ml-auto inline-flex min-h-10 items-center gap-2 rounded-xl border border-red-200 px-4 text-xs font-semibold text-red-700 transition hover:bg-red-50">
                <Trash2 className="size-4" /> Belgeyi Sil
              </button>
            </div>
          )}
        </footer>
      </section>
    </div>
  );
}
