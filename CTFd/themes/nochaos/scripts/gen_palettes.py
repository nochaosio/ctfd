#!/usr/bin/env python3
"""Gera assets/js/nochaos/palettes.json: as paletas do portal NOCHAOS (Omarchy + Formal).

    python3 scripts/gen_palettes.py [caminho/do/repo/nochaos]   # default: ../../../../nochaos
    npm run build                                              # recompila static/

Le apps/portal/src/lib/omarchy-themes.js e os FORMAL_THEMES de themes.js e reduz cada
tema aos tokens que o tema CTFd usa (--nc-*). O JSON gerado e commitado: compilar o
tema nao depende do repo nochaos.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "js" / "nochaos" / "palettes.json"


def hexrgb(h):
    h = h.lstrip("#")
    return [int(h[i:i + 2], 16) for i in (0, 2, 4)]


def tohex(c):
    return "#" + "".join(f"{max(0, min(255, round(v))):02x}" for v in c)


def mix(a, b, t):
    x, y = hexrgb(a), hexrgb(b)
    return tohex([p + (q - p) * t for p, q in zip(x, y)])


def lum(h):
    def ch(v):
        s = v / 255
        return s / 12.92 if s <= 0.03928 else ((s + 0.055) / 1.055) ** 2.4
    r, g, b = map(ch, hexrgb(h))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b):
    x, y = sorted([lum(a), lum(b)], reverse=True)
    return (x + 0.05) / (y + 0.05)


def hsl(h):
    r, g, b = (v / 255 for v in hexrgb(h))
    mx, mn = max(r, g, b), min(r, g, b)
    l = (mx + mn) / 2
    if mx == mn:
        return 0, 0, l
    d = mx - mn
    s = d / (2 - mx - mn) if l > 0.5 else d / (mx + mn)
    if mx == r:
        hh = ((g - b) / d + (6 if g < b else 0)) * 60
    elif mx == g:
        hh = ((b - r) / d + 2) * 60
    else:
        hh = ((r - g) / d + 4) * 60
    return hh, s, l


def in_band(h, band):
    a, b = band
    return a <= h <= b if a <= b else (h >= a or h <= b)


def signal(cands, band, fallback, bg):
    """Cor de status que continua significando o que deve (erro nunca verde), como o portal faz."""
    for c in cands:
        if not c or not re.fullmatch(r"#[0-9a-fA-F]{6}", c):
            continue
        h, s, l = hsl(c)
        if in_band(h, band) and s >= 0.35 and 0.25 <= l <= 0.85:
            return ensure(c, bg)
    return ensure(fallback, bg)


def ensure(fg, bg, minc=3.0):
    toward = "#ffffff" if lum(bg) < 0.4 else "#000000"
    c = fg
    for i in range(1, 11):
        if contrast(c, bg) >= minc:
            break
        c = mix(fg, toward, i / 10)
    return c


def site_tokens(t):
    """Tokens do omarchy.org quando o gerador do portal os achou; o que faltar é derivado da paleta."""
    c = t["colors"]
    dark = t["mode"] != "light"
    bg = c["background"]
    lift = "#ffffff" if dark else "#000000"
    lb = c.get("lighter_background") or mix(bg, lift, 0.08)
    derived = {
        "bg-deep": c.get("dark_background") or mix(bg, "#000000" if dark else "#ffffff", 0.25),
        "bg": bg, "surface": mix(bg, lb, 0.5), "surface-2": lb,
        "border-subtle": lb, "border-strong": c.get("muted") or mix(bg, lift, 0.3),
        "text": c.get("bright_foreground") or c["foreground"], "text-secondary": c["foreground"],
        "text-muted": c.get("dark_foreground") or mix(c["foreground"], bg, 0.35),
        "brand": c["accent"],
        "brand-ink": "#0c0e10" if contrast(c["accent"], "#0c0e10") >= contrast(c["accent"], "#ffffff") else "#ffffff",
        "selection": c.get("selection") or mix(bg, c["accent"], 0.2),
    }
    return {**derived, **(t.get("site") or {})}


def compact(t):
    c, s = t["colors"], site_tokens(t)
    bg = s["bg"]
    return {
        "id": t["id"], "name": t["name"], "mode": t["mode"],
        "v": {
            "bg-deep": s["bg-deep"], "bg": bg, "surface": s["surface"], "surface-2": s["surface-2"],
            "border": s["border-subtle"], "border-strong": s["border-strong"],
            "text": s["text"], "text-2": s["text-secondary"], "muted": s["text-muted"],
            "brand": s["brand"], "brand-ink": s["brand-ink"], "selection": s["selection"],
            "danger": signal([c.get("red"), c.get("bright_red")], (340, 20), "#e5484d", bg),
            "success": signal([c.get("green"), c.get("bright_green")], (75, 165), "#2fb67c", bg),
            "warning": signal([c.get("yellow"), c.get("bright_yellow"), c.get("orange")], (25, 60), "#e5a50a", bg),
            "info": signal([c.get("cyan"), c.get("blue"), c.get("bright_cyan")], (170, 240), "#4c8dff", bg),
        },
    }


def js_array(src, name):
    m = re.search(rf"export const {name}\s*=\s*(\[.*?\n\]);", src, re.S)
    if not m:
        sys.exit(f"não achei {name}")
    return m.group(1)


def formal_themes(src):
    """FORMAL_THEMES é JS literal (chaves sem aspas, spread de `signals`): converte para JSON."""
    signals = json.loads(re.sub(r"(\w+):", r'"\1":', re.search(r"const signals = (\{.*?\});", src).group(1)).replace("'", '"'))
    body = js_array(src, "FORMAL_THEMES")
    body = body.replace("...signals,", "")
    body = re.sub(r"//.*", "", body)
    body = body.replace("'", '"')
    body = re.sub(r"([{,]\s*)([A-Za-z_][\w]*)\s*:", r'\1"\2":', body)
    body = re.sub(r",\s*([}\]])", r"\1", body)
    out = json.loads(body)
    for t in out:
        t["colors"] = {**signals, **t["colors"]}
    return out


def main():
    nochaos = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT.parents[3] / "nochaos"
    lib = nochaos / "apps" / "portal" / "src" / "lib"
    om_src = (lib / "omarchy-themes.js").read_text()
    default = re.search(r'DEFAULT_THEME = "([^"]+)"', om_src).group(1)
    themes = json.loads(js_array(om_src, "OMARCHY_THEMES"))
    themes += formal_themes((lib / "themes.js").read_text())
    data = [compact(t) for t in themes]
    data.sort(key=lambda t: (t["id"] != default, t["mode"] != "dark", t["name"].lower()))
    OUT.write_text(json.dumps({"default": default, "themes": data}, indent=1, ensure_ascii=False) + "\n")
    print(f"{OUT.relative_to(ROOT)}: {len(data)} temas, default {default}")


if __name__ == "__main__":
    main()
