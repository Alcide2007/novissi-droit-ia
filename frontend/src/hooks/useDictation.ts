import { useEffect, useRef, useState } from "react";
import type { Lang } from "../api";

type Ev = { results: ArrayLike<ArrayLike<{ transcript: string }> & { isFinal: boolean }> };
type SR = new () => {
  lang: string; interimResults: boolean; continuous: boolean;
  onresult: ((e: Ev) => void) | null; onerror: ((e: { error: string }) => void) | null; onend: (() => void) | null;
  start: () => void; stop: () => void; abort: () => void;
};
const ERRORS: Record<string, string> = {
  "not-allowed": "Accès au microphone refusé. Autorisez le micro dans les paramètres du site.",
  "service-not-allowed": "La reconnaissance vocale est bloquée par le navigateur ou le système.",
  "no-speech": "Aucune voix détectée. Parlez plus près du microphone puis réessayez.",
  "audio-capture": "Aucun microphone disponible. Vérifiez votre périphérique.",
  "network": "Le service de dictée a rencontré une erreur réseau.",
  "language-not-supported": "Cette langue n'est pas prise en charge par la dictée native de ce navigateur. Vous pouvez saisir le texte manuellement.",
};
const SPEECH_LOCALES: Record<Lang, string> = { "Français": "fr-FR", "Ewé": "ee-TG", "Kabiyè": "kbp-TG" };

/** Dictée Web Speech API. La dictée ne soumet jamais automatiquement le message. */
export function useDictation(lang: Lang, onText: (t: string) => void) {
  const [listening, setListening] = useState(false);
  const [error, setError] = useState("");
  const rec = useRef<InstanceType<SR> | null>(null);
  const baseText = useRef("");
  const wanted = useRef(false);
  const restartTimer = useRef<number | null>(null);
  const recognitionCtor = useRef<SR | undefined>(undefined);
  const w = window as unknown as { SpeechRecognition?: SR; webkitSpeechRecognition?: SR };
  const Rec = w.SpeechRecognition || w.webkitSpeechRecognition;
  recognitionCtor.current = Rec;

  useEffect(() => () => {
    wanted.current = false;
    if (restartTimer.current !== null) window.clearTimeout(restartTimer.current);
    try { rec.current?.abort(); } catch { /* déjà arrêté */ }
  }, []);

  function start(existingText = "") {
    setError("");
    if (!Rec) { setError("La dictée vocale n'est pas disponible dans ce navigateur. Utilisez la saisie manuelle ou essayez un navigateur compatible."); return; }
    if (!window.isSecureContext) { setError("Le microphone nécessite HTTPS ou localhost. Ouvrez l'application avec http://localhost:5173."); return; }
    if (rec.current) { setError("Une dictée est déjà en cours."); return; }
    wanted.current = true;
    baseText.current = existingText.trim();
    const createRecognition = () => {
      const Ctor = recognitionCtor.current;
      if (!Ctor || !wanted.current) return;
      const r = new Ctor();
      r.lang = SPEECH_LOCALES[lang]; r.interimResults = true; r.continuous = true;
    r.onresult = (e) => {
      let transcript = "";
      for (let i = 0; i < e.results.length; i++) transcript += e.results[i][0].transcript;
      const joined = [baseText.current, transcript.trim()].filter(Boolean).join(baseText.current ? " " : "");
      onText(joined);
    };
      r.onerror = (e) => {
        setError(ERRORS[e.error] ?? `Erreur de dictée : ${e.error}`);
        if (["not-allowed", "service-not-allowed", "audio-capture", "language-not-supported"].includes(e.error)) {
          wanted.current = false;
          setListening(false);
        }
      };
      r.onend = () => {
        rec.current = null;
        if (wanted.current) {
          // Certains navigateurs coupent la reconnaissance après un silence même en continu.
          // On la relance tant que l'utilisateur n'a pas appuyé sur « Arrêter la dictée ».
          restartTimer.current = window.setTimeout(() => {
            if (!wanted.current) return;
            try { createRecognition(); }
            catch { wanted.current = false; setListening(false); setError("La dictée s'est interrompue. Appuyez sur le micro pour reprendre."); }
          }, 250);
        } else {
          setListening(false);
        }
      };
      try { rec.current = r; r.start(); setListening(true); }
      catch {
        rec.current = null; wanted.current = false; setListening(false);
        setError("Impossible de démarrer la dictée. Vérifiez les permissions du microphone.");
      }
    };
    createRecognition();
  }
  function stop() {
    wanted.current = false;
    if (restartTimer.current !== null) window.clearTimeout(restartTimer.current);
    restartTimer.current = null;
    try { rec.current?.stop(); } catch { /* déjà arrêté */ }
    setListening(false);
  }
  return { supported: Boolean(Rec), listening, error, start, stop };
}
