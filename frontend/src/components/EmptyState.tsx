import { ArrowRight, Database, Network, Shapes, Sparkles, TestTubeDiagonal } from "../icons";

const prompts = [
  { icon: Database, eyebrow: "Veritabanı", text: "Primary key ile foreign key arasındaki fark nedir?" },
  { icon: Shapes, eyebrow: "Programlama", text: "Polimorfizm nedir?" },
  { icon: Network, eyebrow: "Ağlar", text: "TCP ile UDP arasındaki fark nedir?" },
  { icon: TestTubeDiagonal, eyebrow: "Test", text: "Unit test ile integration test arasındaki fark nedir?" },
];

export function EmptyState({ onSelect }: { onSelect: (prompt: string) => void }) {
  return (
    <div className="animate-enter mx-auto flex w-full max-w-[820px] flex-1 flex-col justify-center px-1 pb-14 pt-10 sm:px-4">
      <div className="mb-9">
        <div className="mb-5 inline-flex items-center gap-2 rounded-full border border-blue-100 bg-blue-50 px-3 py-1.5 text-[11px] font-semibold text-blue-800">
          <Sparkles className="size-3.5" aria-hidden="true" />
          Kaynaklara dayalı yerel yapay zekâ
        </div>
        <h1 className="max-w-3xl text-balance text-[clamp(2.25rem,5vw,4.25rem)] font-semibold leading-[1.02] tracking-[-0.055em] text-[#102a43]">
          Belgelerinizdeki bilgiye, anında ulaşın.
        </h1>
        <p className="mt-5 max-w-2xl text-pretty text-sm leading-6 text-slate-600 sm:text-base sm:leading-7">
          Sorunuzu doğal biçimde yazın. Yerel asistan yalnızca eklediğiniz belgeleri tarar,
          yanıtını kaynaklarıyla birlikte sunar ve verilerinizi cihazınızda tutar.
        </p>
      </div>

      <div>
        <p className="mb-3 text-[10px] font-bold uppercase tracking-[0.15em] text-slate-500">Örnek sorular</p>
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
          {prompts.map(({ icon: Icon, eyebrow, text }) => (
            <button key={text} type="button" onClick={() => onSelect(text)} className="focus-ring group flex min-h-[92px] items-center gap-4 rounded-2xl border border-slate-200 bg-white px-4 py-4 text-left shadow-sm shadow-slate-200/40 transition duration-150 hover:-translate-y-0.5 hover:border-blue-200 hover:shadow-md hover:shadow-blue-900/5">
              <span className="grid size-10 shrink-0 place-items-center rounded-xl bg-slate-100 text-[#123b5d] transition group-hover:bg-blue-50 group-hover:text-blue-700">
                <Icon className="size-[18px]" aria-hidden="true" />
              </span>
              <span className="min-w-0 flex-1">
                <span className="block text-[10px] font-bold uppercase tracking-[0.1em] text-slate-400">{eyebrow}</span>
                <span className="mt-1 block text-[13px] font-semibold leading-5 text-slate-700">{text}</span>
              </span>
              <ArrowRight className="size-4 shrink-0 text-slate-300 transition group-hover:translate-x-0.5 group-hover:text-blue-600" aria-hidden="true" />
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
