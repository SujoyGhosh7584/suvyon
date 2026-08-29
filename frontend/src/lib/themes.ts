export const THEME_STORAGE_KEY = "suvyon_theme";

export const THEMES = [
  { id: "midnight", label: "Midnight", hint: "Deep indigo night" },
  { id: "dawn", label: "Dawn", hint: "Soft lavender light" },
  { id: "ocean", label: "Ocean", hint: "Teal and cyan" },
  { id: "forest", label: "Forest", hint: "Moss and pine" },
  { id: "ember", label: "Ember", hint: "Warm amber glow" },
] as const;

export type ThemeId = (typeof THEMES)[number]["id"];

export const DEFAULT_THEME: ThemeId = "midnight";

export function isThemeId(value: string | null): value is ThemeId {
  return THEMES.some((theme) => theme.id === value);
}

export function applyTheme(theme: ThemeId) {
  document.documentElement.dataset.theme = theme;
}

export function readStoredTheme(): ThemeId {
  try {
    const stored = localStorage.getItem(THEME_STORAGE_KEY);
    if (isThemeId(stored)) return stored;
  } catch {
    /* private mode */
  }
  return DEFAULT_THEME;
}
