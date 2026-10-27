import { useEffect, useRef, useState } from "react";
import L from "leaflet";
import * as api from "../api";
import type { Lang, Score } from "../api";
import { IconActe, IconAlert, IconCalendar, IconCheck, IconClock, IconMapPin, IconNavigation } from "../components/Icons";
import { t, translateAdvice, translateCheckLabel } from "../i18n";

const COULEUR: Record<Score, string> = { vert: "#2E8B57", orange: "#D9822B", rouge: "#C0392B" };

type Props = {
  focus: api.Diag | null;
  onDecodeParcel?: (d: api.Diag) => void;
  lang?: Lang;
};

export default function TerraCheckPage({ focus, onDecodeParcel, lang = "Français" }: Props) {
  const el = useRef<HTMLDivElement>(null);
  const map = useRef<L.Map | null>(null);
  const layer = useRef<L.LayerGroup | null>(null);
  const [list, setList] = useState<api.Diag[]>([]);
  const [sel, setSel] = useState<api.Diag | null>(focus);
  const [filter, setFilter] = useState("");
  const [err, setErr] = useState("");
  const ui = t(lang);

  useEffect(() => {
    if (!el.current || map.current) return;
    const m = L.map(el.current).setView([6.19, 1.23], 12);
    L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", { attribution: "© OpenStreetMap" }).addTo(m);
    layer.current = L.layerGroup().addTo(m);
    map.current = m;
    api.parcels().then((data) => {
      setList(data);
      if (!focus && data.length > 0) setSel(data[0]);
    }).catch((e: Error) => setErr(e.message));
    return () => { m.remove(); map.current = null; };
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    if (!layer.current) return;
    layer.current.clearLayers();
    list.forEach((d) => {
      const shown = focus && focus.id === d.id ? focus : d;
      const active = sel?.id === d.id;
      L.polygon(d.polygon, { color: COULEUR[shown.score], fillOpacity: active ? 0.8 : 0.5, weight: active ? 5 : 3 })
        .addTo(layer.current!).on("click", () => {
          setSel(shown);
          map.current?.flyTo(shown.center, 15, { duration: 0.8 });
        }).bindTooltip(`${d.name} (${shown.score.toUpperCase()})`);
    });
  }, [list, focus, sel]);

  useEffect(() => {
    if (!focus || !map.current) return;
    setSel(focus);
    map.current.flyTo(focus.center, 15, { duration: 1 });
  }, [focus]);

  const filtered = list.filter((p) =>
    !filter.trim() ||
    `${p.name} ${p.quartier} ${p.lot} ${p.reference_titre || ""} ${p.proprietaire || ""}`.toLowerCase().includes(filter.toLowerCase())
  );

  const mapsDirUrl = sel
    ? `https://www.google.com/maps/dir/?api=1&destination=${sel.center[0]},${sel.center[1]}&travelmode=driving`
    : "#";

  return (
    <section className="panel">
      <div className="row" style={{ justifyContent: "space-between", marginBottom: "14px", marginTop: 0 }}>
        <p className="muted" style={{ margin: 0 }}>{ui.terraIntro}</p>
        <input
          type="search"
          placeholder={ui.terraSearchPlaceholder}
          aria-label="Filtrer les parcelles"
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          style={{ maxWidth: "340px" }}
        />
      </div>

      <div className="chips" style={{ marginBottom: "14px" }}>
        {filtered.map((d) => {
          const shown = focus && focus.id === d.id ? focus : d;
          return (
            <button
              key={d.id}
              type="button"
              className="chip"
              style={{
                borderColor: sel?.id === d.id ? COULEUR[shown.score] : undefined,
                fontWeight: sel?.id === d.id ? 700 : 500,
              }}
              onClick={() => {
                setSel(shown);
                map.current?.flyTo(shown.center, 15, { duration: 0.8 });
              }}
            >
              <span className={"score " + shown.score} style={{ padding: "1px 8px", fontSize: "11px" }}>{ui.scoreLabels[shown.score]}</span>
              <span>{d.name}</span>
            </button>
          );
        })}
      </div>

      <div className="two">
        <div ref={el} className="map" aria-label="Carte des parcelles" />
        <div className="detail">
          {err && <p className="err">{err}</p>}
          {!sel ? (
            <p className="muted">{ui.terraIntro}</p>
          ) : (
            <>
              <div className="row" style={{ justifyContent: "space-between", marginTop: 0 }}>
                <h2 style={{ margin: 0 }}>{sel.name}</h2>
                <span className={"score " + sel.score}>{ui.scoreLabels[sel.score]}</span>
              </div>

              <div className="row" style={{ marginTop: "12px", marginBottom: "10px" }}>
                <a
                  className="btn no-underline"
                  href={mapsDirUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  aria-label="Me diriger vers ce terrain avec Google Maps"
                >
                  <IconNavigation size={15} />
                  <span>{ui.mapsItinerary}</span>
                </a>
                {onDecodeParcel && (
                  <button type="button" className="chip" onClick={() => onDecodeParcel(sel)}>
                    <IconActe size={15} />
                    <span>{ui.analyzeThisActe}</span>
                  </button>
                )}
              </div>

              <p className="muted small" style={{ textAlign: "left", display: "flex", alignItems: "center", gap: "6px", margin: "4px 0 10px" }}>
                <IconMapPin size={14} />
                <span>{ui.gpsCoords} : {sel.center[0].toFixed(5)}° N, {sel.center[1].toFixed(5)}° E</span>
              </p>

              <table className="fields" style={{ marginTop: "6px" }}>
                <tbody>
                  <tr><th>{ui.communeQuartier}</th><td>{sel.commune || sel.quartier} ({ui.ilotLabel} {sel.ilot || "—"}, {ui.lotLabel} {sel.lot})</td></tr>
                  <tr><th>{ui.legalStatus}</th><td>{sel.nature_terrain || "Lotissement"}</td></tr>
                  <tr><th>{ui.refTitreOtr}</th><td><b>{sel.reference_titre || "—"}</b> ({sel.requisition || "—"})</td></tr>
                  <tr>
                    <th>{ui.check3Tampons}</th>
                    <td style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                      {sel.trois_tampons === "oui" ? (
                        <><IconCheck size={15} className="ic-ok" /><span>{ui.tamponsComplete}</span></>
                      ) : sel.trois_tampons === "non" ? (
                        <><IconAlert size={15} className="ic-warn" /><span>{ui.tamponsMissing}</span></>
                      ) : (
                        <><IconClock size={15} className="ic-wait" /><span>{ui.tamponsPending}</span></>
                      )}
                    </td>
                  </tr>
                  <tr><th>{ui.registeredOwner}</th><td>{sel.proprietaire || "—"} ({sel.superficie_m2 || "—"} m²)</td></tr>
                  {sel.collectivite && <tr><th>{ui.customaryOrigin}</th><td>{sel.collectivite}</td></tr>}
                </tbody>
              </table>

              <h3 style={{ marginBottom: "6px" }}>{ui.securityChecks}</h3>
              <ul className="checks">
                {sel.checks.map((c) => (
                  <li key={c.label} className="check-row">
                    {c.ok ? <IconCheck size={16} className="ic-ok" /> : <IconAlert size={16} className="ic-warn" />}
                    <span>{translateCheckLabel(c.label, lang)}</span>
                  </li>
                ))}
              </ul>

              {sel.ventes && sel.ventes.length > 0 && (
                <>
                  <h4 style={{ margin: "10px 0 4px" }}>{ui.mutationHistory} ({sel.ventes.length})</h4>
                  <ul className="checks" style={{ fontSize: "13.5px" }}>
                    {sel.ventes.map((v, idx) => (
                      <li key={idx} className="check-row">
                        <IconCalendar size={15} />
                        <span><b>{v.date}</b> — {ui.buyerLabel} : <b>{v.acquereur}</b> {v.notaire ? `(${v.notaire})` : ""} [{v.statut}]</span>
                      </li>
                    ))}
                  </ul>
                </>
              )}

              <p className="notice"><b>{ui.recommendation} :</b> {translateAdvice(sel.score, sel.advice, lang)}</p>
            </>
          )}
        </div>
      </div>
    </section>
  );
}
