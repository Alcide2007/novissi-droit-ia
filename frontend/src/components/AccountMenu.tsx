import { useEffect, useRef, useState } from "react";
import * as api from "../api";
import type { Lang, UserAccount } from "../api";
import { t } from "../i18n";
import { IconClose, IconLogout, IconSparkle, IconSwitchUser, IconUser } from "./Icons";

type Props = {
  user: UserAccount | null;
  onUserChange: (u: UserAccount | null) => void;
  placement?: "bottom-left" | "top-right";
  collapsed?: boolean;
  lang?: Lang;
};

const VILLES_TOGO = ["Lomé (Grand Lomé)", "Agoè-Nyivé", "Kara", "Sokodé", "Atakpamé", "Kpalimé", "Dapaong", "Tsévié", "Aného"];

export default function AccountMenu({ user, onUserChange, placement = "bottom-left", collapsed = false, lang = "Français" }: Props) {
  const [open, setOpen] = useState(false);
  const [busy, setBusy] = useState(false);
  const [showEmailForm, setShowEmailForm] = useState(false);
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [ville, setVille] = useState("Lomé (Grand Lomé)");
  const [err, setErr] = useState("");
  const menuRef = useRef<HTMLDivElement>(null);
  const ui = t(lang);

  useEffect(() => {
    function onClickOutside(e: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    }
    function onKey(e: KeyboardEvent) {
      if (e.key === "Escape") setOpen(false);
    }
    if (open) {
      document.addEventListener("mousedown", onClickOutside);
      document.addEventListener("keydown", onKey);
    }
    return () => {
      document.removeEventListener("mousedown", onClickOutside);
      document.removeEventListener("keydown", onKey);
    };
  }, [open]);

  async function quickOAuth(provider: "google" | "apple" | "microsoft") {
    setErr("");
    const defaults = {
      google: "citoyen.togo@gmail.com",
      apple: "citoyen.togo@icloud.com",
      microsoft: "citoyen.togo@outlook.com",
    }[provider];
    const chosenEmail = window.prompt(`${provider.toUpperCase()} — E-mail :`, defaults) || "";
    if (!chosenEmail.trim()) return;
    const chosenName = chosenEmail.split("@")[0].replace(/[._-]/g, " ");

    setBusy(true);
    try {
      const r = await api.oauthLogin(provider, chosenEmail.trim(), chosenName, ville);
      api.setCurrentUser(r.user);
      onUserChange(r.user);
      setOpen(false);
    } catch {
      const fallback: UserAccount = {
        id: "usr_" + provider + "_" + chosenEmail.replace(/[^a-zA-Z0-9]/g, "").slice(0, 16),
        email: chosenEmail.trim(),
        name: chosenName,
        provider,
        ville,
      };
      api.setCurrentUser(fallback);
      onUserChange(fallback);
      setOpen(false);
    } finally {
      setBusy(false);
    }
  }

  async function submitEmail(e: React.FormEvent) {
    e.preventDefault();
    setErr("");
    if (!email.trim() || !name.trim() || password.length < 4) {
      setErr("4+ caractères requis.");
      return;
    }
    setBusy(true);
    try {
      const r = await api.registerEmail(email.trim(), name.trim(), password, ville);
      api.setCurrentUser(r.user);
      onUserChange(r.user);
      setShowEmailForm(false);
      setOpen(false);
    } catch (error) {
      setErr((error as Error).message);
    } finally {
      setBusy(false);
    }
  }

  function logout() {
    api.setCurrentUser(null);
    onUserChange(null);
    setOpen(false);
  }

  const initial = user?.name ? user.name.trim().charAt(0).toUpperCase() : null;

  return (
    <div className={"acct-menu-wrap " + (placement === "bottom-left" ? "acct-bottom-left" : "acct-top-right")} ref={menuRef}>
      {user ? (
        <button
          type="button"
          className={"acct-sidebar-btn connected" + (collapsed ? " compact" : "")}
          onClick={() => setOpen(!open)}
          aria-label={`Mon compte : ${user.name}`}
          title={`${user.name} (${user.email})`}
        >
          <span className="acct-ring">
            <span className="acct-circle">{initial}</span>
          </span>
          {!collapsed && (
            <span className="acct-meta">
              <strong>{user.name}</strong>
              <small>{user.email}</small>
            </span>
          )}
        </button>
      ) : (
        <button
          type="button"
          className={"acct-sidebar-btn" + (collapsed ? " compact" : "")}
          onClick={() => setOpen(!open)}
          aria-label="Se connecter à mon compte"
          title={ui.signIn}
        >
          <span className="acct-ring">
            <span className="acct-circle"><IconUser size={16} /></span>
          </span>
          {!collapsed && (
            <span className="acct-meta">
              <strong>{ui.signIn}</strong>
              <small>{ui.signInSub}</small>
            </span>
          )}
        </button>
      )}

      {open && (
        <div className={"acct-popover " + (placement === "bottom-left" ? "popover-up" : "")} role="dialog" aria-label="Menu du compte">
          <button
            type="button"
            className="icon acct-close"
            onClick={() => setOpen(false)}
            aria-label="Fermer"
          >
            <IconClose size={15} />
          </button>

          {user ? (
            <>
              <div className="acct-email-top">{user.email}</div>
              <div className="acct-big-avatar">
                <span>{initial}</span>
              </div>
              <div className="acct-hello">{ui.greeting.split(",")[0]} {user.name.split(" ")[0]} !</div>
              <span className="acct-provider-pill">
                {user.provider.toUpperCase()} · {user.ville}
              </span>

              <div className="acct-actions-card">
                <button type="button" className="acct-action-row" onClick={() => void quickOAuth("google")}>
                  <IconSwitchUser size={16} />
                  <span>{ui.switchAccount}</span>
                </button>
                <button type="button" className="acct-action-row" onClick={logout}>
                  <IconLogout size={16} />
                  <span>{ui.logout}</span>
                </button>
              </div>
            </>
          ) : (
            <>
              <div className="acct-email-top">Novissi-Droit IA</div>
              <div className="acct-big-avatar guest">
                <span><IconSparkle size={24} /></span>
              </div>
              <div className="acct-hello">{ui.signIn}</div>
              <p className="acct-sub">{ui.accountSaveNote}</p>

              <div className="acct-oauth-list">
                <button type="button" className="oauth-btn" onClick={() => void quickOAuth("google")} disabled={busy}>
                  <svg width="18" height="18" viewBox="0 0 24 24" aria-hidden="true">
                    <path fill="#EA4335" d="M12 5c1.6 0 3 .6 4.1 1.7l3.1-3.1C17.3 1.8 14.8 1 12 1 7.4 1 3.5 3.6 1.6 7.4l3.7 2.8C6.2 7.2 8.9 5 12 5z"/>
                    <path fill="#4285F4" d="M23.5 12.3c0-.8-.1-1.6-.2-2.3H12v4.5h6.5c-.3 1.5-1.1 2.8-2.4 3.6l3.7 2.9c2.2-2 3.7-5 3.7-8.7z"/>
                    <path fill="#FBBC05" d="M5.3 14.8c-.2-.8-.4-1.6-.4-2.5s.2-1.7.4-2.5L1.6 7C.6 9 0 11.2 0 13.5s.6 4.5 1.6 6.5l3.7-2.9z"/>
                    <path fill="#34A853" d="M12 24c3.2 0 6-1.1 8-3l-3.7-2.9c-1.1.7-2.5 1.2-4.3 1.2-3.1 0-5.8-2.1-6.7-5l-3.7 2.8C3.5 21.4 7.4 24 12 24z"/>
                  </svg>
                  <span>{ui.continueGoogle}</span>
                </button>

                <button type="button" className="oauth-btn" onClick={() => void quickOAuth("apple")} disabled={busy}>
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
                    <path d="M17.05 20.28c-.98.95-2.05.8-3.08.35-1.09-.46-2.09-.48-3.24 0-1.44.62-2.2.44-3.06-.35C2.79 15.25 3.51 7.59 9.05 7.31c1.35.07 2.29.74 3.08.8 1.18-.24 2.31-.93 3.57-.84 1.51.12 2.65.72 3.4 1.8-3.12 1.87-2.38 5.98.48 7.13-.57 1.5-1.31 2.99-2.53 4.08zM12.03 7.25c-.15-2.23 1.66-4.07 3.74-4.25.29 2.58-2.34 4.5-3.74 4.25z"/>
                  </svg>
                  <span>{ui.continueApple}</span>
                </button>

                <button type="button" className="oauth-btn" onClick={() => void quickOAuth("microsoft")} disabled={busy}>
                  <svg width="18" height="18" viewBox="0 0 24 24" aria-hidden="true">
                    <rect x="2" y="2" width="9" height="9" fill="#F25022"/>
                    <rect x="13" y="2" width="9" height="9" fill="#7FBA00"/>
                    <rect x="2" y="13" width="9" height="9" fill="#00A4EF"/>
                    <rect x="13" y="13" width="9" height="9" fill="#FFB900"/>
                  </svg>
                  <span>{ui.continueMicrosoft}</span>
                </button>

                <button
                  type="button"
                  className="acct-manage-btn"
                  onClick={() => setShowEmailForm(!showEmailForm)}
                >
                  {showEmailForm ? ui.hideEmail : ui.useEmail}
                </button>
              </div>

              {showEmailForm && (
                <form className="acct-email-form" onSubmit={(e) => void submitEmail(e)}>
                  {err && <p className="err small">{err}</p>}
                  <input placeholder={ui.fullName} value={name} onChange={(e) => setName(e.target.value)} required />
                  <select value={ville} onChange={(e) => setVille(e.target.value)} aria-label="Ville au Togo">
                    {VILLES_TOGO.map((v) => <option key={v} value={v}>{v}</option>)}
                  </select>
                  <input type="email" placeholder="E-mail" value={email} onChange={(e) => setEmail(e.target.value)} required />
                  <input type="password" placeholder="••••••" value={password} onChange={(e) => setPassword(e.target.value)} required />
                  <button type="submit" className="btn" style={{ width: "100%", marginTop: "6px" }} disabled={busy}>
                    {ui.saveAccount}
                  </button>
                </form>
              )}
            </>
          )}

          <div className="acct-foot">
            <span>Novissi-Droit IA</span> · <span>Togo</span>
          </div>
        </div>
      )}
    </div>
  );
}
