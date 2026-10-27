import { useState } from "react";
import * as api from "../api";
import type { Lang, LetterKind } from "../api";
import { IconCopy, IconLetter } from "../components/Icons";
import { t } from "../i18n";

export default function LetterGenerator({ lang = "Français" }: { lang?: Lang }) {
  const [f, setF] = useState<api.LetterIn>({
    kind: "salaire",
    nom: "",
    adresse: "",
    telephone: "",
    destinataire: "",
    ville: "Lomé",
    periode: "",
    reference_parcelle: "",
    details: "",
    delai_jours: 8,
  });
  const [res, setRes] = useState<api.LetterOut | null>(null);
  const [err, setErr] = useState("");
  const [busy, setBusy] = useState(false);
  const ui = t(lang);
  const set = <K extends keyof api.LetterIn>(k: K, v: api.LetterIn[K]) => setF((p) => ({ ...p, [k]: v }));

  const LETTER_CATEGORIES: { group: string; items: { value: LetterKind; label: string; destLabel: string; destPlaceholder: string; showAmount?: boolean; showParcel?: boolean }[] }[] = [
    {
      group: ui.groupTravail,
      items: [
        { value: "salaire", label: ui.letterSalaire, destLabel: ui.employer, destPlaceholder: "Ex. Monsieur le Directeur Général", showAmount: true },
        { value: "inspection_travail", label: ui.letterInspectionTravail, destLabel: "Inspection du Travail", destPlaceholder: "Ex. Monsieur l’Inspecteur du Travail (Lomé)", showAmount: true },
        { value: "licenciement_abusif", label: ui.letterLicenciement, destLabel: ui.employer, destPlaceholder: "Ex. Monsieur le Directeur", showAmount: true },
        { value: "certificat_travail", label: ui.letterCertificat, destLabel: ui.employer, destPlaceholder: "Ex. Madame la Directrice des Ressources Humaines" },
      ],
    },
    {
      group: ui.groupBail,
      items: [
        { value: "bail", label: ui.letterBail, destLabel: ui.landlord, destPlaceholder: "Ex. Monsieur KOFFI (Propriétaire)" },
        { value: "restitution_caution", label: ui.letterRestitutionCaution, destLabel: ui.landlord, destPlaceholder: "Ex. Madame ADJOVI (Bailleresse)", showAmount: true },
        { value: "preavis_locataire", label: ui.letterPreavisLocataire, destLabel: ui.landlord, destPlaceholder: "Ex. Monsieur LAWSON (Propriétaire)" },
      ],
    },
    {
      group: ui.groupFoncier,
      items: [
        { value: "opposition_fonciere", label: ui.letterOppFoncier, destLabel: ui.destLabelOtr, destPlaceholder: "Monsieur le Conservateur (OTR)", showParcel: true },
        { value: "demande_etat_descriptif", label: ui.letterEtatDescriptif, destLabel: ui.destLabelOtr, destPlaceholder: "Monsieur le Directeur du Cadastre (OTR)", showParcel: true },
        { value: "mise_en_demeure_vendeur", label: ui.letterMiseDemeureVendeur, destLabel: ui.destLabelVendeur, destPlaceholder: "Ex. Monsieur AMEGAH (Vendeur)", showAmount: true, showParcel: true },
      ],
    },
    {
      group: ui.groupJustice,
      items: [
        { value: "plainte_procureur", label: ui.letterPlainte, destLabel: ui.destLabelProc, destPlaceholder: "Monsieur le Procureur de la République", showAmount: true, showParcel: true },
        { value: "reconnaissance_dette", label: ui.letterDette, destLabel: ui.destLabelDebiteur, destPlaceholder: "Ex. Monsieur MENSAH", showAmount: true },
      ],
    },
  ];

  const ALL_ITEMS = LETTER_CATEGORIES.flatMap((c) => c.items);
  const currentMeta = ALL_ITEMS.find((i) => i.value === f.kind) || ALL_ITEMS[0];

  function onKindChange(nextKind: LetterKind) {
    const meta = ALL_ITEMS.find((i) => i.value === nextKind);
    setF((prev) => ({
      ...prev,
      kind: nextKind,
      destinataire:
        nextKind === "opposition_fonciere" || nextKind === "demande_etat_descriptif"
          ? "Monsieur le Conservateur de la Propriété (OTR)"
          : nextKind === "inspection_travail"
          ? "Monsieur l’Inspecteur du Travail et des Lois Sociales"
          : meta?.destPlaceholder.includes("Procureur")
          ? "Monsieur le Procureur de la République près le TPI"
          : "",
    }));
  }

  async function go() {
    setBusy(true); setErr(""); setRes(null);
    try { setRes(await api.letter(f)); } catch (e) { setErr((e as Error).message); }
    setBusy(false);
  }

  function download() {
    if (!res) return;
    const a = document.createElement("a");
    a.href = URL.createObjectURL(new Blob([res.texte], { type: "text/plain;charset=utf-8" }));
    a.download = `courrier-${f.kind}-togo.txt`;
    a.click();
  }

  return (
    <section className="panel">
      <p className="muted" style={{ marginTop: 0 }}>{ui.letterIntro}</p>
      <div className="grid2">
        <label style={{ gridColumn: "1 / -1" }}>{ui.letterType}
          <select value={f.kind} onChange={(e) => onKindChange(e.target.value as LetterKind)}>
            {LETTER_CATEGORIES.map((cat) => (
              <optgroup key={cat.group} label={cat.group}>
                {cat.items.map((it) => (
                  <option key={it.value} value={it.value}>{it.label}</option>
                ))}
              </optgroup>
            ))}
          </select>
        </label>

        <label>{ui.fullName}
          <input value={f.nom} placeholder="Ex. KOFFI Mensah" onChange={(e) => set("nom", e.target.value)} />
        </label>
        <label>{ui.telTogo}
          <input value={f.telephone ?? ""} placeholder="Ex. (+228) 90 00 00 00" onChange={(e) => set("telephone", e.target.value)} />
        </label>
        <label>{ui.yourAddress}
          <input value={f.adresse} placeholder="Ex. Quartier Agoè-Nyivé, près du marché" onChange={(e) => set("adresse", e.target.value)} />
        </label>
        <label>{ui.city}
          <input value={f.ville} placeholder="Ex. Lomé, Kara, Sokodé, Kpalimé…" onChange={(e) => set("ville", e.target.value)} />
        </label>
        <label style={{ gridColumn: "1 / -1" }}>{currentMeta.destLabel}
          <input value={f.destinataire} placeholder={currentMeta.destPlaceholder} onChange={(e) => set("destinataire", e.target.value)} />
        </label>

        {currentMeta.showParcel && (
          <label style={{ gridColumn: "1 / -1" }}>{ui.parcelRef}
            <input value={f.reference_parcelle ?? ""} placeholder="Ex. Agoè-Nyivé, Lot n° 14, Îlot 3 — TF n° 12345/TG" onChange={(e) => set("reference_parcelle", e.target.value)} />
          </label>
        )}

        {currentMeta.showAmount && (
          <>
            <label>{ui.amountDue}
              <input type="number" min={0} value={f.montant_fcfa ?? ""} placeholder="Ex. 300000" onChange={(e) => set("montant_fcfa", e.target.value ? Number(e.target.value) : undefined)} />
            </label>
            <label>{ui.unpaidPeriod}
              <input value={f.periode} placeholder={ui.unpaidPeriodPlaceholder} onChange={(e) => set("periode", e.target.value)} />
            </label>
          </>
        )}
      </div>

      <label>{ui.extraDetails}
        <textarea rows={3} value={f.details} placeholder="Exposez brièvement les faits importants (dates, témoins, accords…)" onChange={(e) => set("details", e.target.value)} />
      </label>

      <div className="row">
        <button type="button" className="btn" onClick={go} disabled={busy || f.nom.length < 2 || f.destinataire.length < 2}>
          <IconLetter size={16} />
          <span>{busy ? ui.generatingLetter : ui.generateLetter}</span>
        </button>
      </div>

      {err && <p className="err">{err}</p>}

      {res && (
        <div className="result">
          <h2>{res.titre}</h2>
          <pre className="letter" style={{ fontFamily: "monospace", padding: "20px", fontSize: "13px", lineHeight: "1.6" }}>{res.texte}</pre>
          <div className="row">
            <button type="button" className="btn" onClick={() => navigator.clipboard?.writeText(res.texte)}>
              <IconCopy size={15} />
              <span>{ui.copy}</span>
            </button>
            <button type="button" className="btn ghost" onClick={download}>{ui.download}</button>
          </div>
          <h3>{ui.whereToGo}</h3>
          <ul>
            {res.services.map((s) => (
              <li key={s.nom}><b>{s.nom}</b> : {s.role}. <span className="muted">{s.adresse}</span></li>
            ))}
          </ul>
          {res.references.length > 0 && (
            <>
              <h3>{ui.refTexts}</h3>
              {res.references.map((s) => (
                <details key={s.id}><summary>{s.ref}</summary><p>{s.texte}</p></details>
              ))}
            </>
          )}
          <p className="muted">{res.disclaimer}</p>
        </div>
      )}
    </section>
  );
}
