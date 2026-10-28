export type Lang = "Français" | "Ewé" | "Kabiyè";
export type UserAccount = { id: string; email: string; name: string; provider: string; ville: string };

export type Source = {
  id: number; ref: string; texte: string; kind: string; url: string;
  demo?: boolean; scope?: string; version_id?: number | null; sha256?: string | null; page?: number | null;
  collected?: string | null; verified?: boolean;
};
export type LegalHit = {
  resource_id: number; version_id: number; article_id: number; ref: string; article: string; texte: string;
  page: number | null; url: string; title: string | null; reference: string | null; text_type: string | null;
  doc_date: string | null; source_key: string; source: string; scope: string; sha256: string; collected: string;
  demo: boolean; verified: boolean;
};
export type LegalSearchOut = { hits: LegalHit[]; corpus_mode: string; note: string };
export type SourceInfo = { key: string; name: string; base_url: string; scope: string; resources: number; archived: number };
export type CollectionStatus = {
  corpus_mode: "officiel" | "demonstration" | "mixte"; indexed_chunks: number; sources: SourceInfo[];
  listing_pages_inspected: number; listing_pages_pending: number; resources_discovered: number;
  resources_by_status: Record<string, number>; documents_extracted: number; documents_not_extracted: number;
  versions_total: number; complete_within_scope: boolean; reasons_incomplete: string[]; note: string;
  last_run: { source_key: string; started_at: string; finished_at: string | null; status: string } | null;
  recent_changes: { resource_id: number; title: string | null; url: string; collected_at: string }[];
};

export type LetterKind =
  | "salaire"
  | "inspection_travail"
  | "licenciement_abusif"
  | "certificat_travail"
  | "bail"
  | "restitution_caution"
  | "preavis_locataire"
  | "opposition_fonciere"
  | "demande_etat_descriptif"
  | "mise_en_demeure_vendeur"
  | "plainte_procureur"
  | "reconnaissance_dette";

export type SuggestedLetter = { kind: LetterKind; label: string };

export type ChatOut = {
  answer: string;
  citations: Source[];
  mode: string;
  notice: string | null;
  suggested_letter?: SuggestedLetter | null;
};

export type Check = { label: string; ok: boolean; critical: boolean };
export type Score = "vert" | "orange" | "rouge";
export type VenteInfo = { date: string; acquereur: string; statut: string; notaire?: string };
export type Diag = {
  id: string; name: string; quartier: string; lot: string; ilot?: string;
  commune?: string; nature_terrain?: string; reference_titre?: string; requisition?: string;
  trois_tampons?: string; collectivite?: string; proprietaire?: string; superficie_m2?: number;
  ventes?: VenteInfo[];
  score: Score; checks: Check[]; advice: string; polygon: [number, number][]; center: [number, number];
  simulated: boolean; elapsed_ms: number;
};
export type Fields = {
  proprietaire?: string; acquereur?: string; superficie_m2?: number | null;
  lot?: string; ilot?: string; quartier?: string; reference_titre?: string;
  notaire?: string; trois_tampons?: string;
};
export type Clause = { extrait: string; risque: string; explication: string };
export type DecodeOut = {
  mode: "ia" | "regles"; resume: string; champs: Fields; clauses: Clause[];
  match: { status: "found" | "ambiguous" | "not_found"; parcel_id: string | null; candidates: string[] };
  terracheck: Diag | null; notice: string | null;
};

export type LetterIn = {
  kind: LetterKind;
  nom: string;
  adresse: string;
  telephone?: string;
  destinataire: string;
  ville: string;
  montant_fcfa?: number;
  periode?: string;
  reference_parcelle?: string;
  details: string;
  delai_jours: number;
};

export type LetterOut = {
  titre: string; texte: string; disclaimer: string; references: Source[];
  services: { nom: string; role: string; adresse: string }[];
};

export type Conversation = { id: string; title: string; created_at: number; updated_at: number };
export type StoredMessage = {
  id: number; role: "u" | "a"; text: string; sources: Source[];
  notice: string | null; mode: string | null; created_at: number;
  suggested_letter?: SuggestedLetter | null;
};

const ENV_BASE = (import.meta.env.VITE_API_BASE_URL as string | undefined)?.replace(/\/$/, "") || "/api";

export function currentUser(): UserAccount | null {
  try {
    const raw = localStorage.getItem("novissi-user");
    return raw ? (JSON.parse(raw) as UserAccount) : null;
  } catch { return null; }
}

export function setCurrentUser(u: UserAccount | null): void {
  try {
    if (u) {
      localStorage.setItem("novissi-user", JSON.stringify(u));
      localStorage.setItem("novissi-client-id", u.id);
    } else {
      localStorage.removeItem("novissi-user");
      localStorage.removeItem("novissi-client-id");
    }
  } catch { /* ignoré */ }
}

export function clientId(): string {
  try {
    const u = currentUser();
    if (u?.id) return u.id;
    let id = localStorage.getItem("novissi-client-id");
    if (!id) { id = crypto.randomUUID().replace(/-/g, ""); localStorage.setItem("novissi-client-id", id); }
    return id;
  } catch { return "anonyme-session-" + Math.random().toString(36).slice(2, 12); }
}

const withId = (init: RequestInit = {}): RequestInit => ({
  ...init, headers: { ...(init.headers as Record<string, string> | undefined), "X-Client-Id": clientId() },
});

async function call<T>(path: string, init?: RequestInit): Promise<T> {
  let r: Response;
  try {
    r = await fetch(ENV_BASE + path, init);
  } catch (e) {
    if ((e as Error).name === "AbortError") throw e;
    throw new Error("Impossible de joindre le serveur. Vérifiez votre connexion.");
  }
  if (!r.ok) {
    const e = await r.json().catch(() => ({}));
    const detail = typeof e.detail === "string" ? e.detail : "Une erreur est survenue. Vérifiez les champs et réessayez.";
    throw new Error(detail);
  }
  return r.json();
}

const json = (body: unknown): RequestInit => ({
  method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body),
});

export const chat = (message: string, lang: Lang) => call<ChatOut>("/chat", json({ message, lang }));
export const decode = (text: string, lang: Lang) => call<DecodeOut>("/decode", json({ text, lang }));
export const letter = (b: LetterIn) => call<LetterOut>("/documents", json(b));

export async function letterPdf(b: LetterIn): Promise<Blob> {
  const r = await fetch(ENV_BASE + "/documents/pdf", withId(json(b)));
  if (!r.ok) throw new Error("Impossible de générer le document PDF.");
  return r.blob();
}

export const parcels = () => call<Diag[]>("/terracheck");
export const ocr = (file: File) => {
  const f = new FormData();
  f.append("file", file);
  return call<{ text: string; confidence: number; needs_review: boolean }>("/ocr", { method: "POST", body: f });
};

export const oauthLogin = (provider: "google" | "apple" | "microsoft", email: string, name: string, ville = "Lomé") =>
  call<{ user: UserAccount }>("/auth/oauth", withId(json({ provider, email, name, ville })));

export const registerEmail = (email: string, name: string, password: string, ville = "Lomé") =>
  call<{ user: UserAccount }>("/auth/register", withId(json({ email, name, password, ville })));

export const listConversations = (q = "") => call<Conversation[]>("/conversations?q=" + encodeURIComponent(q), withId());
export const createConversation = () => call<Conversation>("/conversations", withId({ method: "POST" }));
export const conversationMessages = (id: string) => call<StoredMessage[]>(`/conversations/${id}/messages`, withId());
export const sendMessage = (id: string, message: string, lang: Lang, signal?: AbortSignal) =>
  call<ChatOut>(`/conversations/${id}/messages`, withId({ ...json({ message, lang }), signal }));
export const renameConversation = (id: string, title: string) =>
  call<{ ok: boolean }>(`/conversations/${id}`, withId({ method: "PATCH", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ title }) }));
export const deleteConversation = (id: string) => call<{ ok: boolean }>(`/conversations/${id}`, withId({ method: "DELETE" }));

export const legalSearch = (q: string, source = "") =>
  call<LegalSearchOut>(`/legal/search?q=${encodeURIComponent(q)}${source ? "&source=" + encodeURIComponent(source) : ""}`);
export const searchLegal = legalSearch;
export const collectionStatus = () => call<CollectionStatus>("/collection/status");
export const legalStatus = collectionStatus;
