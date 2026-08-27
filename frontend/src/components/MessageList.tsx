import { Bot, ChevronDown, FileText } from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import type { ChatMessage } from "../types";

function AssistantContent({ content }: { content: string }) {
  return <div className="markdown-body"><ReactMarkdown remarkPlugins={[remarkGfm]}>{content}</ReactMarkdown></div>;
}

function SourceList({ message }: { message: ChatMessage }) {
  if (!message.sources?.length) return null;
  return (
    <details className="source-details mt-5 border-t border-slate-200 pt-3">
      <summary className="focus-ring -ml-1 flex w-fit cursor-pointer list-none items-center gap-2 rounded-md px-1 py-1 text-[11px] font-bold uppercase tracking-[0.1em] text-slate-500 hover:text-blue-700">
        <FileText className="size-3.5" aria-hidden="true" /> {message.sources.length} kaynak parçası
        <ChevronDown className="chevron size-3.5 transition-transform" aria-hidden="true" />
      </summary>
      <ul className="mt-2 flex flex-wrap gap-2">
        {message.sources.map((source, index) => (
          <li key={`${source.filename}-${source.chunk_index}-${index}`} className="inline-flex max-w-full items-center gap-2 rounded-lg border border-blue-100 bg-blue-50/70 px-2.5 py-1.5 text-[11px] text-slate-500">
            <span className="max-w-[230px] truncate font-semibold text-blue-800" title={source.filename}>{source.filename}</span>
            <span className="text-slate-400">Parça {source.chunk_index + 1}</span>
          </li>
        ))}
      </ul>
    </details>
  );
}

export function MessageList({ messages }: { messages: ChatMessage[] }) {
  return (
    <div className="mx-auto w-full max-w-[840px] space-y-7 py-8 sm:py-12" aria-live="polite">
      {messages.map((message) => message.role === "user" ? (
        <article key={message.id} className="animate-enter flex justify-end pl-8 sm:pl-20">
          <div className="max-w-[86%] rounded-2xl rounded-br-md bg-[#123b5d] px-4 py-3 text-sm leading-6 text-white shadow-sm"><p className="whitespace-pre-wrap">{message.content}</p></div>
        </article>
      ) : (
        <article key={message.id} className="animate-enter flex gap-3 rounded-3xl border border-slate-200 bg-white p-4 shadow-sm shadow-slate-200/40 sm:gap-4 sm:p-5">
          <span className="mt-0.5 grid size-9 shrink-0 place-items-center rounded-xl bg-blue-50 text-blue-700"><Bot className="size-[18px]" aria-hidden="true" /></span>
          <div className="min-w-0 flex-1 pt-0.5">
            <div className="mb-2 flex items-center gap-2">
              <span className="text-xs font-bold text-slate-800">Yerel RAG</span>
              {message.usedFallback && <span className="rounded-full border border-slate-200 bg-slate-50 px-2 py-0.5 text-[9px] font-bold uppercase tracking-[0.1em] text-slate-500">Belgelerde bulunamadı</span>}
            </div>
            <AssistantContent content={message.content} />
            <SourceList message={message} />
          </div>
        </article>
      ))}
    </div>
  );
}

export function AssistantThinking() {
  return (
    <div className="animate-enter mx-auto flex w-full max-w-[840px] gap-4 rounded-3xl border border-slate-200 bg-white p-5 shadow-sm" role="status">
      <span className="grid size-9 shrink-0 place-items-center rounded-xl bg-blue-50 text-blue-700"><Bot className="size-[18px]" /></span>
      <div className="pt-1"><p className="text-xs font-semibold text-slate-700">Belgelerde aranıyor…</p><div className="mt-3 flex gap-1.5" aria-hidden="true"><span className="thinking-dot" /><span className="thinking-dot" /><span className="thinking-dot" /></div></div>
    </div>
  );
}
