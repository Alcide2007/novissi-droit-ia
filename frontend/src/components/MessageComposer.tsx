import { useEffect, useRef, useState } from "react";
import * as api from "../api";
import { useDictation } from "../hooks/useDictation";
import type { Lang } from "../api";
import { t } from "../i18n";
import { IconMic, IconPlus, IconSend, IconStop } from "./Icons";

type Props = { lang: Lang; busy: boolean; onSend: (t: string) => Promise<boolean>; onStop: () => void; draft?: string; onDraftUsed?: () => void };

export default function MessageComposer({ lang, busy, onSend, onStop, draft, onDraftUsed }: Props) {
  const [q, setQ] = useState("");
  const [ocrBusy, setOcrBusy] = useState(false);
  const [attachmentError, setAttachmentError] = useState("");
  const ta = useRef<HTMLTextAreaElement>(null);
  const fileInput = useRef<HTMLInputElement>(null);
  const dict = useDictation(lang, setQ);
  const ui = t(lang);

  async function attachImage(file?: File) {
    if (!file) return;
    setAttachmentError("");
    setOcrBusy(true);
    try {
      const result = await api.ocr(file);
      if (!result.text.trim()) {
        setAttachmentError("Aucun texte lisible n'a été détecté sur cette image.");
        return;
      }
      const extracted = `\n\n[Texte extrait de l’image « ${file.name} »]\n${result.text}`;
      setQ((previous) => `${previous}${extracted}`.trim());
      if (result.needs_review) setAttachmentError("Le texte extrait peut contenir des erreurs : vérifiez-le avant l'envoi.");
      ta.current?.focus();
    } catch (e) {
      setAttachmentError((e as Error).message || "Impossible de lire cette image.");
    } finally {
      setOcrBusy(false);
      if (fileInput.current) fileInput.current.value = "";
    }
  }

  useEffect(() => { if (draft) { setQ(draft); onDraftUsed?.(); ta.current?.focus(); } }, [draft, onDraftUsed]);
  useEffect(() => {
    const el = ta.current; if (!el) return;
    el.style.height = "auto"; el.style.height = Math.min(el.scrollHeight, 200) + "px";
  }, [q]);

  async function submit(txt: string) {
    if (!txt.trim() || busy) return;
    const started = await onSend(txt);
    if (started) setQ("");
  }

  return (
    <div className="composer-wrap">
      <div className="composer">
        <input ref={fileInput} className="file-input-hidden" type="file" accept="image/*" aria-label="Choisir une image à joindre"
          onChange={(e) => void attachImage(e.target.files?.[0])} />
        <button className="icon attach" type="button" onClick={() => fileInput.current?.click()} disabled={busy || ocrBusy}
          aria-label="Joindre une image" title="Joindre une image ou une photo de document">
          <IconPlus size={18} />
        </button>
        <textarea ref={ta} rows={1} value={q} aria-label="Votre question" placeholder={ui.questionPlaceholder}
          onChange={(e) => setQ(e.target.value)}
          onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey && !e.nativeEvent.isComposing) { e.preventDefault(); void submit(q); } }} />
        <button
          type="button"
          className="icon"
          onClick={() => dict.listening ? dict.stop() : dict.start(q)}
          aria-label={dict.listening ? "Arrêter la dictée" : "Dicter"}
          aria-pressed={dict.listening}
          title={dict.supported ? `Dicter en ${lang}` : "La dictée n’est pas disponible dans ce navigateur"}
        >
          {dict.listening ? <IconStop size={16} /> : <IconMic size={17} />}
        </button>
        {busy
          ? <button type="button" className="icon send" onClick={onStop} aria-label="Arrêter"><IconStop size={15} /></button>
          : <button type="button" className="icon send" onClick={() => void submit(q)} disabled={!q.trim() || ocrBusy} aria-label="Envoyer"><IconSend size={17} /></button>}
      </div>
      {dict.listening && <p className="muted" role="status">Écoute en cours en {lang}…</p>}
      {dict.error && <p className="muted" role="alert">{dict.error}</p>}
      {ocrBusy && <p className="muted" role="status">Lecture du texte de l’image…</p>}
      {attachmentError && <p className="muted" role="alert">{attachmentError}</p>}
      <p className="muted small">{ui.footerDisclaimer}</p>
    </div>
  );
}
