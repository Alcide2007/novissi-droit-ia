import { useCallback, useEffect, useState } from "react";
import * as api from "./api";
import type { Conversation, Lang, LetterKind, UserAccount } from "./api";
import ChatPage from "./components/ChatPage";
import { IconMenu, IconShare } from "./components/Icons";
import Sidebar, { type View } from "./components/Sidebar";
import ThemeToggle from "./components/ThemeToggle";
import ActeAnalyzer from "./features/ActeAnalyzer";
import LetterGenerator from "./features/LetterGenerator";
import PreventionFoncierPage from "./features/PreventionFoncierPage";
import TerraCheckPage from "./features/TerraCheckPage";
import { t } from "./i18n";

export default function App() {
  const [view, setView] = useState<View>("chat");
  const [lang, setLang] = useState<Lang>("Français");
  const [focus, setFocus] = useState<api.Diag | null>(null);
  const [selectedLetterKind, setSelectedLetterKind] = useState<LetterKind | null>(null);
  const [convs, setConvs] = useState<Conversation[]>([]);
  const [activeId, setActiveId] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [err, setErr] = useState("");
  const [menu, setMenu] = useState(false);
  const [collapsed, setCollapsed] = useState<boolean>(() => {
    try { return localStorage.getItem("novissi-sidebar-collapsed") === "1"; } catch { return false; }
  });
  const [user, setUser] = useState<UserAccount | null>(() => api.currentUser());
  const [transcript, setTranscript] = useState("");
  const [chatBusy, setChatBusy] = useState(false);

  const ui = t(lang);
  const TITRES: Record<View, string> = {
    chat: ui.titleChat,
    docs: ui.titleDocs,
    acte: ui.titleActe,
    terra: ui.titleTerra,
    prev: ui.titlePrev,
  };

  const refresh = useCallback(() => {
    api.listConversations(search).then((c) => { setConvs(c); setErr(""); })
      .catch((e: Error) => setErr(e.message));
  }, [search]);
  useEffect(refresh, [refresh]);

  function toggleCollapse() {
    setCollapsed((prev) => {
      const next = !prev;
      try { localStorage.setItem("novissi-sidebar-collapsed", next ? "1" : "0"); } catch { /* ignoré */ }
      return next;
    });
  }

  function handleUserChange(u: UserAccount | null) {
    setUser(u);
    setActiveId(null);
    refresh();
  }

  const handleTranscriptChange = useCallback((tr: string, b: boolean) => {
    setTranscript(tr);
    setChatBusy(b);
  }, []);

  async function shareCurrent() {
    const textToShare =
      view === "chat" && transcript.trim()
        ? transcript
        : focus
        ? `Novissi-Droit IA — Parcelle ${focus.name} (Verdict : ${focus.score.toUpperCase()})\nGPS : https://www.google.com/maps/search/?api=1&query=${focus.center[0]},${focus.center[1]}`
        : `Novissi-Droit IA — ${TITRES[view]} (${window.location.href})`;

    const payload = { title: `Novissi-Droit IA — ${TITRES[view]}`, text: textToShare };
    try {
      if (navigator.share) {
        await navigator.share(payload);
      } else if (navigator.clipboard?.writeText) {
        await navigator.clipboard.writeText(textToShare);
        window.alert("Le contenu a été copié dans le presse-papiers. Vous pouvez le partager où vous voulez.");
      } else {
        window.prompt("Copiez ce contenu pour le partager :", textToShare);
      }
    } catch (e) {
      if ((e as Error).name !== "AbortError") {
        window.alert("Impossible de partager depuis ce navigateur.");
      }
    }
  }

  return (
    <div className="shell">
      <Sidebar
        view={view}
        onView={setView}
        convs={convs}
        activeId={activeId}
        onOpen={setActiveId}
        onNew={() => setActiveId(null)}
        onChanged={refresh}
        onSearch={setSearch}
        open={menu}
        onClose={() => setMenu(false)}
        error={err}
        user={user}
        onUserChange={handleUserChange}
        collapsed={collapsed}
        onToggleCollapse={toggleCollapse}
        lang={lang}
      />
      {menu && <div className="scrim" onClick={() => setMenu(false)} />}
      <main className="main">
        <div className="topbar">
          <button type="button" className="icon burger" onClick={() => setMenu(true)} aria-label="Ouvrir le menu">
            <IconMenu size={18} />
          </button>
          <h1>{TITRES[view]}</h1>
          <div className="topbar-actions">
            <select
              className="topbar-lang"
              value={lang}
              onChange={(e) => setLang(e.target.value as Lang)}
              aria-label="Langue"
              title="Choisir la langue (Français, Ewé, Kabiyè)"
            >
              <option>Français</option>
              <option>Ewé</option>
              <option>Kabiyè</option>
            </select>
            <ThemeToggle lang={lang} />
            <button
              type="button"
              className="share-btn"
              onClick={() => void shareCurrent()}
              disabled={view === "chat" && (!transcript.trim() || chatBusy)}
              aria-label="Partager la conversation"
              title={ui.share}
            >
              <IconShare size={15} />
              <span>{ui.share}</span>
            </button>
          </div>
        </div>
        {view === "chat" && (
          <ChatPage
            lang={lang}
            convId={activeId}
            onConvId={setActiveId}
            onChanged={refresh}
            onTranscriptChange={handleTranscriptChange}
            onOpenLetter={(kind) => {
              setSelectedLetterKind(kind);
              setView("docs");
            }}
          />
        )}
        {view === "docs" && <div className="page"><LetterGenerator lang={lang} initialKind={selectedLetterKind} /></div>}
        {view === "acte" && (
          <div className="page">
            <ActeAnalyzer
              lang={lang}
              linkedParcel={focus}
              onMap={(d) => { setFocus(d); setView("terra"); }}
            />
          </div>
        )}
        {view === "terra" && (
          <div className="page">
            <TerraCheckPage
              focus={focus}
              lang={lang}
              onDecodeParcel={(d) => { setFocus(d); setView("acte"); }}
            />
          </div>
        )}
        {view === "prev" && (
          <div className="page">
            <PreventionFoncierPage
              lang={lang}
              onNavigate={(nextView, letterKind) => {
                if (letterKind) setSelectedLetterKind(letterKind);
                setView(nextView);
              }}
            />
          </div>
        )}
      </main>
    </div>
  );
}
