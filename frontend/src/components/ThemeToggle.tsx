import { useEffect, useState } from "react";
import type { Lang } from "../api";
import { t } from "../i18n";
import { IconMoon, IconSun } from "./Icons";

type Theme = "light" | "dark";
function initial(): Theme {
  try { const th = localStorage.getItem("novissi-theme"); if (th === "light" || th === "dark") return th; } catch { /* ignoré */ }
  return window.matchMedia?.("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

export default function ThemeToggle({ lang = "Français" }: { lang?: Lang }) {
  const [theme, setTheme] = useState<Theme>(initial);
  const ui = t(lang);
  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    try { localStorage.setItem("novissi-theme", theme); } catch { /* ignoré */ }
  }, [theme]);
  return (
    <button
      type="button"
      className="side-btn"
      onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
      aria-label={theme === "dark" ? "Passer au thème clair" : "Passer au thème sombre"}
      style={{ display: "inline-flex", alignItems: "center", gap: "6px" }}
    >
      {theme === "dark" ? <IconSun size={15} /> : <IconMoon size={15} />}
      <span>{theme === "dark" ? ui.themeLight : ui.themeDark}</span>
    </button>
  );
}
