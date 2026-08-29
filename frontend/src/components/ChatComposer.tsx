import { ArrowUp, CornerDownLeft, Paperclip } from "../icons";
import { useEffect, useRef } from "react";

interface ChatComposerProps {
  value: string;
  disabled: boolean;
  onChange: (value: string) => void;
  onSubmit: () => void;
  onUpload: () => void;
}

export function ChatComposer({
  value,
  disabled,
  onChange,
  onSubmit,
  onUpload,
}: ChatComposerProps) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    const textarea = textareaRef.current;
    if (!textarea) return;
    textarea.style.height = "0px";
    textarea.style.height = `${Math.min(textarea.scrollHeight, 160)}px`;
  }, [value]);

  return (
    <div className="mx-auto w-full max-w-[860px] px-3 pb-3 sm:px-6 sm:pb-6">
      <form
        className="composer-shell rounded-2xl border border-slate-200 bg-white/95 p-2 backdrop-blur-xl transition focus-within:border-blue-300 focus-within:ring-4 focus-within:ring-blue-100/70"
        onSubmit={(event) => {
          event.preventDefault();
          onSubmit();
        }}
      >
        <textarea
          ref={textareaRef}
          value={value}
          onChange={(event) => onChange(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === "Enter" && !event.shiftKey) {
              event.preventDefault();
              if (!disabled && value.trim()) onSubmit();
            }
          }}
          rows={1}
          maxLength={4000}
          disabled={disabled}
          placeholder="Belgelerin hakkında bir soru sor…"
          className="block max-h-40 min-h-12 w-full resize-none bg-transparent px-3 py-3 text-sm leading-6 text-slate-800 outline-none placeholder:text-slate-400 disabled:cursor-not-allowed"
          aria-label="Soru"
        />
        <div className="flex items-center justify-between px-1 pb-1">
          <div className="flex items-center gap-1">
            <button
              type="button"
              onClick={onUpload}
              className="focus-ring grid size-9 place-items-center rounded-lg text-slate-500 transition hover:bg-slate-100 hover:text-blue-700"
              aria-label="PDF dokümanı ekle"
              title="Doküman ekle"
            >
              <Paperclip className="size-[17px]" />
            </button>
            <span className="hidden items-center gap-1.5 text-[10px] text-slate-400 sm:flex">
              <CornerDownLeft className="size-3" aria-hidden="true" />
              Enter gönderir • Shift+Enter yeni satır
            </span>
          </div>
          <button
            type="submit"
            disabled={disabled || !value.trim()}
            className="focus-ring grid size-9 place-items-center rounded-xl bg-blue-700 text-white transition hover:bg-blue-800 active:scale-95 disabled:cursor-not-allowed disabled:bg-slate-200 disabled:text-slate-400"
            aria-label="Soruyu gönder"
          >
            <ArrowUp className="size-[17px]" />
          </button>
        </div>
      </form>
      <p className="mt-2 text-center text-[10px] leading-4 text-slate-400">
        Yanıtlar yalnızca indekslenmiş belgelere dayanır. Önemli bilgileri kaynaklardan doğrulayın.
      </p>
    </div>
  );
}
