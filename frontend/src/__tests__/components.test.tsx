import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";
import * as api from "../api";
import type { Source } from "../api";
import ChatMessage from "../components/ChatMessage";
import CitationList from "../components/CitationList";
import Markdown from "../components/Markdown";
import MessageComposer from "../components/MessageComposer";
import ThemeToggle from "../components/ThemeToggle";

afterEach(() => { cleanup(); vi.restoreAllMocks(); });

const src: Source = { id: 1, ref: "Journal Officiel - Article 5", texte: "Le salaire est payé.", kind: "loi", url: "https://jo.test/a.pdf",
  demo: false, scope: "national", version_id: 7, sha256: "abcdef0123456789", page: 3, collected: "2026-10-01", verified: false };

describe("Markdown sécurisé", () => {
  it("n'exécute pas de HTML dangereux et isole les liens", () => {
    const { container } = render(<Markdown text={'<script>alert(1)</script><img src=x onerror="alert(1)">\n\n[lien](https://exemple.tg)\n\n| a | b |\n|---|---|\n| 1 | 2 |'} />);
    expect(container.querySelector("script")).toBeNull();
    expect(container.querySelector("img")).toBeNull();
    const a = screen.getByRole("link", { name: "lien" });
    expect(a).toHaveAttribute("rel", expect.stringContaining("noopener"));
    expect(container.querySelector("table")).not.toBeNull();   // les tableaux sont rendus
  });
});

describe("MessageComposer", () => {
  it("Entrée envoie, Maj+Entrée saute une ligne, le champ n'est vidé qu'après le démarrage", async () => {
    const onSend = vi.fn().mockResolvedValue(true);
    render(<MessageComposer lang="Français" busy={false} onSend={onSend} onStop={() => {}} />);
    const box = screen.getByLabelText("Votre question");
    await userEvent.type(box, "Mon salaire{Shift>}{Enter}{/Shift}suite");
    expect(onSend).not.toHaveBeenCalled();
    expect(box).toHaveValue("Mon salaire\nsuite");
    await userEvent.type(box, "{Enter}");
    expect(onSend).toHaveBeenCalledWith("Mon salaire\nsuite");
    await waitFor(() => expect(box).toHaveValue(""));
  });
  it("ne vide pas le champ si l'envoi n'a pas démarré et désactive l'envoi à vide", async () => {
    const onSend = vi.fn().mockResolvedValue(false);
    render(<MessageComposer lang="Français" busy={false} onSend={onSend} onStop={() => {}} />);
    expect(screen.getByLabelText("Envoyer")).toBeDisabled();
    const box = screen.getByLabelText("Votre question");
    await userEvent.type(box, "question{Enter}");
    expect(box).toHaveValue("question");
  });
  it("affiche un bouton Arrêter pendant le chargement", () => {
    const onStop = vi.fn();
    render(<MessageComposer lang="Français" busy onSend={vi.fn()} onStop={onStop} />);
    fireEvent.click(screen.getByLabelText("Arrêter"));
    expect(onStop).toHaveBeenCalled();
  });
  it("permet de joindre une image et insère son texte OCR dans la question", async () => {
    vi.spyOn(api, "ocr").mockResolvedValue({ text: "Article 5. Le salaire est payé.", confidence: 92, needs_review: false });
    render(<MessageComposer lang="Français" busy={false} onSend={vi.fn()} onStop={() => {}} />);
    const file = new File(["fake image bytes"], "document.png", { type: "image/png" });
    await userEvent.upload(screen.getByLabelText("Choisir une image à joindre"), file);
    await waitFor(() => expect((screen.getByLabelText("Votre question") as HTMLTextAreaElement).value).toContain("Article 5"));
  });
});

describe("Sources et provenance", () => {
  it("affiche version, empreinte, page, date et statut non vérifié ; copie la référence", async () => {
    const writeText = vi.fn().mockResolvedValue(undefined);
    Object.assign(navigator, { clipboard: { writeText } });
    render(<CitationList sources={[src]} />);
    expect(screen.getByText("Sources juridiques")).toBeInTheDocument();
    expect(screen.getByText(/Version 7 \(empreinte abcdef01\)/)).toBeInTheDocument();
    expect(screen.getByText(/page 3/)).toBeInTheDocument();
    expect(screen.getByText(/statut juridique non vérifié/)).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Source d’origine" })).toHaveAttribute("href", "https://jo.test/a.pdf");
    await userEvent.click(screen.getByText("Copier la référence"));
    expect(writeText).toHaveBeenCalledWith("Journal Officiel - Article 5");
  });
  it("signale clairement les textes fictifs de démonstration", () => {
    render(<ChatMessage m={{ role: "a", text: "Réponse", mode: "extraits", sources: [{ ...src, demo: true, scope: "demo" }] }} />);
    expect(screen.getAllByText(/fictif/i).length).toBeGreaterThanOrEqual(2);
    expect(screen.getByText(/IA indisponible/)).toBeInTheDocument();
  });
  it("affiche le bouton Écouter la réponse pour les messages de l'assistant", () => {
    render(<ChatMessage m={{ role: "a", text: "Le salaire est payé [1].", mode: "ia", sources: [src] }} />);
    expect(screen.getByRole("button", { name: /Écouter la réponse/i })).toBeInTheDocument();
  });
  it("ne montre rien sans source", () => {
    const { container } = render(<CitationList sources={[]} />);
    expect(container).toBeEmptyDOMElement();
  });
});

describe("ThemeToggle", () => {
  it("bascule le thème sur <html> et le mémorise", async () => {
    localStorage.setItem("novissi-theme", "light");
    render(<ThemeToggle />);
    expect(document.documentElement.dataset.theme).toBe("light");
    await userEvent.click(screen.getByRole("button", { name: /thème sombre/i }));
    expect(document.documentElement.dataset.theme).toBe("dark");
    expect(localStorage.getItem("novissi-theme")).toBe("dark");
  });
});
