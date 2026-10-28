import { useEffect, useState } from "react";
import * as api from "../api";
import type { CollectionStatus, LegalHit } from "../api";
import Provenance from "../components/Provenance";

const MODES: Record<CollectionStatus["corpus_mode"], string> = {
  officiel: "Corpus officiel (textes collectés)", demonstration: "MODE DÉMONSTRATION : textes fictifs uniquement", mixte: "Corpus officiel + textes de démonstration",
};

export default function LegalSearchPage() {
  const [q, setQ] = useState("");
  const [source, setSource] = useState("");
  const [hits, setHits] = useState<LegalHit[] | null>(null);
  const [note, setNote] = useState("");
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");
  const [status, setStatus] = useState<CollectionStatus | null>(null);

  useEffect(() => { api.collectionStatus().then(setStatus).catch(() => setStatus(null)); }, []);

  async function search(e?: React.FormEvent) {
    e?.preventDefault();
    if (q.trim().length < 2 || busy) return;
    setBusy(true); setErr("");
    try { const r = await api.legalSearch(q.trim(), source); setHits(r.hits); setNote(r.note); }
    catch (x) { setErr((x as Error).message); setHits(null); }
    finally { setBusy(false); }
  }

  return (
    <div className="legal-search">
      {status && (
        <section className={"corpus-state" + (status.corpus_mode === "demonstration" ? " demo" : "")} aria-label="État du corpus">
          <strong>{MODES[status.corpus_mode]}</strong>
          <p className="muted small">
            {status.indexed_chunks} extraits indexés · {status.documents_extracted} document(s) extrait(s) · {status.documents_not_extracted} à revoir ·
            {" "}{status.versions_total} version(s) · {status.listing_pages_inspected} page(s) de liste inspectée(s)
          </p>
          {!status.complete_within_scope && status.reasons_incomplete.length > 0 &&
            <details><summary>Collecte incomplète ({status.reasons_incomplete.length} raison(s))</summary>
              <ul>{status.reasons_incomplete.map((r) => <li key={r}>{r}</li>)}</ul><p className="muted small">{status.note}</p></details>}
        </section>
      )}
      <form className="search-row" onSubmit={(e) => void search(e)} role="search">
        <input type="search" value={q} onChange={(e) => setQ(e.target.value)} aria-label="Recherche juridique"
          placeholder="Mot-clé, titre, ou « article 12 »" maxLength={200} />
        <select value={source} onChange={(e) => setSource(e.target.value)} aria-label="Filtrer par source">
          <option value="">Toutes les sources</option>
          {status?.sources.map((s) => <option key={s.key} value={s.key}>{s.name}</option>)}
        </select>
        <button className="btn" type="submit" disabled={busy || q.trim().length < 2}>{busy ? "Recherche…" : "Rechercher"}</button>
      </form>
      {err && <p className="err" role="alert">{err}</p>}
      {hits && !hits.length && <p className="muted">Aucun texte trouvé dans le corpus collecté. Cela ne signifie pas que le texte n’existe pas.</p>}
      {hits?.map((h) => (
        <article key={h.article_id} className="hit">
          <h3>{h.ref}</h3>
          {(h.reference || h.title) && <p className="muted small">{[h.reference, h.doc_date, h.title].filter(Boolean).join(" · ")}</p>}
          <p>{h.texte}</p>
          <Provenance demo={h.demo} scope={h.scope} sha256={h.sha256} version_id={h.version_id} page={h.page}
            collected={h.collected} verified={h.verified} url={h.url} reference={h.ref} />
        </article>
      ))}
      {hits && note && <p className="muted small">{note}</p>}
    </div>
  );
}
