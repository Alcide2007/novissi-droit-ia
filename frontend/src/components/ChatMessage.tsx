import { useEffect, useState } from "react";
import type { Lang, Source } from "../api";
import { t } from "../i18n";
import CitationList from "./CitationList";
import { IconCopy, IconSparkle, IconStop, IconVolume } from "./Icons";
import Markdown from "./Markdown";
import NovissiLogo from "./NovissiLogo";

export type Msg = { role: "u" | "a"; text: string; sources?: Source[]; notice?: string | null; mode?: string | null; error?: boolean };

function cleanForSpeech(raw: string): string {
  return raw
    .replace(/\[\d+\]/g, "")
    .replace(/[#*_`~>-]/g, " ")
    .replace(/\[([^\]]+)\]\([^)]+\)/g, "$1")
    .replace(/\s+/g, " ")
    .trim();
}

export default function ChatMessage({ m, lang = "Français" }: { m: Msg; lang?: Lang }) {
  const [speaking, setSpeaking] = useState(false);
  const ui = t(lang);

  useEffect(() => {
    return () => {
      if (typeof window !== "undefined" && "speechSynthesis" in window) {
        window.speechSynthesis.cancel();
      }
    };
  }, []);

  function toggleSpeech() {
    if (typeof window === "undefined") return;
    if (!("speechSynthesis" in window)) {
      alert("La lecture vocale n'est pas disponible sur ce navigateur.");
      return;
    }
    if (speaking) {
      window.speechSynthesis.cancel();
      setSpeaking(false);
      return;
    }
    window.speechSynthesis.cancel();
    const u = new SpeechSynthesisUtterance(cleanForSpeech(m.text));
    u.lang = "fr-FR";
    u.rate = 0.95;
    const voices = window.speechSynthesis.getVoices?.() ?? [];
    const frVoice = voices.find((v) => v.lang?.toLowerCase().startsWith("fr"));
    if (frVoice) u.voice = frVoice;
    u.onend = () => setSpeaking(false);
    u.onerror = () => setSpeaking(false);
    setSpeaking(true);
    window.speechSynthesis.speak(u);
  }

  if (m.role === "u") return <div className="turn u"><div className="bubble">{m.text}</div></div>;
  return (
    <div className="turn a">
      <div className="avatar gemini-avatar" aria-hidden>
        <NovissiLogo size={28} />
      </div>
      <div className="body">
        {m.error ? <p className="err" role="alert">{m.text}</p> : <Markdown text={m.text} />}
        {m.notice && <p className="notice">{m.notice}</p>}
        {m.mode === "ia" && (
          <p className="muted" style={{ display: "inline-flex", alignItems: "center", gap: "6px" }}>
            <IconSparkle size={14} />
            <span>{ui.aiDraftedNote}</span>
          </p>
        )}
        {m.mode === "extraits" && <p className="notice">{ui.degradedNote}</p>}
        {m.sources?.some((x) => x.demo) && <p className="notice" role="note">{ui.demoNote}</p>}
        <CitationList sources={m.sources ?? []} lang={lang} />
        {!m.error && (
          <div className="row action-bar">
            <button
              type="button"
              className={"chip tts-btn" + (speaking ? " active-tts" : "")}
              onClick={toggleSpeech}
              aria-label={speaking ? ui.stopListening : ui.listenResponse}
              title={speaking ? ui.stopListening : ui.listenResponse}
            >
              {speaking ? <IconStop size={15} /> : <IconVolume size={15} />}
              <span>{speaking ? ui.stopListening : ui.listenResponse}</span>
            </button>
            <button type="button" className="chip" onClick={() => navigator.clipboard?.writeText(m.text)}>
              <IconCopy size={15} />
              <span>{ui.copyResponse}</span>
            </button>
          </div>
        )}
      </div>
    </div>
  );
}