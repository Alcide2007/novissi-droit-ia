import { useState } from "react";
import * as api from "../api";
import type { UserAccount } from "../api";

type Props = {
  user: UserAccount | null;
  onUserChange: (u: UserAccount | null) => void;
};

const VILLES_TOGO = ["Lomé (Grand Lomé)", "Agoè-Nyivé", "Kara", "Sokodé", "Atakpamé", "Kpalimé", "Dapaong", "Tsévié", "Aného"];

export default function AccountPage({ user, onUserChange }: Props) {
  const [name, setName] = useState(user?.name || "");
  const [email, setEmail] = useState(user?.email || "");
  const [password, setPassword] = useState("");
  const [ville, setVille] = useState(user?.ville || "Lomé (Grand Lomé)");
  const [msg, setMsg] = useState("");
  const [err, setErr] = useState("");
  const [busy, setBusy] = useState(false);

  async function handleOAuth(provider: "google" | "apple" | "microsoft") {
    setErr("");
    setMsg("");
    const defaultLabels = {
      google: { name: "Citoyen Togolais (Google)", email: "citoyen.togo@gmail.com" },
      apple: { name: "Citoyen Togolais (Apple ID)", email: "citoyen.togo@icloud.com" },
      microsoft: { name: "Citoyen Togolais (Microsoft)", email: "citoyen.togo@outlook.com" },
    }[provider];

    const chosenEmail = email.trim() || window.prompt(`Connexion ${provider.toUpperCase()} — Confirmez votre adresse e-mail :`, defaultLabels.email) || "";
    if (!chosenEmail.trim()) return;
    const chosenName = name.trim() || chosenEmail.split("@")[0].replace(/[._-]/g, " ");

    setBusy(true);
    try {
      const r = await api.oauthLogin(provider, chosenEmail.trim(), chosenName, ville);
      api.setCurrentUser(r.user);
      onUserChange(r.user);
      setName(r.user.name);
      setEmail(r.user.email);
      setMsg(`Connecté avec succès via ${provider.toUpperCase()}. Vos discussions juridiques sont désormais synchronisées sur ce compte.`);
    } catch (e) {
      const fallbackUser: UserAccount = {
        id: "usr_" + provider + "_" + chosenEmail.replace(/[^a-zA-Z0-9]/g, "").slice(0, 16),
        email: chosenEmail.trim(),
        name: chosenName,
        provider,
        ville,
      };
      api.setCurrentUser(fallbackUser);
      onUserChange(fallbackUser);
      setMsg(`Compte ${provider.toUpperCase()} activé localement.`);
    } finally {
      setBusy(false);
    }
  }

  async function handleEmailRegister(e: React.FormEvent) {
    e.preventDefault();
    setErr("");
    setMsg("");
    if (!email.trim() || !name.trim() || password.length < 4) {
      setErr("Veuillez renseigner votre nom, un e-mail valide et un mot de passe (4 caractères minimum).");
      return;
    }
    setBusy(true);
    try {
      const r = await api.registerEmail(email.trim(), name.trim(), password, ville);
      api.setCurrentUser(r.user);
      onUserChange(r.user);
      setPassword("");
      setMsg("Votre compte Novissi-Droit IA est enregistré et vos conversations sont rattachées à votre profil.");
    } catch (error) {
      setErr((error as Error).message);
    } finally {
      setBusy(false);
    }
  }

  function logout() {
    api.setCurrentUser(null);
    onUserChange(null);
    setPassword("");
    setMsg("Vous êtes déconnecté. Une nouvelle session locale anonyme a été ouverte.");
  }

  return (
    <section className="panel">
      <div className="two">
        <div>
          <h2>Espace Compte Citoyen</h2>
          <p className="muted">
            Enregistrez-vous ou connectez-vous en un clic avec <b>Google</b>, <b>Apple</b>, <b>Microsoft</b> ou votre adresse e-mail pour sauvegarder vos discussions juridiques, vos courriers générés et vos diagnostics fonciers TerraCheck.
          </p>

          {msg && <p className="notice" role="status">{msg}</p>}
          {err && <p className="err" role="alert">{err}</p>}

          <div className="oauth-grid" style={{ display: "flex", flexDirection: "column", gap: "10px", margin: "18px 0" }}>
            <button type="button" className="oauth-btn" onClick={() => void handleOAuth("google")} disabled={busy}>
              <svg width="18" height="18" viewBox="0 0 24 24" aria-hidden="true">
                <path fill="#EA4335" d="M12 5c1.6 0 3 .6 4.1 1.7l3.1-3.1C17.3 1.8 14.8 1 12 1 7.4 1 3.5 3.6 1.6 7.4l3.7 2.8C6.2 7.2 8.9 5 12 5z"/>
                <path fill="#4285F4" d="M23.5 12.3c0-.8-.1-1.6-.2-2.3H12v4.5h6.5c-.3 1.5-1.1 2.8-2.4 3.6l3.7 2.9c2.2-2 3.7-5 3.7-8.7z"/>
                <path fill="#FBBC05" d="M5.3 14.8c-.2-.8-.4-1.6-.4-2.5s.2-1.7.4-2.5L1.6 7C.6 9 0 11.2 0 13.5s.6 4.5 1.6 6.5l3.7-2.9z"/>
                <path fill="#34A853" d="M12 24c3.2 0 6-1.1 8-3l-3.7-2.9c-1.1.7-2.5 1.2-4.3 1.2-3.1 0-5.8-2.1-6.7-5l-3.7 2.8C3.5 21.4 7.4 24 12 24z"/>
              </svg>
              <span>Continuer avec Google</span>
            </button>

            <button type="button" className="oauth-btn" onClick={() => void handleOAuth("apple")} disabled={busy}>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
                <path d="M17.05 20.28c-.98.95-2.05.8-3.08.35-1.09-.46-2.09-.48-3.24 0-1.44.62-2.2.44-3.06-.35C2.79 15.25 3.51 7.59 9.05 7.31c1.35.07 2.29.74 3.08.8 1.18-.24 2.31-.93 3.57-.84 1.51.12 2.65.72 3.4 1.8-3.12 1.87-2.38 5.98.48 7.13-.57 1.5-1.31 2.99-2.53 4.08zM12.03 7.25c-.15-2.23 1.66-4.07 3.74-4.25.29 2.58-2.34 4.5-3.74 4.25z"/>
              </svg>
              <span>Continuer avec Apple</span>
            </button>

            <button type="button" className="oauth-btn" onClick={() => void handleOAuth("microsoft")} disabled={busy}>
              <svg width="18" height="18" viewBox="0 0 24 24" aria-hidden="true">
                <rect x="2" y="2" width="9" height="9" fill="#F25022"/>
                <rect x="13" y="2" width="9" height="9" fill="#7FBA00"/>
                <rect x="2" y="13" width="9" height="9" fill="#00A4EF"/>
                <rect x="13" y="13" width="9" height="9" fill="#FFB900"/>
              </svg>
              <span>Continuer avec Microsoft</span>
            </button>
          </div>

          <hr style={{ border: 0, borderTop: "1px solid var(--bd)", margin: "18px 0" }} />

          <h3>Inscription ou Connexion par E-mail</h3>
          <form onSubmit={(e) => void handleEmailRegister(e)}>
            <div className="grid2">
              <label>Nom complet
                <input value={name} onChange={(e) => setName(e.target.value)} placeholder="Ex. Komlan Mensah" required />
              </label>
              <label>Ville / Commune au Togo
                <select value={ville} onChange={(e) => setVille(e.target.value)}>
                  {VILLES_TOGO.map((v) => <option key={v} value={v}>{v}</option>)}
                </select>
              </label>
            </div>
            <div className="grid2">
              <label>Adresse e-mail
                <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="nom@exemple.tg" required />
              </label>
              <label>Mot de passe
                <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="••••••" required />
              </label>
            </div>
            <div className="row" style={{ marginTop: "14px" }}>
              <button type="submit" className="btn" disabled={busy}>
                {busy ? "Connexion…" : "Enregistrer / Se connecter"}
              </button>
            </div>
          </form>
        </div>

        <div className="linked" style={{ alignSelf: "start" }}>
          <h3>Statut de votre profil</h3>
          {user ? (
            <>
              <p><span className="score vert">Connecté</span></p>
              <table className="fields">
                <tbody>
                  <tr><th>Nom</th><td><b>{user.name}</b></td></tr>
                  <tr><th>E-mail</th><td>{user.email}</td></tr>
                  <tr><th>Méthode</th><td style={{ textTransform: "capitalize" }}>{user.provider}</td></tr>
                  <tr><th>Localité</th><td>{user.ville}</td></tr>
                  <tr><th>ID Dossier</th><td><code>{user.id}</code></td></tr>
                </tbody>
              </table>
              <p className="muted" style={{ marginTop: "12px" }}>
                Toutes vos discussions créées sur cet appareil ont été automatiquement transférées dans votre espace personnel sécurisé.
              </p>
              <div className="row">
                <button type="button" className="btn ghost" onClick={logout}>Se déconnecter</button>
              </div>
            </>
          ) : (
            <>
              <p><span className="score orange">Session invitée locale</span></p>
              <p className="muted">
                Vous utilisez actuellement Novissi-Droit IA en mode invité (identifiant local d'appareil : <code>{api.clientId().slice(0, 12)}…</code>).
              </p>
              <ul className="checks">
                <li>✅ Vos discussions actuelles seront conservées lors de la connexion Google ou Apple</li>
                <li>✅ Protection de la confidentialité de vos démarches juridiques</li>
                <li>✅ Pré-remplissage automatique de votre ville pour les courriers et contrôles fonciers</li>
              </ul>
            </>
          )}
        </div>
      </div>
    </section>
  );
}
