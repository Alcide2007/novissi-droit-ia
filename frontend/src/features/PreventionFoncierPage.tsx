import { useState } from "react";
import type { Lang, LetterKind } from "../api";
import { IconCheck, IconLetter, IconTerra } from "../components/Icons";

type Step = {
  num: number;
  title: Record<Lang, string>;
  lawRef: string;
  desc: Record<Lang, string>;
  danger: Record<Lang, string>;
  actionView?: "terra" | "acte" | "docs";
  actionLabel?: Record<Lang, string>;
  letterKind?: LetterKind;
};

const STEPS: Step[] = [
  {
    num: 1,
    title: {
      Français: "Exiger le numéro du Titre Foncier (TF) ou de la Réquisition d’Immatriculation",
      Ewé: "Bia Titre Foncier (TF) alo Réquisition ƒe xexlẽdzesi le OTR",
      Kabiyè: "Pɔzɩ Titre Foncier (TF) ñʊʊ OTR Cadastre taa",
    },
    lawRef: "Art. 142 & 175 — Code foncier (Loi n° 2018-005)",
    desc: {
      Français: "Demandez la copie du Titre Foncier et vérifiez son authenticité au guichet du Cadastre et de la Conservation Foncière de l’OTR avant tout engagement.",
      Ewé: "Bia Titre Foncier ƒe kopie eye nàdo eƒe nyateƒetoto kpɔ le OTR Cadastre hafi nàwɔ ɖoɖo aɖeke.",
      Kabiyè: "Pɔzɩ Titre Foncier takayaɣ nɛ na-cɔnɩ OTR Cadastre taa se pɩkɛ toovenim.",
    },
    danger: {
      Français: "Ne vous fiez jamais à un simple « reçu de vente » ou à la parole d’un démarcheur.",
      Ewé: "Megaɖo dzi ɖe gaƒleƒe ƒe agbalẽvi (reçu) alo démarcheur ƒe nya ɖeɖe dzi o.",
      Kabiyè: "Taatɩŋna liidiye takayaɣ kɩbɩnaɣ yem yɔɔ.",
    },
    actionView: "docs",
    actionLabel: {
      Français: "Générer une demande d’état descriptif OTR",
      Ewé: "Ŋlɔ agbalẽ bia anyigba ƒe nɔnɔme le OTR",
      Kabiyè: "Ma OTR takayaɣ nɛ na-cɔnɩ tɛtʊ wɛtʊ",
    },
    letterKind: "demande_etat_descriptif",
  },
  {
    num: 2,
    title: {
      Français: "Contrôler la validation technique « 3 Tampons » (Lotissement approuvé)",
      Ewé: "Do « Kpeɖodzi 3 (3 Tampons) » kpɔ le anyigba ƒe tata (plan) dzi",
      Kabiyè: "Cɔnɩ « 3 Tampons » tɛtʊ tata (plan) yɔɔ",
    },
    lawRef: "Décret n° 2019-033/PR sur les lotissements",
    desc: {
      Français: "Exigez le plan parcellaire géo-référencé portant les 3 visas : 1) Géomètre agréé, 2) Chef traditionnel / Mairie, et 3) Le visa technique de la Direction du Cadastre (OTR) qui bloque les doubles ventes.",
      Ewé: "Kpɔ egbɔ be kpeɖodzi 3 le plan la dzi : 1) Géomètre, 2) Fia alo Mairie, kple 3) OTR Cadastre ƒe kpeɖodzi si xea mɔ na anyigba dzradzra zi eve.",
      Kabiyè: "Cɔnɩ se tampons 3 wɛ plan yɔɔ : Géomètre, Mairie nɛ OTR Cadastre.",
    },
    danger: {
      Français: "Un plan avec seulement 1 ou 2 tampons sans le visa final de l’OTR expose au risque élevé de double vente.",
      Ewé: "Plan si dzi OTR ƒe kpeɖodzi mele o la ate ŋu ahe anyigba dzradzra zi eve vɛ.",
      Kabiyè: "OTR tampon fɛyɩ yɔ, papɩzɩɣ pɛpɛdɩ tɛtʊ nabʊlɛ.",
    },
    actionView: "terra",
    actionLabel: {
      Français: "Vérifier une parcelle sur TerraCheck",
      Ewé: "Do anyigba kpɔ le TerraCheck dzi",
      Kabiyè: "Cɔnɩ tɛtʊ TerraCheck tata yɔɔ",
    },
  },
  {
    num: 3,
    title: {
      Français: "Vérifier le Mandat Familial et le Procès-Verbal de Conseil de Famille",
      Ewé: "Do Ƒomea ƒe Mɔɖegbalẽ (PV de Conseil de Famille) kpɔ",
      Kabiyè: "Cɔnɩ ɖɩɣa tɩnaa nɔɔ kpɛndʊʊ takayaɣ",
    },
    lawRef: "Art. 166 & 532 — Code foncier & Code de la famille",
    desc: {
      Français: "Si le terrain appartient à une collectivité familiale ou à une succession, exigez le PV de conseil de famille homologué au tribunal et signé par tous les cohéritiers majeurs.",
      Ewé: "Ne ƒome ƒe anyigbae la, bia ƒomea ƒe takpekpe ƒe agbalẽ si dzi domenyilawo katã de asie le ʋɔnudrɔ̃ƒe.",
      Kabiyè: "Yee pɩkɛ ɖɩɣa tɛtʊ, pɔzɩ ɖɩɣa tɩnaa tɩŋa nesi sɩʊ takayaɣ.",
    },
    danger: {
      Français: "60 % des litiges fonciers au Togo viennent d’un terrain familial vendu par un seul héritier sans l’accord des autres.",
      Ewé: "Anyigbadzre 60% le Togo tsoa ƒome ƒe anyigba si ame ɖeka dzra le bubuawo ƒe manyamanya me gbɔ.",
      Kabiyè: "Tɛtʊ you 60% Togo taa lɩɣna ɛyʊ kʊyʊm pɛdʊʊ.",
    },
    actionView: "acte",
    actionLabel: {
      Français: "Analyser les clauses de l’acte",
      Ewé: "Do agbalẽa ƒe nyawo kpɔ",
      Kabiyè: "Cɔnɩ takayaɣ taa tɔm",
    },
  },
  {
    num: 4,
    title: {
      Français: "S’assurer que la parcelle n’est pas une Réserve Administrative de l’État",
      Ewé: "Kpɔ egbɔ be menye Dziɖuɖu ƒe Anyigba (Réserve Administrative) o",
      Kabiyè: "Cɔnɩ se pɩtɛkɛ Komina tɛtʊ (Réserve Administrative)",
    },
    lawRef: "Code de l’urbanisme & Domaine public",
    desc: {
      Français: "Vérifiez auprès de la Mairie et du ministère de l’Urbanisme que le lot n’est pas réservé à une route, une école, un marché ou un bassin de rétention d’eau.",
      Ewé: "Bia Mairie kple Urbanisme be womedzra anyigba la ɖo na mɔɖoɖo, suku alo tsiƒoƒe o.",
      Kabiyè: "Pɔzɩ Mairie se pɩtɛkɛ sukuli yaa habɩyɛ lone.",
    },
    danger: {
      Français: "Une réserve administrative est inaliénable : toute construction peut être démolie sans indemnisation.",
      Ewé: "Womeƒlea dziɖuɖu ƒe anyigba o : woate ŋu agbã xɔ si nètu ɖe edzi.",
      Kabiyè: "Komina tɛtʊ yɔɔ xɔʊ kɛ kʊñɔŋ.",
    },
  },
  {
    num: 5,
    title: {
      Français: "Faire une descente sur le terrain et une enquête de voisinage",
      Ewé: "Yi anyigbaa dzi kple Géomètre eye nàbia aƒelikawo",
      Kabiyè: "Wolo tɛtʊ yɔɔ nɛ na-pɔzɩ kpaɣdɛ tɩnaa",
    },
    lawRef: "Principe du bornage contradictoire",
    desc: {
      Français: "Déplacez-vous sur la parcelle avec un géomètre agréé pour vérifier les bornes et interrogez les voisins directs ainsi que le chef du quartier sur l’histoire du terrain.",
      Ewé: "Yi anyigbaa dzi kple géomètre eye nàbia aƒelikawo kple nutomefia be nya aɖe le anyigbaa ŋu mahã.",
      Kabiyè: "Wolo tɛtʊ yɔɔ nɛ géomètre nɛ na-pɔzɩ egeetiye ñʊʊdʊ.",
    },
    danger: {
      Français: "Les inscriptions « Terrain litigieux — Pas à vendre » sont parfois effacées juste avant la visite.",
      Ewé: "Ame aɖewo tutua nuŋlɔɖi « Anyigba sia mele dzradzram o » le gliwo ŋu.",
      Kabiyè: "Nabɛyɛ lɩzɩɣ « Tɛtʊ fɛyɩ pɛdʊʊ » takayɩsɩ.",
    },
  },
  {
    num: 6,
    title: {
      Français: "Passer obligatoirement devant un Notaire (Aucun paiement en espèces)",
      Ewé: "De asi agbalẽa te le Notaire ŋkume (Megaxe ga le asi me o)",
      Kabiyè: "Wolo Notaire cɔlɔ (Taahɛyɩ liidiye nesi taa)",
    },
    lawRef: "Art. 166 — Loi n° 2018-005 (Acte authentique obligatoire)",
    desc: {
      Français: "Toute vente immobilière au Togo doit être établie par acte authentique devant un Notaire inscrit à la Chambre Nationale des Notaires, avec paiement traçable.",
      Ewé: " le Togo ƒe se nu la, Notaire gbɔ koe wodea asi anyigbaƒlegbalẽ te le.",
      Kabiyè: "Togo paɣtʊ taa lɛ, Notaire cɔlɔ pamaɣ tɛtʊ pɛdʊʊ takayaɣ.",
    },
    danger: {
      Français: "Un acte sous seing privé (simple papier signé entre vendeur et acheteur) ne transfère pas la propriété.",
      Ewé: "Agbalẽ si womeŋlɔ le Notaire gbɔ o la mena anyigbatɔnyenye blibo o.",
      Kabiyè: "Takayaɣ ŋga katatɩŋna Notaire yɔ, kafɛyɩ ɖoŋ.",
    },
  },
  {
    num: 7,
    title: {
      Français: "Faire inscrire immédiatement la mutation au Livre Foncier de l’OTR",
      Ewé: "Na woaŋlɔ wò ŋkɔ ɖe OTR ƒe Agbalẽ Gã (Livre Foncier) me",
      Kabiyè: "Sɩɩ ña-hɩɖɛ OTR Livre Foncier takayaɣ taa",
    },
    lawRef: "Art. 180 — Opposabilité aux tiers par l’inscription",
    desc: {
      Français: "Veillez à ce que le notaire dépose le dossier à l’OTR pour la mutation du Titre Foncier à votre nom. Si le vendeur bloque la remise des pièces, formez opposition ou mettez-le en demeure.",
      Ewé: "Kpɔ egbɔ be woŋlɔ wò ŋkɔ ɖe Titre Foncier la dzi le OTR. Ne nudzrala gbe agbalẽwo nana la, ŋlɔ mise en demeure nɛ.",
      Kabiyè: "Cɔnɩ se pasɩɩ ña-hɩɖɛ OTR taa. Yee pɛdɩyʊ ekiziɣ, ma-ɩ takayaɣ.",
    },
    danger: {
      Français: "Tant que la mutation n’est pas inscrite à l’OTR, un vendeur malhonnête peut revendre le terrain à un tiers.",
      Ewé: "Ne wò ŋkɔ medze le OTR o la, nudzrala ate ŋu agadzrae na ame bubu.",
      Kabiyè: "Ña-hɩɖɛ fɛyɩ OTR taa yɔ, papɩzɩɣ pɛpɛdɩ lɛlʊ.",
    },
    actionView: "docs",
    actionLabel: {
      Français: "Mise en demeure au vendeur de terrain",
      Ewé: "Ŋlɔ agbalẽ sẽŋu na nudzrala",
      Kabiyè: "Ma tɛtʊ pɛdɩyʊ takayaɣ",
    },
    letterKind: "mise_en_demeure_vendeur",
  },
];

type Props = {
  lang?: Lang;
  onNavigate: (view: "terra" | "acte" | "docs", letterKind?: LetterKind) => void;
};

export default function PreventionFoncierPage({ lang = "Français", onNavigate }: Props) {
  const [checked, setChecked] = useState<Record<number, boolean>>({});

  function toggle(n: number) {
    setChecked((prev) => ({ ...prev, [n]: !prev[n] }));
  }

  const doneCount = Object.values(checked).filter(Boolean).length;
  const pct = Math.round((doneCount / STEPS.length) * 100);

  const headerTitle = {
    Français: "Guide de Prévention : Les 7 étapes indispensables avant d’acheter un terrain au Togo",
    Ewé: "Mɔfiafia : Afɔɖeɖe 7 siwo hiã hafi nàƒle anyigba le Togo",
    Kabiyè: "Lɔŋ tasɩtʊ : Mbʊ pʊwɛɛ se na-la (7) pʊcɔ na-ya tɛtʊ Togo taa",
  }[lang];

  const headerSub = {
    Français: "Cochez chaque vérification accomplie avant de verser le moindre acompte (Loi n° 2018-005 portant Code foncier et domanial).",
    Ewé: "De dzesi afɔɖeɖe siawo katã hafi nàxe ga aɖeke (Togo ƒe Anyigbase Loi n° 2018-005).",
    Kabiyè: "Cɔnɩ tɔm tʊnɛ tɩ-tɩŋa pʊcɔ nɛ na-hɛyɩ liidiye (Loi n° 2018-005).",
  }[lang];

  return (
    <section className="panel">
      <div className="row" style={{ justifyContent: "space-between", marginTop: 0 }}>
        <div style={{ flex: 1, minWidth: "240px" }}>
          <h2 style={{ margin: "0 0 4px", fontSize: "18px" }}>{headerTitle}</h2>
          <p className="muted" style={{ margin: 0 }}>{headerSub}</p>
        </div>
        <div className={"score " + (pct === 100 ? "vert" : pct >= 50 ? "orange" : "rouge")} style={{ fontSize: "13.5px", padding: "6px 14px" }}>
          {doneCount}/7 ({pct} %)
        </div>
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: "12px", marginTop: "16px" }}>
        {STEPS.map((s) => {
          const isDone = Boolean(checked[s.num]);
          return (
            <div
              key={s.num}
              className="card"
              style={{
                flexDirection: "column",
                alignItems: "stretch",
                borderLeft: `5px solid ${isDone ? "#2E8B57" : "var(--pr)"}`,
                background: isDone ? "rgba(46, 139, 87, 0.06)" : "var(--card)",
              }}
            >
              <div className="row" style={{ justifyContent: "space-between", marginTop: 0 }}>
                <label style={{ display: "flex", flexDirection: "row", alignItems: "center", gap: "10px", margin: 0, cursor: "pointer", flex: 1 }}>
                  <input
                    type="checkbox"
                    checked={isDone}
                    onChange={() => toggle(s.num)}
                    style={{ width: "20px", height: "20px", accentColor: "#2E8B57", flex: "none" }}
                  />
                  <span style={{ fontSize: "15px", fontWeight: 700 }}>
                    {s.num}. {s.title[lang]}
                  </span>
                </label>
                <span className="chip" style={{ fontSize: "11px", padding: "3px 10px" }}>{s.lawRef}</span>
              </div>

              <p style={{ margin: "6px 0 4px", fontSize: "14px", lineHeight: 1.5 }}>{s.desc[lang]}</p>
              <p className="notice" style={{ margin: "4px 0" }}>
                <b>⚠️ :</b> {s.danger[lang]}
              </p>

              {s.actionView && s.actionLabel && (
                <div className="row" style={{ marginTop: "6px" }}>
                  <button
                    type="button"
                    className="btn ghost"
                    style={{ padding: "7px 14px", fontSize: "13px", display: "inline-flex", alignItems: "center", gap: "6px" }}
                    onClick={() => onNavigate(s.actionView!, s.letterKind)}
                  >
                    {s.actionView === "docs" ? <IconLetter size={15} /> : s.actionView === "terra" ? <IconTerra size={15} /> : <IconCheck size={15} />}
                    <span>{s.actionLabel[lang]}</span>
                  </button>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </section>
  );
}
