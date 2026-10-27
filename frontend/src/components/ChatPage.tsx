import { useCallback, useEffect, useRef, useState } from "react";
import * as api from "../api";
import type { Lang } from "../api";
import { t } from "../i18n";
import ChatMessage, { type Msg } from "./ChatMessage";
import { IconSparkle } from "./Icons";
import MessageComposer from "./MessageComposer";
import NovissiLogo from "./NovissiLogo";

type Props = {
  lang: Lang;
  convId: string | null;
  onConvId: (id: string) => void;
  onChanged: () => void;
  onTranscriptChange?: (transcript: string, busy: boolean) => void;
};

export default function ChatPage({ lang, convId, onConvId, onChanged, onTranscriptChange }: Props) {
  const [msgs, setMsgs] = useState<Msg[]>([]);
  const [busy, setBusy] = useState(false);
  const [loading, setLoading] = useState(false);
  const [draft, setDraft] = useState("");
  const abort = useRef<AbortController | null>(null);
  const skipLoad = useRef<string | null>(null);
  const end = useRef<HTMLDivElement>(null);
  const clearDraft = useCallback(() => setDraft(""), []);
  const ui = t(lang);

  useEffect(() => {
    if (!convId) { setMsgs([]); return; }
    if (skipLoad.current === convId) { skipLoad.current = null; return; }
    let alive = true;
    setLoading(true);
    api.conversationMessages(convId)
      .then((r) => alive && setMsgs(r.map((m) => ({ role: m.role, text: m.text, sources: m.sources, notice: m.notice, mode: m.mode }))))
      .catch((e: Error) => alive && setMsgs([{ role: "a", text: e.message, error: true }]))
      .finally(() => alive && setLoading(false));
    return () => { alive = false; };
  }, [convId]);

  useEffect(() => { end.current?.scrollIntoView({ behavior: "smooth" }); }, [msgs, busy]);

  useEffect(() => {
    const transcript = msgs.map((m) => `${m.role === "u" ? "Vous" : "Novissi-Droit IA"} :\n${m.text}`).join("\n\n");
    onTranscriptChange?.(transcript, busy);
  }, [msgs, busy, onTranscriptChange]);

  async function send(text: string): Promise<boolean> {
    if (busy) return false;
    let id = convId;
    try {
      if (!id) { id = (await api.createConversation()).id; skipLoad.current = id; onConvId(id); }
    } catch (e) { setMsgs((m) => [...m, { role: "a", text: (e as Error).message, error: true }]); return false; }
    setMsgs((m) => [...m, { role: "u", text }]);
    setBusy(true);
    const ctl = new AbortController(); abort.current = ctl;
    try {
      const r = await api.sendMessage(id, text, lang, ctl.signal);
      setMsgs((m) => [...m, { role: "a", text: r.answer, sources: r.citations, notice: r.notice, mode: r.mode }]);
    } catch (e) {
      if ((e as Error).name !== "AbortError") setMsgs((m) => [...m, { role: "a", text: (e as Error).message, error: true }]);
      else setMsgs((m) => [...m, { role: "a", text: "Génération interrompue.", error: true }]);
    } finally { setBusy(false); abort.current = null; onChanged(); }
    return true;
  }

  return (
    <div className="chat">
      <div className="scroll" aria-live="polite">
        {!msgs.length && !loading ? (
          <div className="hero">
            <div className="hero-logo-wrap">
              <NovissiLogo size={64} animated />
            </div>
            <p className="gemini-greeting">{ui.greeting}</p>
            <h2>{ui.heroTitle}</h2>
            <div className="suggest">
              {ui.suggestions.map((s) => (
                <button key={s} type="button" className="card" onClick={() => setDraft(s)}>
                  <span className="card-text">{s}</span>
                  <span className="card-icon" aria-hidden><IconSparkle size={16} /></span>
                </button>
              ))}
            </div>
            {lang !== "Français" && <p className="muted">{ui.langWarning}</p>}
          </div>
        ) : (
          <div className="thread">
            {loading && <p className="muted">Chargement…</p>}
            {msgs.map((m, i) => <ChatMessage key={i} m={m} lang={lang} />)}
            {busy && (
              <div className="turn a">
                <div className="avatar gemini-avatar" aria-hidden><NovissiLogo size={26} animated /></div>
                <div className="body muted">{ui.searchingLaws}</div>
              </div>
            )}
            <div ref={end} />
          </div>
        )}
      </div>
      <MessageComposer lang={lang} busy={busy} onSend={send} onStop={() => abort.current?.abort()} draft={draft} onDraftUsed={clearDraft} />
    </div>
  );
}
