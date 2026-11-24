"use strict";

// Temas do portal NOCHAOS (Omarchy + Formal) no CTFd. Substitui o color_mode_switcher
// do core: roda no <head> para pintar o tema certo antes do primeiro frame, troca o
// botao sol/lua da navbar por um seletor e a tecla T alterna (Shift+T volta).
// A escolha fica no localStorage; ?tema=<id> na URL escolhe e salva um tema.
import palettes from "./nochaos/palettes.json";

const KEY = "nc-theme";
const root = document.documentElement;
const byId = Object.fromEntries(palettes.themes.map(t => [t.id, t]));

function rgb(hex) {
  const n = parseInt(hex.slice(1), 16);
  return `${(n >> 16) & 255}, ${(n >> 8) & 255}, ${n & 255}`;
}

function store(fn) {
  try {
    return fn(window.localStorage);
  } catch (e) {
    return null;
  }
}

function apply(id, persist) {
  const t = byId[id] || byId[palettes.default];
  for (const [k, v] of Object.entries(t.v)) {
    root.style.setProperty(`--nc-${k}`, v);
    root.style.setProperty(`--nc-${k}-rgb`, rgb(v));
  }
  const mode = t.mode === "light" ? "light" : "dark";
  root.setAttribute("data-nc-theme", t.id);
  root.setAttribute("data-bs-theme", mode);
  store(s => {
    if (persist) s.setItem(KEY, t.id);
    s.setItem("theme", mode);
  });
  const sel = document.getElementById("nc-theme-select");
  if (sel) sel.value = t.id;
  return t;
}

const asked = (location.search.match(/[?&]tema=([\w-]+)/) || [])[1];
if (asked && byId[asked]) apply(asked, true);
else apply(store(s => s.getItem(KEY)) || palettes.default, false);

window.ncTheme = { apply, themes: palettes.themes };

function picker() {
  const sel = document.getElementById("nc-theme-select");
  if (!sel || sel.options.length) return;
  for (const [mode, label] of [
    ["dark", sel.dataset.darkLabel || "Dark"],
    ["light", sel.dataset.lightLabel || "Light"],
  ]) {
    const group = document.createElement("optgroup");
    group.label = label;
    for (const t of palettes.themes.filter(t => (t.mode === "light") === (mode === "light"))) {
      const o = document.createElement("option");
      o.value = t.id;
      o.textContent = t.name;
      group.appendChild(o);
    }
    sel.appendChild(group);
  }
  sel.value = root.getAttribute("data-nc-theme");
  sel.addEventListener("change", () => apply(sel.value, true));
}

if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", picker);
else picker();

document.addEventListener("keydown", e => {
  if (e.key !== "t" && e.key !== "T") return;
  if (e.ctrlKey || e.metaKey || e.altKey) return;
  const el = e.target;
  if (el && (el.isContentEditable || /^(INPUT|TEXTAREA|SELECT)$/.test(el.tagName))) return;
  if (document.querySelector(".modal.show")) return;
  const ids = palettes.themes.map(t => t.id);
  const i = ids.indexOf(root.getAttribute("data-nc-theme"));
  apply(ids[(i + (e.shiftKey ? ids.length - 1 : 1)) % ids.length], true);
});
