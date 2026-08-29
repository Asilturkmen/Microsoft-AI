import {
  BookOpenText,
  CheckCircle2,
  ChevronRight,
  FileText,
  HardDrive,
  LoaderCircle,
  Plus,
  X,
} from "../icons";
import type { KnowledgeDocument } from "../types";

interface KnowledgeSidebarProps {
  documents: KnowledgeDocument[];
  loading: boolean;
  open: boolean;
  onClose: () => void;
  onUpload: () => void;
  onSelect: (document: KnowledgeDocument) => void;
}

function DocumentRow({
  document,
  onSelect,
}: {
  document: KnowledgeDocument;
  onSelect: () => void;
}) {
  const ready = document.status === "ready";
  return (
    <li>
      <button
        type="button"
        onClick={onSelect}
        className="focus-ring group flex w-full items-start gap-3 rounded-2xl border border-transparent px-3 py-3 text-left transition duration-150 hover:border-slate-200 hover:bg-white hover:shadow-sm"
        aria-label={`${document.title} belgesini aç`}
      >
        <span className="mt-0.5 grid size-10 shrink-0 place-items-center rounded-xl border border-slate-200 bg-white text-blue-700 shadow-sm shadow-slate-200/50">
          <FileText className="size-[18px]" aria-hidden="true" />
        </span>
        <span className="min-w-0 flex-1">
          <span className="block truncate text-[13px] font-semibold text-slate-800" title={document.title}>
            {document.title}
          </span>
          <span className="mt-0.5 block truncate text-[11px] text-slate-500" title={document.filename}>
            {document.filename}
          </span>
          <span className="mt-2 flex items-center gap-1.5 text-[10px] font-medium text-slate-500">
            <span className="rounded-md bg-slate-100 px-1.5 py-0.5 font-semibold text-slate-600">{document.file_type}</span>
            <span>{document.chunk_count} parça</span>
            <span className="ml-auto inline-flex items-center gap-1 text-emerald-700">
              {ready ? <CheckCircle2 className="size-3" /> : <LoaderCircle className="size-3 animate-spin" />}
              {ready ? "Hazır" : "İşleniyor"}
            </span>
          </span>
        </span>
        <ChevronRight className="mt-3 size-4 shrink-0 text-slate-300 transition group-hover:translate-x-0.5 group-hover:text-blue-600" />
      </button>
    </li>
  );
}

function SidebarContent({
  documents,
  loading,
  onClose,
  onUpload,
  onSelect,
}: Omit<KnowledgeSidebarProps, "open">) {
  const chunkCount = documents.reduce((sum, document) => sum + document.chunk_count, 0);
  return (
    <div className="flex h-full flex-col">
      <div className="flex h-[76px] items-center justify-between border-b border-slate-200/80 px-5">
        <div className="flex items-center gap-3">
          <span className="grid size-10 place-items-center rounded-2xl bg-[#123b5d] text-white shadow-sm">
            <BookOpenText className="size-[19px]" aria-hidden="true" />
          </span>
          <div>
            <p className="text-sm font-bold tracking-[-0.015em] text-slate-950">Bilgi Kütüphanesi</p>
            <p className="mt-0.5 text-[11px] text-slate-500">Yerel belge koleksiyonu</p>
          </div>
        </div>
        <button type="button" onClick={onClose} className="focus-ring grid size-10 place-items-center rounded-xl text-slate-500 hover:bg-slate-100 hover:text-slate-900 lg:hidden" aria-label="Bilgi Kütüphanesi panelini kapat">
          <X className="size-5" />
        </button>
      </div>

      <div className="px-4 pt-5">
        <button type="button" onClick={onUpload} className="focus-ring flex min-h-11 w-full items-center justify-center gap-2 rounded-xl bg-blue-700 px-4 text-sm font-semibold text-white shadow-sm shadow-blue-900/10 transition hover:bg-blue-800 active:scale-[0.99]">
          <Plus className="size-4" aria-hidden="true" /> Doküman Ekle
        </button>
        <div className="mt-6 flex items-center justify-between px-1">
          <span className="text-[10px] font-bold uppercase tracking-[0.14em] text-slate-500">Belgeler</span>
          {!loading && <span className="rounded-full border border-slate-200 bg-white px-2 py-0.5 text-[10px] font-semibold tabular-nums text-slate-600">{documents.length}</span>}
        </div>
        {!loading && documents.length > 0 && (
          <p className="mt-2 px-1 text-[11px] leading-4 text-slate-400">İçeriğini görüntülemek için bir belge seç.</p>
        )}
      </div>

      <nav className="sidebar-scroll mt-2 min-h-0 flex-1 overflow-y-auto px-2" aria-label="Belgeler">
        {loading ? (
          <div className="space-y-2 px-2 py-2" aria-label="Belgeler yükleniyor">
            {[0, 1, 2, 3].map((item) => <div key={item} className="h-[82px] animate-pulse rounded-2xl bg-slate-200/60" />)}
          </div>
        ) : documents.length ? (
          <ul className="space-y-1 py-1">
            {documents.map((document) => (
              <DocumentRow key={document.filename} document={document} onSelect={() => onSelect(document)} />
            ))}
          </ul>
        ) : (
          <div className="mx-2 mt-4 rounded-2xl border border-dashed border-slate-300 bg-white/60 px-4 py-7 text-center">
            <FileText className="mx-auto size-6 text-slate-400" aria-hidden="true" />
            <p className="mt-3 text-xs font-medium text-slate-600">Henüz indekslenmiş belge yok.</p>
            <p className="mt-1 text-[11px] text-slate-400">İlk PDF belgeni ekleyerek başla.</p>
          </div>
        )}
      </nav>

      <div className="border-t border-slate-200/80 p-4">
        <div className="flex items-center gap-3 rounded-2xl border border-slate-200 bg-white px-3 py-3 shadow-sm shadow-slate-200/30">
          <span className="grid size-8 place-items-center rounded-lg bg-emerald-50 text-emerald-700"><HardDrive className="size-4" /></span>
          <div className="min-w-0">
            <p className="text-[11px] font-semibold text-slate-700">Cihazınızda güvenle saklanır</p>
            <p className="mt-0.5 text-[10px] text-slate-500">{documents.length} belge • {chunkCount} parça</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export function KnowledgeSidebar(props: KnowledgeSidebarProps) {
  return (
    <>
      <aside className="hidden h-dvh w-[332px] shrink-0 border-r border-slate-200 bg-[#f3f5f4] lg:block">
        <SidebarContent {...props} />
      </aside>
      <div className={`fixed inset-0 z-40 bg-slate-950/25 backdrop-blur-[2px] transition-opacity lg:hidden ${props.open ? "pointer-events-auto opacity-100" : "pointer-events-none opacity-0"}`} onClick={props.onClose} aria-hidden="true" />
      <aside className={`fixed inset-y-0 left-0 z-50 w-[min(90vw,340px)] border-r border-slate-200 bg-[#f3f5f4] shadow-2xl transition-transform duration-200 lg:hidden ${props.open ? "translate-x-0" : "-translate-x-full"}`} aria-label="Bilgi Kütüphanesi" aria-hidden={!props.open} inert={!props.open}>
        <SidebarContent {...props} />
      </aside>
    </>
  );
}
