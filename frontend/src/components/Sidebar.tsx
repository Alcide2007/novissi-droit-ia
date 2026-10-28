import React, { useEffect, useState } from "react";
import * as api from "../api";
import type { Conversation, Lang, UserAccount } from "../api";
import { t } from "../i18n";
import AccountMenu from "./AccountMenu";
import {
  IconActe,
  IconCheck,
  IconClose,
  IconEdit,
  IconLetter,
  IconPlus,
  IconSidebarToggle,
  IconSparkle,
  IconTerra,
  IconTrash,
} from "./Icons";
import NovissiLogo from "./NovissiLogo";

export type View = "chat" | "docs" | "acte" | "terra" | "prev";

type Props = {
  view: View; onView: (v: View) => void; convs: Conversation[]; activeId: string | null;
  onOpen: (id: string) => void; onNew: () => void; onChanged: () => void; onSearch: (q: string) => void;
  open: boolean; onClose: () => void; error: string;
  user: UserAccount | null; onUserChange: (u: UserAccount | null) => void;
  collapsed: boolean; onToggleCollapse: () => void;
  lang?: Lang;
};

export default function Sidebar(p: Props) {
  const [q, setQ] = useState("");
  const ui = t(p.lang || "Français");
  useEffect(() => { const tm = setTimeout(() => p.onSearch(q), 250); return () => clearTimeout(tm); }, [q]); // eslint-disable-line react-hooks/exhaustive-deps

  const NAV: [View, string, React.ReactNode, string][] = [
    ["chat", ui.navChat, <IconSparkle size={18} />, "Assistant juridique"],
    ["docs", ui.navDocs, <IconLetter size={18} />, "Génération de courriers"],
    ["acte", ui.navActe, <IconActe size={18} />, "Analyse d’actes"],
    ["terra", ui.navTerra, <IconTerra size={18} />, "TerraCheck : vérification foncière"],
    ["prev", ui.navPrev, <IconCheck size={18} />, "Prévention achat terrain"],
  ];

  async function rename(c: Conversation) {
    const title = window.prompt("Nouveau titre", c.title);
    if (title && title.trim()) { try { await api.renameConversation(c.id, title.trim()); p.onChanged(); } catch (e) { window.alert((e as Error).message); } }
  }
  async function remove(c: Conversation) {
    if (!window.confirm(`Supprimer « ${c.title} » ? Cette action est définitive.`)) return;
    try { await api.deleteConversation(c.id); if (c.id === p.activeId) p.onNew(); p.onChanged(); } catch (e) { window.alert((e as Error).message); }
  }

  return (
    <aside className={"sidebar" + (p.open ? " open" : "") + (p.collapsed ? " collapsed" : "")} aria-label="Navigation">
      <div className="side-head">
        <div className="logo" aria-hidden>
          <NovissiLogo size={34} />
        </div>
        {!p.collapsed && (
          <div className="brand-copy">
            <strong>Novissi-Droit IA</strong>
            <small>{ui.slogan}</small>
          </div>
        )}
        <button
          type="button"
          className="icon collapse-btn"
          onClick={p.onToggleCollapse}
          aria-label={p.collapsed ? "Agrandir la barre latérale" : "Replier la barre latérale"}
          title={p.collapsed ? "Agrandir le menu latéral" : "Replier le menu latéral"}
        >
          <IconSidebarToggle size={18} />
        </button>
        <button type="button" className="icon close" onClick={p.onClose} aria-label="Fermer le menu">
          <IconClose size={16} />
        </button>
      </div>
      <button
        type="button"
        className="new-chat"
        aria-label="Nouvelle conversation"
        title={ui.newChat}
        onClick={() => { p.onNew(); p.onView("chat"); p.onClose(); }}
      >
        <IconPlus size={18} />
        {!p.collapsed && <span>{ui.newChat}</span>}
      </button>
      <nav aria-label="Fonctionnalités">
        {NAV.map(([k, l, icon, accessibleLabel]) => (
          <button
            key={k}
            type="button"
            className="nav-item"
            aria-label={accessibleLabel}
            title={l}
            aria-current={p.view === k ? "page" : undefined}
            onClick={() => { p.onView(k); p.onClose(); }}
          >
            <span className="nav-icon" aria-hidden>{icon}</span>
            {!p.collapsed && <span>{l}</span>}
          </button>
        ))}
      </nav>
      {!p.collapsed && (
        <>
          <div className="history-label">{ui.historyLabel}</div>
          <input
            className="side-search"
            type="search"
            placeholder={ui.searchConvPlaceholder}
            aria-label="Rechercher une conversation"
            value={q}
            onChange={(e) => setQ(e.target.value)}
          />
          <div className="history" aria-label="Historique des conversations">
            {p.error && <p className="err small">{p.error}</p>}
            {!p.error && !p.convs.length && <p className="muted small">{ui.noConv}</p>}
            {p.convs.map((c) => (
              <div key={c.id} className={"conv" + (c.id === p.activeId && p.view === "chat" ? " active" : "")}>
                <button className="conv-open" onClick={() => { p.onOpen(c.id); p.onView("chat"); p.onClose(); }} title={c.title}>{c.title}</button>
                <button className="icon" onClick={() => rename(c)} aria-label={`Renommer ${c.title}`}><IconEdit size={14} /></button>
                <button className="icon" onClick={() => remove(c)} aria-label={`Supprimer ${c.title}`}><IconTrash size={14} /></button>
              </div>
            ))}
          </div>
        </>
      )}
      <div className="side-foot">
        <AccountMenu user={p.user} onUserChange={p.onUserChange} placement="bottom-left" collapsed={p.collapsed} lang={p.lang} />
      </div>
    </aside>
  );
}
