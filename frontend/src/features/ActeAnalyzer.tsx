import { useEffect, useState } from "react";
import * as api from "../api";
import type { Lang, Score } from "../api";
import { IconCamera, IconNavigation, IconTerra } from "../components/Icons";
import { t } from "../i18n";

const ACTES_EXEMPLES: { id?: string; text: string }[] = [
  {
    id: "TG-AGN-014",
    text: "Acte de vente. Vendeur : Monsieur KOFFI Mensah vend à Madame AKAKPO Ama une parcelle située à Agoè-Nyivé, lot n° 14, îlot 3, d’une superficie de 600 m². Titre foncier n° 12345/TG. L’acquéreur paie le prix en totalité à la signature, sans aucune garantie du vendeur sur les limites du terrain.",
  },
  {
    id: "TG-KEG-031",
    text: "Reçu sous seing privé. Vendeur : Madame DOGBE Ama cède au nom de la collectivité familiale à Monsieur TOGBUI Yao un terrain situé à Kégué, lot n° 31, îlot 2, superficie de 500 m², en cours d’immatriculation (héritiers non signataires). Le prix est payé comptant entre les mains du vendeur hors la comptabilité du notaire et sans garantie d’éviction.",
  },
  {
    id: "TG-BAG-008",
    text: "Acte authentique par-devant Maître AQUEREBURU, Notaire à Lomé. Vendeur : Monsieur LAWSON Edem vend à Madame MENSAH Afi une parcelle sise à Baguida, lot n° 8, îlot 1, d’une superficie de 800 m², couverte par le Titre foncier n° 28910/RT avec plan parcellaire visé (trois tampons) par le cadastre de l’OTR.",
  },
];

function buildActeFromParcel(p: api.Diag): string {
  const pre = ACTES_EXEMPLES.find((a) => a.id === p.id);
  if (pre) return pre.text;
  return (
    `Acte de vente concernant la parcelle ${p.name}. Vendeur : Monsieur/Madame ${p.proprietaire || "INCONNU"} ` +
    `vend à l'Acquéreur un terrain situé à ${p.quartier}, lot n° ${p.lot}${p.ilot ? `, îlot ${p.ilot}` : ""}, ` +
    `d'une superficie de ${p.superficie_m2 || 500} m². Référence cadastrale : ${p.reference_titre || "sans titre foncier"}.`
  );
}

/** Fusionne tous les contrôles en UNE SEULE couleur (rouge | orange | vert) et UNE SEULE phrase dans la langue choisie. */
export function computeUnifiedVerdict(res: api.DecodeOut, lang: Lang = "Français"): {
  score: Score;
  sentence: string;
} {
  const ui = t(lang);
  const hasHighClause = res.clauses.some((c) => {
    const r = c.risque.toLowerCase();
    return r.startsWith("é") || r === "eleve" || r === "rouge";
  });
  const hasMedClause = res.clauses.some((c) => {
    const r = c.risque.toLowerCase();
    return r === "moyen" || r === "orange";
  });
  const tcScore = res.terracheck?.score;

  let score: Score = "vert";
  if (hasHighClause || tcScore === "rouge") {
    score = "rouge";
  } else if (hasMedClause || tcScore === "orange" || res.clauses.length > 0) {
    score = "orange";
  }

  // En Éwé ou Kabiyè, utiliser prioritairement la phrase traduite de l'interface si le backend est en mode règles français
  const firstClause = res.clauses[0]?.explication;
  const useBackendText = lang === "Français" || res.mode === "ia";
  const sentence =
    score === "rouge"
      ? (useBackendText && firstClause) || ui.verdictRougeDefault
      : score === "orange"
      ? (useBackendText && firstClause) || ui.verdictOrangeDefault
      : (useBackendText && res.resume) || ui.verdictVertDefault;

  return { score, sentence };
}

function highlightUnified(text: string, clauses: api.Clause[], unifiedScore: Score) {
  const spans = clauses
    .map((c) => ({ c, i: text.toLowerCase().indexOf(c.extrait.trim().toLowerCase()) }))
    .filter((x) => x.c.extrait.trim().length > 3 && x.i >= 0)
    .sort((a, b) => a.i - b.i);
  const out: React.ReactNode[] = [];
  let pos = 0;
  spans.forEach(({ c, i }, k) => {
    if (i < pos) return;
    out.push(text.slice(pos, i));
    out.push(
      <mark key={k} className={unifiedScore} title={c.explication}>
        {text.slice(i, i + c.extrait.trim().length)}
      </mark>
    );
    pos = i + c.extrait.trim().length;
  });
  out.push(text.slice(pos));
  return out;
}

type Props = {
  lang: Lang;
  linkedParcel?: api.Diag | null;
  onMap: (d: api.Diag) => void;
};

export default function ActeAnalyzer({ lang, linkedParcel, onMap }: Props) {
  const [text, setText] = useState("");
  const [res, setRes] = useState<api.DecodeOut | null>(null);
  const [msg, setMsg] = useState("");
  const [busy, setBusy] = useState(false);
  const ui = t(lang);

  useEffect(() => {
    if (linkedParcel && !text.trim()) {
      setText(buildActeFromParcel(linkedParcel));
    }
  }, [linkedParcel]); // eslint-disable-line react-hooks/exhaustive-deps

  async function photo(f?: File) {
    if (!f) return;
    setMsg(ui.loading);
    try {
      const r = await api.ocr(f);
      setText(r.text);
      setMsg("");
    } catch (e) { setMsg((e as Error).message); }
  }

  async function run() {
    setBusy(true); setMsg(""); setRes(null);
    try {
      const decoded = await api.decode(text, lang);
      setRes(decoded);
    } catch (e) { setMsg((e as Error).message); }
    setBusy(false);
  }

  const ch = res?.champs;
  const rows: [string, string | number | undefined | null][] = ch ? [
    [ui.registeredOwner, ch.proprietaire],
    [ui.buyerLabel, ch.acquereur],
    [ui.areaLabel, ch.superficie_m2],
    [ui.lotLabel, ch.lot],
    [ui.ilotLabel, ch.ilot],
    [ui.communeQuartier, ch.quartier],
    [ui.refTitreOtr, ch.reference_titre],
  ] : [];

  const unified = res ? computeUnifiedVerdict(res, lang) : null;
  const activeDiag = res?.terracheck || linkedParcel || null;

  return (
    <section className="panel">
      <div className="row" style={{ justifyContent: "space-between", marginTop: 0 }}>
        <p className="muted" style={{ margin: 0 }}>{ui.acteIntro}</p>
        {activeDiag && (
          <button type="button" className="chip" onClick={() => onMap(activeDiag)}>
            <IconTerra size={15} />
            <span>{ui.switchToTerra} ({activeDiag.name})</span>
          </button>
        )}
      </div>

      <div className="row">
        <label className="btn ghost" style={{ display: "inline-flex", alignItems: "center", gap: "8px" }}>
          <IconCamera size={16} />
          <span>{ui.photoActe}</span>
          <input type="file" accept="image/*" capture="environment" hidden onChange={(e) => photo(e.target.files?.[0])} />
        </label>
        <button type="button" className="chip" onClick={() => setText(ACTES_EXEMPLES[0].text)}>{ui.sample1}</button>
        <button type="button" className="chip" onClick={() => setText(ACTES_EXEMPLES[1].text)}>{ui.sample2}</button>
        <button type="button" className="chip" onClick={() => setText(ACTES_EXEMPLES[2].text)}>{ui.sample3}</button>
      </div>

      <textarea rows={6} value={text} onChange={(e) => setText(e.target.value)} aria-label="Texte de l’acte"
        placeholder={ui.actePlaceholder} />

      <div className="row">
        <button type="button" className="btn" onClick={run} disabled={busy || text.length < 10}>
          {busy ? ui.analyzing : ui.analyzeActe}
        </button>
      </div>

      {msg && <p className="muted">{msg}</p>}

      {res && unified && (
        <div className="result">
          <div className={"unified-verdict " + unified.score}>
            <div className="unified-verdict-head">
              <span className={"score " + unified.score}>{ui.scoreLabels[unified.score]}</span>
              <p className="unified-sentence">{unified.sentence}</p>
            </div>
            {res.clauses.length > 0 && (
              <p className="acte" style={{ marginTop: "10px", marginBottom: 0 }}>
                {highlightUnified(text, res.clauses, unified.score)}
              </p>
            )}
          </div>

          <h3>{ui.extractedInfo}</h3>
          <table className="fields">
            <tbody>
              {rows.filter(([, v]) => v !== undefined && v !== null && v !== "").map(([k, v]) => (
                <tr key={k}><th>{k}</th><td>{v}</td></tr>
              ))}
            </tbody>
          </table>

          {res.terracheck ? (
            <div className="linked" style={{ marginTop: "14px" }}>
              <div className="row" style={{ justifyContent: "space-between", marginTop: 0 }}>
                <div>
                  <b>{res.terracheck.name}</b>
                  <span className="muted" style={{ marginLeft: "8px" }}>
                    ({res.terracheck.reference_titre || "OTR"})
                  </span>
                </div>
                <div className="row" style={{ marginTop: 0 }}>
                  <button
                    type="button"
                    className="btn"
                    onClick={() => onMap({ ...res.terracheck!, score: unified.score })}
                  >
                    <IconTerra size={15} />
                    <span>{ui.seeOnMap}</span>
                  </button>
                  <a
                    className="chip no-underline"
                    href={`https://www.google.com/maps/dir/?api=1&destination=${res.terracheck.center[0]},${res.terracheck.center[1]}&travelmode=driving`}
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    <IconNavigation size={15} />
                    <span>{ui.mapsItinerary}</span>
                  </a>
                </div>
              </div>
            </div>
          ) : (
            <p className="muted">
              {res.match.status === "ambiguous" ? ui.ambiguousParcelMatch : ui.noParcelMatch}
            </p>
          )}
        </div>
      )}
    </section>
  );
}
