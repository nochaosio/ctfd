# Tema `nochaos`

Tema do CTFd com o visual do portal NOCHAOS (`nochaosio/nochaos`, `apps/portal`).
Base: o tema `core` do CTFd 3.8.9.

- **Fontes**: JetBrains Mono no texto e Geist nos títulos, as mesmas do portal. Servidas
  pelo próprio CTFd a partir de `static/webfonts` (via `@fontsource`), sem Google Fonts.
- **Cores**: o Bootstrap é compilado com a paleta padrão do portal (Kanagawa). Em runtime,
  os tokens `--nc-*` trocam a paleta por qualquer um dos 29 temas do portal (Omarchy + Formal).
- **Seletor de tema** na navbar, no lugar do sol/lua do `core`. A tecla **T** alterna
  (Shift+T volta), a escolha fica no `localStorage` e `?tema=<id>` na URL força um tema.
- **Visual**: cantos retos, superfícies planas com anel de 1px, rótulos em caixa alta
  espaçados, campo de pixels no hero e uma faixa de chama embaixo da navbar.

## Arquivos

| Arquivo | O quê |
|---|---|
| `assets/scss/includes/nochaos/_tokens.scss` | tokens `--nc-*` e o mapeamento para as variáveis do Bootstrap |
| `assets/scss/includes/nochaos/_look.scss` | navbar, hero, cards, tabelas, formulários, botões |
| `assets/scss/includes/utils/_fonts.scss` | `@font-face` da JetBrains Mono e da Geist |
| `assets/js/nochaos_theme.js` | aplica a paleta no `<head>`, seletor e tecla T (substitui o `color_mode_switcher`) |
| `assets/js/nochaos/palettes.json` | paletas geradas a partir do portal |
| `scripts/gen_palettes.py` | gera o `palettes.json` |

## Atualizar as paletas e compilar

```bash
cd CTFd/themes/nochaos
python3 scripts/gen_palettes.py ../../../../nochaos   # caminho do repo nochaos
npm install
npm run build                                          # escreve static/ (commitado)
```

## Usar

Escolha `nochaos` em Admin > Config > Theme (ou no `/setup`). A imagem Docker deste fork
(`docker build .`) já leva o tema.
