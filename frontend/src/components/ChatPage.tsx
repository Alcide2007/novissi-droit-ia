import { useCallback, useEffect, useRef, useState } from "react";
import * as api from "../api";
import type { Lang, LetterKind } from "../api";
import { t } from "../i18n";
import ChatMessage, { cleanForSpeech, type Msg } from "./ChatMessage";
import { IconMic, IconSparkle, IconStop } from "./Icons";
import MessageComposer from "./MessageComposer";
import NovissiLogo from "./NovissiLogo";

type Props = {
  lang: Lang;
  convId: string | null;
  onConvId: (id: string) => void;
  onChanged: () => void;
  onTranscriptChange?: (transcript: string, busy: boolean) => void;
  onOpenLetter?: (kind: LetterKind) => void;
};

export default function ChatPage({ lang, convId, onConvId, onChanged, onTranscriptChange, onOpenLetter }: Props) {
  const [msgs, setMsgs] = useState<Msg[]>([]);
  const [busy, setBusy] = useState(false);
  const [loading, setLoading] = useState(false);
  const [draft, setDraft] = useState("");
  const [speechToSpeech, setSpeechToSpeech] = useState(false);
  const [stsState, setStsState] = useState<"idle" | "listening" | "thinking" | "speaking">("idle");
  const abort = useRef<AbortController | null>(null);
  const skipLoad = useRef<string | null>(null);
  const end = useRef<HTMLDivElement>(null);
  const stsActiveRef = useRef(false);
  const clearDraft = useCallback(() => setDraft(""), []);
  const ui = t(lang);

  useEffect(() => {
    if (!convId) { setMsgs([]); return; }
    if (skipLoad.current === convId) { skipLoad.current = null; return; }
    let alive = true;
    setLoading(true);
    api.conversationMessages(convId)
      .then((r) => alive && setMsgs(r.map((m) => ({
        role: m.role, text: m.text, sources: m.sources, notice: m.notice, mode: m.mode, suggested_letter: m.suggested_letter,
      }))))
      .catch((e: Error) => alive && setMsgs([{ role: "a", text: e.message, error: true }]))
      .finally(() => alive && setLoading(false));
    return () => { alive = false; };
  }, [convId]);

  useEffect(() => { end.current?.scrollIntoView({ behavior: "smooth" }); }, [msgs, busy]);

  useEffect(() => {
    const transcript = msgs.map((m) => `${m.role === "u" ? "Vous" : "Novissi-Droit IA"} :\n${m.text}`).join("\n\n");
    onTranscriptChange?.(transcript, busy);
  }, [msgs, busy, onTranscriptChange]);

  function speakTextInFrench(text: string, onDone?: () => void) {
    if (typeof window === "undefined" || !("speechSynthesis" in window)) {
      onDone?.();
      return;
    }
    window.speechSynthesis.cancel();
    const u = new SpeechSynthesisUtterance(cleanForSpeech(text));
    u.lang = "fr-FR";
    u.rate = 0.98;
    const voices = window.speechSynthesis.getVoices?.() ?? [];
    const frVoice = voices.find((v) => v.lang?.toLowerCase().startsWith("fr"));
    if (frVoice) u.voice = frVoice;
    setStsState("speaking");
    u.onend = () => { setStsState("idle"); onDone?.(); };
    u.onerror = () => { setStsState("idle"); onDone?.(); };
    window.speechSynthesis.speak(u);
  }

  async function send(text: string, fromVoice = false): Promise<boolean> {
    if (busy) return false;
    let id = convId;
    try {
      if (!id) { id = (await api.createConversation()).id; skipLoad.current = id; onConvId(id); }
    } catch (e) { setMsgs((m) => [...m, { role: "a", text: (e as Error).message, error: true }]); return false; }
    setMsgs((m) => [...m, { role: "u", text }]);
    setBusy(true);
    if (fromVoice) setStsState("thinking");
    const ctl = new AbortController(); abort.current = ctl;
    try {
      const r = await api.sendMessage(id, text, lang, ctl.signal);
      setMsgs((m) => [...m, {
        role: "a", text: r.answer, sources: r.citations, notice: r.notice, mode: r.mode, suggested_letter: r.suggested_letter,
      }]);
      if (fromVoice || stsActiveRef.current) {
        speakTextInFrench(r.answer, () => {
          if (stsActiveRef.current) startVoiceLoop();
        });
      }
    } catch (e) {
      if ((e as Error).name !== "AbortError") setMsgs((m) => [...m, { role: "a", text: (e as Error).message, error: true }]);
      else setMsgs((m) => [...m, { role: "a", text: "Génération interrompue.", error: true }]);
    } finally { setBusy(false); abort.current = null; onChanged(); }
    return true;
  }

  function startVoiceLoop() {
    if (!stsActiveRef.current) return;
    const w = window as unknown as { SpeechRecognition?: any; webkitSpeechRecognition?: any };
    const Rec = w.SpeechRecognition || w.webkitSpeechRecognition;
    if (!Rec) {
      alert("La reconnaissance vocale n'est pas disponible sur ce navigateur.");
      setSpeechToSpeech(false);
      stsActiveRef.current = false;
      return;
    }
    const r = new Rec();
    r.lang = "fr-FR";
    r.interimResults = false;
    r.continuous = false;
    setStsState("listening");
    r.onresult = (e: any) => {
      const spoken = e.results?.[0]?.[0]?.transcript?.trim();
      if (spoken) {
        void send(spoken, true);
      } else if (stsActiveRef.current) {
        setStsState("idle");
      }
    };
    r.onerror = () => { setStsState("idle"); setSpeechToSpeech(false); stsActiveRef.current = false; };
    try { r.start(); } catch { setStsState("idle"); }
  }

  function toggleSpeechToSpeech() {
    if (speechToSpeech) {
      stsActiveRef.current = false;
      setSpeechToSpeech(false);
      setStsState("idle");
      if (typeof window !== "undefined" && "speechSynthesis" in window) window.speechSynthesis.cancel();
    } else {
      stsActiveRef.current = true;
      setSpeechToSpeech(true);
      startVoiceLoop();
    }
  }

  return (
    <div className="chat">
      <div className="chat-toolbar">
        <div className="chat-status">
          <span className="status-dot" />
          <span>Code du travail · Bail d’habitation · Code foncier OTR</span>
        </div>
        <button
          type="button"
          className={"chip" + (speechToSpeech ? " active-tts" : "")}
          onClick={toggleSpeechToSpeech}
          title="Conversation vocale mains-libres en français (Speech-to-Speech)"
        >
          {speechToSpeech ? <IconStop size={15} /> : <IconMic size={15} />}
          <span>
            {speechToSpeech
              ? stsState === "listening"
                ? "Écoute en cours… Parlez"
                : stsState === "thinking"
                ? "Analyse juridique…"
                : stsState === "speaking"
                ? "Lecture vocale…"
                : "Arrêter le mode vocal"
              : ui.voiceModeBtn}
          </span>
        </button>
      </div>

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
            {msgs.map((m, i) => <ChatMessage key={i} m={m} lang={lang} onOpenLetter={onOpenLetter} />)}
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
      <MessageComposer lang={lang} busy={busy} onSend={(txt) => send(txt, false)} onStop={() => abort.current?.abort()} draft={draft} onDraftUsed={clearDraft} />
    </div>
  );
}
