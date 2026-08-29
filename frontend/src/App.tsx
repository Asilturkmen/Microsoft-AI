import { Menu, RotateCcw, TriangleAlert } from "./icons";
import { useCallback, useEffect, useRef, useState } from "react";
import { askQuestion, getDocuments, getHealth } from "./api";
import { ChatComposer } from "./components/ChatComposer";
import { DocumentViewer } from "./components/DocumentViewer";
import { EmptyState } from "./components/EmptyState";
import { KnowledgeSidebar } from "./components/KnowledgeSidebar";
import { AssistantThinking, MessageList } from "./components/MessageList";
import { RuntimeBadge } from "./components/RuntimeBadge";
import { UploadDialog } from "./components/UploadDialog";
import type { ChatMessage, HealthStatus, KnowledgeDocument } from "./types";

function makeId() {
  return crypto.randomUUID();
}

export default function App() {
  const [documents, setDocuments] = useState<KnowledgeDocument[]>([]);
  const [documentsLoading, setDocumentsLoading] = useState(true);
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [healthLoading, setHealthLoading] = useState(true);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [question, setQuestion] = useState("");
  const [sending, setSending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [uploadOpen, setUploadOpen] = useState(false);
  const [selectedDocument, setSelectedDocument] = useState<KnowledgeDocument | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  const refreshDocuments = useCallback(async () => {
    try {
      setDocuments(await getDocuments());
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Belgeler yüklenemedi.");
    } finally {
      setDocumentsLoading(false);
    }
  }, []);

  const refreshHealth = useCallback(async () => {
    try {
      setHealth(await getHealth());
    } catch {
      setHealth(null);
    } finally {
      setHealthLoading(false);
    }
  }, []);

  useEffect(() => {
    void refreshDocuments();
    void refreshHealth();
    const timer = window.setInterval(refreshHealth, 15_000);
    return () => window.clearInterval(timer);
  }, [refreshDocuments, refreshHealth]);

  useEffect(() => {
    const frame = requestAnimationFrame(() => {
      scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
    });
    return () => cancelAnimationFrame(frame);
  }, [messages, sending]);

  const send = async (suggestion?: string) => {
    const text = (suggestion ?? question).trim();
    if (!text || sending) return;
    setQuestion("");
    setError(null);
    setSending(true);
    setMessages((current) => [
      ...current,
      { id: makeId(), role: "user", content: text },
    ]);
    try {
      const response = await askQuestion(text);
      setMessages((current) => [
        ...current,
        {
          id: makeId(),
          role: "assistant",
          content: response.answer,
          sources: response.sources,
          usedFallback: response.used_fallback,
        },
      ]);
      void refreshHealth();
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : "Yerel asistan yanıt veremedi.",
      );
    } finally {
      setSending(false);
    }
  };

  const newConversation = () => {
    setMessages([]);
    setQuestion("");
    setError(null);
  };

  return (
    <div className="flex h-dvh overflow-hidden bg-[#f8faf9] text-slate-900">
      <KnowledgeSidebar
        documents={documents}
        loading={documentsLoading}
        open={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
        onUpload={() => {
          setSidebarOpen(false);
          setUploadOpen(true);
        }}
        onSelect={(document) => {
          setSidebarOpen(false);
          setSelectedDocument(document);
        }}
      />

      <main className="relative flex min-w-0 flex-1 flex-col">
        <header className="z-20 flex h-[76px] shrink-0 items-center justify-between border-b border-slate-200/80 bg-white/90 px-3 backdrop-blur-xl sm:px-7">
          <div className="flex min-w-0 items-center gap-2 sm:gap-3">
            <button
              type="button"
              onClick={() => setSidebarOpen(true)}
              className="focus-ring grid size-10 place-items-center rounded-xl text-slate-500 hover:bg-slate-100 hover:text-slate-950 lg:hidden"
              aria-label="Bilgi Kütüphanesi panelini aç"
            >
              <Menu className="size-5" />
            </button>
            <div className="min-w-0">
              <div className="flex items-center gap-2">
                <h1 className="truncate text-sm font-bold tracking-[-0.01em] text-slate-950">
                  Yerel Bilgi Asistanı
                </h1>
                <span className="hidden rounded-md border border-blue-100 bg-blue-50 px-1.5 py-0.5 text-[8px] font-bold uppercase tracking-[0.14em] text-blue-700 sm:inline">
                  Local RAG
                </span>
              </div>
              <p className="mt-0.5 hidden text-[11px] text-slate-500 sm:block">
                Belgelerinize dayalı, güvenilir ve yerel yanıtlar
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {messages.length > 0 && (
              <button
                type="button"
                onClick={newConversation}
                disabled={sending}
                className="focus-ring grid size-9 place-items-center rounded-xl text-slate-500 hover:bg-slate-100 hover:text-slate-950 disabled:opacity-40"
                aria-label="Yeni konuşma"
                title="Yeni konuşma"
              >
                <RotateCcw className="size-4" />
              </button>
            )}
            <RuntimeBadge health={health} loading={healthLoading} />
          </div>
        </header>

        <div ref={scrollRef} className="chat-scroll min-h-0 flex-1 overflow-y-auto">
          <div className="mx-auto flex min-h-full w-full max-w-[1040px] flex-col px-4 sm:px-8">
            {messages.length === 0 ? (
              <EmptyState onSelect={(prompt) => void send(prompt)} />
            ) : (
              <MessageList messages={messages} />
            )}
            {sending && <AssistantThinking />}
            {error && (
              <div className="animate-enter mx-auto mb-5 flex w-full max-w-[840px] items-start gap-3 rounded-2xl border border-amber-200 bg-amber-50 px-4 py-3" role="alert">
                <TriangleAlert className="mt-0.5 size-4 shrink-0 text-amber-600" aria-hidden="true" />
                <div className="min-w-0 flex-1">
                  <p className="text-xs font-semibold text-amber-950">İstek tamamlanamadı</p>
                  <p className="mt-1 break-words text-xs leading-5 text-amber-800">{error}</p>
                </div>
                <button
                  type="button"
                  onClick={() => setError(null)}
                  className="focus-ring text-[11px] font-semibold text-amber-700 hover:text-amber-950"
                >
                  Kapat
                </button>
              </div>
            )}
          </div>
        </div>

        <div className="pointer-events-none absolute inset-x-0 bottom-0 h-28 bg-gradient-to-t from-[#f8faf9] via-[#f8faf9]/90 to-transparent" aria-hidden="true" />
        <div className="relative z-10 shrink-0 bg-[#f8faf9]/88 pt-2 backdrop-blur-md">
          <ChatComposer
            value={question}
            disabled={sending || health?.status === "error"}
            onChange={setQuestion}
            onSubmit={() => void send()}
            onUpload={() => setUploadOpen(true)}
          />
        </div>
      </main>

      <UploadDialog
        open={uploadOpen}
        onClose={() => setUploadOpen(false)}
        onComplete={() => {
          void refreshDocuments();
          void refreshHealth();
        }}
      />

      <DocumentViewer
        document={selectedDocument}
        onClose={() => setSelectedDocument(null)}
        onDeleted={() => {
          void refreshDocuments();
          void refreshHealth();
        }}
      />

      <div className="sr-only" aria-live="polite">
        {sending ? "Belgelerde aranıyor" : ""}
        {health?.local ? "Yerel AI bağlantısı etkin" : ""}
      </div>
    </div>
  );
}
