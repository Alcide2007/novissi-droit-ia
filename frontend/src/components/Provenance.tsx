import { useState } from "react";
import type { Lang } from "../api";
import { t } from "../i18n";

type P = {
  demo?: boolean; scope?: string; sha256?: string | null; version_id?: number | null; page?: number | null;
  collected?: string | null; verified?: boolean; url?: string; reference: string; lang?: Lang;
};

export default function Provenance(p: P) {
  const [copied, setCopied] = useState(false);
  const ui = t(p.lang || "Français");
  async function copy() {
    try { await navigator.clipboard.writeText(p.reference); setCopied(true); setTimeout(() => setCopied(false), 1500); } catch { /* copie indisponible */ }
  }
  return (
    <div className="prov">
      {p.demo && <p className="badge-demo" role="note">EXEMPLE FICTIF : {ui.demoNote}</p>}
      <p className="muted small">
        {p.version_id != null && <>Version {p.version_id}{p.sha256 ? ` (empreinte ${p.sha256.slice(0, 8)})` : ""} · </>}
        {p.page != null && <>page {p.page} · </>}
        {p.collected && <>{p.collected} · </>}
        {p.scope && p.scope !== "national" && !p.demo && <>{p.scope} · </>}
        {p.verified ? ui.verifiedStatus : ui.unverifiedStatus}
      </p>
      <div className="row">
        {p.url && <a href={p.url} target="_blank" rel="noopener noreferrer">{ui.originalSource}</a>}
        <button type="button" className="chip" onClick={() => void copy()}>{copied ? ui.refCopied : ui.copyRef}</button>
      </div>
    </div>
  );
}
