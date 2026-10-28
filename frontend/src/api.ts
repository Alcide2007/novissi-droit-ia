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
export type ChatOut = { answer: string; citations: Source[]; mode: string; notice: string | null };
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
  proprietaire?: string; acquereur?: string; superficie_m2?: number; lot?: string; ilot?: string;
  quartier?: string; reference_titre?: string; notaire?: string; trois_tampons?: string;
};
export type Clause = { extrait: string; risque: string; explication: string };
export type DecodeOut = {
  mode: string; resume: string; champs: Fields; clauses: Clause[];
  match: { status: "found" | "ambiguous" | "not_found"; parcel_id: string | null; candidates: string[] };
  terracheck: Diag | null; notice: string | null;
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

export type LetterIn = {
  kind: LetterKind; nom: string; adresse: string; telephone?: string; destinataire: string; ville: string;
  montant_fcfa?: number; periode?: string; reference_parcelle?: string; details: string; delai_jours: number;
};

export type LetterOut = {
  titre: string; texte: string; disclaimer: string; references: Source[];
  services: { nom: string; role: string; adresse: string }[];
};

export type Conversation = { id: string; title: string; updated_at: string; message_count: number };
export type StoredMessage = {
  id: number; role: "u" | "a"; text: string; sources?: Source[]; notice?: string | null; mode?: string | null; created_at: string;
};

const BASE = import.meta.env.VITE_API_BASE_URL ?? "";

export function clientId(): string {
  const k = "novissi_client_id";
  let v = localStorage.getItem(k);
  if (!v) {
    const arr = new Uint8Array(12);
    crypto.getRandomValues(arr);
    v = "anon_" + Array.from(arr, (b) => b.toString(16).padStart(2, "0")).join("");
    localStorage.setItem(k, v);
  }
  return v;
}

export function currentUser(): UserAccount | null {
  try {
    const raw = localStorage.getItem("novissi_current_user");
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

export function setCurrentUser(u: UserAccount | null): void {
  if (u) localStorage.setItem("novissi_current_user", JSON.stringify(u));
  else localStorage.removeItem("novissi_current_user");
}

async function call<T>(path: string, init?: RequestInit): Promise<T> {
  const headers = new Headers(init?.headers ?? {});
  headers.set("X-Client-Id", clientId());
  const r = await fetch(`${BASE}${path}`, { credentials: "same-origin", ...init, headers });
  if (!r.ok) {
    let msg = `Erreur HTTP ${r.status}`;
    try {
      const j = await r.json();
      msg = j.detail ?? j.error ?? msg;
    } catch {
      /* texte brut */
    }
    throw new Error(msg);
  }
  return r.json();
}

const json = (data: unknown, method = "POST") => ({
  method,
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(data),
});

export const oauthLogin = (provider: "google" | "apple" | "microsoft", email: string, name: string, ville: string) =>
  call<{ user: UserAccount }>("/auth/oauth", json({ provider, email, name, ville }));

export const registerEmail = (email: string, name: string, password: string, ville: string) =>
  call<{ user: UserAccount }>("/auth/register", json({ email, name, password, ville }));

export const listConversations = (q = "") => call<Conversation[]>(`/conversations${q ? `?q=${encodeURIComponent(q)}` : ""}`);
export const createConversation = () => call<Conversation>("/conversations", { method: "POST" });
export const conversationMessages = (cid: string) => call<StoredMessage[]>(`/conversations/${cid}/messages`);
export const sendMessage = (cid: string, message: string, lang: Lang, signal?: AbortSignal) =>
  call<ChatOut>(`/conversations/${cid}/messages`, { ...json({ message, lang }), signal });
export const renameConversation = (cid: string, title: string) =>
  call<{ ok: boolean }>(`/conversations/${cid}`, json({ title }, "PATCH"));
export const deleteConversation = (cid: string) => call<{ ok: boolean }>(`/conversations/${cid}`, { method: "DELETE" });

export const ask = (message: string, lang: Lang, signal?: AbortSignal) =>
  call<ChatOut>("/chat", { ...json({ message, lang }), signal });

export const decode = (text: string, lang: Lang) => call<DecodeOut>("/decode", json({ text, lang }));
export const letter = (b: LetterIn) => call<LetterOut>("/documents", json(b));
export const parcels = () => call<Diag[]>("/terracheck");
export const ocr = (file: File) => {
  const f = new FormData();
  f.append("file", file);
  return call<{ text: string; confidence: number; needs_review: boolean }>("/ocr", { method: "POST", body: f });
};
export const searchLegal = (q: string, source?: string, scope?: string) => {
  const p = new URLSearchParams({ q });
  if (source) p.set("source", source);
  if (scope) p.set("scope", scope);
  return call<LegalSearchOut>(`/legal/search?${p}`);
};
export const legalStatus = () => call<CollectionStatus>("/collection/status");