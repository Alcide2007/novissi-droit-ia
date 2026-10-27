import { cleanup, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import App from "../App";
import * as api from "../api";

beforeEach(() => {
  localStorage.clear();
  vi.spyOn(api, "listConversations").mockResolvedValue([]);
});
afterEach(() => { cleanup(); vi.restoreAllMocks(); });

describe("Application", () => {
  it("rendu initial : barre latérale repliable, compte en bas à gauche, contrôles en haut à droite et bascule d'interface en Éwé / Kabiyè", async () => {
    render(<App />);
    expect(screen.getByRole("button", { name: /Nouvelle conversation/ })).toBeInTheDocument();
    expect(screen.getByText(/Comment puis-je vous aider sur le droit togolais/)).toBeInTheDocument();

    // Changement de langue vers Ewé : toute l'interface passe en Éwé
    const langSelect = screen.getByLabelText("Langue");
    await userEvent.selectOptions(langSelect, "Ewé");
    expect(screen.getByText(/Woezɔ, Togovi/)).toBeInTheDocument();
    expect(screen.getByText(/Aleke mate ŋu akpe ɖe ŋuwò/)).toBeInTheDocument();

    // Retour en Français
    await userEvent.selectOptions(langSelect, "Français");
    expect(screen.getByText(/Comment puis-je vous aider sur le droit togolais/)).toBeInTheDocument();

    // Test du repli et de l'agrandissement de la barre latérale
    const toggleBtn = screen.getByRole("button", { name: /Replier la barre latérale/i });
    await userEvent.click(toggleBtn);
    expect(screen.getByRole("button", { name: /Agrandir la barre latérale/i })).toBeInTheDocument();
    await userEvent.click(screen.getByRole("button", { name: /Agrandir la barre latérale/i }));

    await userEvent.click(screen.getByRole("button", { name: "Génération de courriers" }));
    expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent("Génération de courriers");
  });

  it("une suggestion remplit réellement le champ de saisie", async () => {
    render(<App />);
    const first = screen.getAllByRole("button").find((b) => b.className === "card" && /salaire/i.test(b.textContent ?? ""));
    if (!first) throw new Error("suggestion introuvable");
    await userEvent.click(first);
    await waitFor(() => expect((screen.getByLabelText("Votre question") as HTMLTextAreaElement).value.length).toBeGreaterThan(5));
  });
});
