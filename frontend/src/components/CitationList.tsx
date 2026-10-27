import type { Lang, Source } from "../api";
import { t } from "../i18n";
import Provenance from "./Provenance";

export default function CitationList({ sources, lang = "Français" }: { sources: Source[]; lang?: Lang }) {
  if (!sources.length) return null;
  const ui = t(lang);
  return (
    <div className="sources">
      <h4>{ui.sourcesTitle}</h4>
      {sources.map((s) => (
        <details key={s.id}>
          <summary>{s.ref} {s.kind === "analyse" && <em>(analyse)</em>} {s.demo && <em className="badge-demo-inline">(fictif)</em>}</summary>
          <p>{s.texte}</p>
          <Provenance demo={s.demo} scope={s.scope} sha256={s.sha256} version_id={s.version_id} page={s.page}
            collected={s.collected} verified={s.verified} url={s.url} reference={s.ref} lang={lang} />
        </details>
      ))}
    </div>
  );
}
