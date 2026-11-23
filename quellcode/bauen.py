# Baut die lokale, eigenständige Fassung des Labor-KPI-Dashboards (eine HTML-Datei, lädt daneben daten.js).
import re, sys
LOGO = '<svg class="marke-logo" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 211.1 23.2" role="img" aria-label="Thomas Labor"><title>Thomas Labor</title><path fill="#00a984" d="M128.3,16.9c0-1.5-.6-2.6-1.6-3.4-.4-.3-1.6-.9-3.5-1.7-1.2-.5-1.7-1.1-1.7-1.8s.7-1.4,1.6-1.4,1.7.5,2.3,1.5l2.4-2c-1-1.5-2.6-2.3-4.6-2.3s-2.5.4-3.4,1.2c-1,.8-1.5,1.9-1.5,3.1,0,2,1.1,3.4,3.3,4.4.7.3,1.5.6,2.2.9.9.5,1.4,1,1.4,1.6s-.2.9-.6,1.2c-.4.3-.9.4-1.5.4-.9,0-1.9-.7-2.8-2l-2.6,1.7c1.3,2,3.1,2.9,5.2,2.9s2.8-.4,3.9-1.2c1.1-.8,1.6-1.9,1.6-3.2M112.6,13.4c0,1.4-.3,2.6-1,3.5-.7,1-1.8,1.6-3.2,1.6s-2.2-.5-2.9-1.3c-.7-.9-1-2-1-3.5s.3-2.5,1-3.4c.7-1,1.8-1.5,3.1-1.5s2.2.5,2.9,1.3c.7.9,1.1,2,1.1,3.3M115.8,6.2h-3.1v1.9c-.4-.7-1-1.2-1.9-1.6-.9-.4-1.8-.6-2.9-.6-2.2,0-3.9.8-5.2,2.3-1.2,1.4-1.8,3.2-1.8,5.4s.6,4.1,1.9,5.5c1.3,1.5,3,2.2,5.1,2.2s2.4-.3,3.4-.9c.6-.4,1.1-.9,1.4-1.4v2h3.1V6.2ZM98.9,9.9c0-1.3-.5-2.4-1.4-3.2-.9-.7-2-1.1-3.4-1.1s-1.7.2-2.5.6c-.8.4-1.4,1-1.8,1.7-.2-.7-.8-1.2-1.6-1.6-.7-.4-1.5-.6-2.3-.6s-1.6.2-2.3.6c-.8.4-1.3.9-1.7,1.6v-1.6h-3v14.8h3.3v-9.6c0-.7.3-1.4.9-2,.6-.6,1.3-.9,2-.9s1.4.2,1.7.6c.3.4.4,1,.4,1.8v10.2h3.3v-9.6c0-.8.3-1.5.8-2.1.6-.6,1.3-.9,2.1-.9,1.4,0,2.2.9,2.2,2.8v9.8h3.3v-11.1ZM73.6,13.6c0,1.3-.4,2.4-1.2,3.2-.8.9-1.9,1.4-3.3,1.4s-2.4-.5-3.2-1.4c-.8-.9-1.2-2-1.2-3.3s.4-2.4,1.2-3.3c.8-.9,1.9-1.4,3.2-1.4s2.6.5,3.4,1.4c.7.9,1.1,2,1.1,3.3M77,13.6c0-2.2-.7-4-2.2-5.5-1.5-1.5-3.4-2.3-5.6-2.3s-4,.7-5.6,2.3c-1.5,1.5-2.3,3.3-2.3,5.5s.8,4.2,2.3,5.6c1.5,1.4,3.4,2.1,5.6,2.1s4.3-.7,5.7-2.3c1.4-1.4,2.1-3.3,2.1-5.5M59.2,10.5c0-1.5-.5-2.7-1.4-3.5-.9-.8-2.1-1.2-3.7-1.2s-1.6.2-2.4.5c-.9.4-1.5.8-1.9,1.5V2.1h-3.4v18.8h3.3v-8.1c0-1.2.3-2.2.8-2.9.6-.8,1.5-1.2,2.8-1.2s2.6.9,2.6,2.7v9.6h3.2v-10.4ZM44.5,2.1h-11.1v3.2h3.8v15.6h3.5V5.3h3.8v-3.2Z"/><rect fill="currentColor" x="7.1" y="11.7" width="21.8" height="1"/><rect fill="#00a984" x="2.2" y="8.9" width="21.8" height="1"/><rect fill="#00a984" x="7.1" y="6.2" width="12" height="1"/><rect fill="currentColor" x="7.1" y="14.5" width="21.8" height="1"/><rect fill="#00a984" x="2.2" y="17.2" width="21.8" height="1"/><rect fill="#00a984" x="7.1" y="20" width="12" height="1"/><rect x="135.2" y="2.1" width="0.6" height="18.8" fill="#00a984"/><path fill="currentColor" d="M143.85 20.95H154.85V18.85H146.22V2.32H143.85ZM161.71 21.27C164.07 21.27 165.38 20.04 165.86 19.05H166.01V20.95H168.22V11.74C168.22 7.37 164.86 6.8 162.98 6.8C160.82 6.8 158.42 7.57 157.34 10.11L159.51 10.82C159.94 9.85 161.03 8.77 163.04 8.77C164.98 8.77 165.97 9.77 165.97 11.51V11.59C165.97 12.62 164.87 12.55 162.38 12.86C159.79 13.19 156.94 13.77 156.94 16.97C156.94 19.72 159.06 21.27 161.71 21.27ZM162.09 19.29C160.42 19.29 159.21 18.54 159.21 17.09C159.21 15.5 160.64 14.97 162.28 14.76C163.14 14.65 165.59 14.4 165.97 13.96V15.9C165.97 17.61 164.58 19.29 162.09 19.29ZM178.4 21.25C181.89 21.25 184.31 18.45 184.31 14C184.31 9.57 181.88 6.8 178.39 6.8C175.66 6.8 174.8 8.47 174.34 9.21H174.16V2.32H171.91V20.95H174.09V18.79H174.34C174.8 19.56 175.74 21.25 178.4 21.25ZM178.06 19.24C175.53 19.24 174.14 17.09 174.14 13.97C174.14 10.89 175.49 8.81 178.06 8.81C180.71 8.81 182.03 11.07 182.03 13.97C182.03 16.91 180.68 19.24 178.06 19.24ZM193.02 21.25C196.83 21.25 199.41 18.36 199.41 14.05C199.41 9.67 196.83 6.8 193.02 6.8C189.22 6.8 186.66 9.67 186.66 14.05C186.66 18.36 189.22 21.25 193.02 21.25ZM193.02 19.24C190.23 19.24 188.94 16.8 188.94 14.05C188.94 11.26 190.23 8.81 193.02 8.81C195.84 8.81 197.13 11.27 197.13 14.05C197.13 16.8 195.84 19.24 193.02 19.24ZM202.43 20.95H204.68V12.2C204.68 10.31 206.15 8.95 208.16 8.95C208.76 8.95 209.38 9.05 209.51 9.07V6.81C209.25 6.8 208.7 6.77 208.38 6.77C206.71 6.77 205.26 7.71 204.75 9.12H204.6V6.97H202.43Z"/></svg>'
from pathlib import Path

L = Path(__file__).resolve().parent            # Ordner quellcode
OUT = L.parent / 'dashboard' / 'Labor-KPI-Dashboard.html'
src = (L / 'vorlage.html').read_text(encoding='utf-8')


def rep(s, old, new, alle=False):
    n = s.count(old)
    assert n >= 1 and (alle or n == 1), (n, old[:60])
    return s.replace(old, new)


# --- Stil -------------------------------------------------------------------------------------
css = re.search(r'<style>(.*?)</style>', src, re.S).group(1)
css += '''
.lk .tabs { display: flex; flex-wrap: wrap; gap: var(--cds-gap-xs); border-bottom: 1px solid var(--color-border-line); }
.lk .tabs button { font: inherit; color: var(--color-fg-muted); background: none; border: 0; border-bottom: 2px solid transparent; margin-bottom: -1px; padding: var(--cds-pad-sm) var(--cds-pad-md); cursor: pointer; }
.lk .tabs button[aria-selected=true] { color: var(--color-fg); border-bottom-color: var(--color-fg); font-weight: var(--cds-font-weight-medium); }
.lk .tab { display: flex; flex-direction: column; gap: var(--cds-gap-xl); }
.lk .tab[hidden] { display: none; }
.lk .chart.kw { min-height: 210px; }
.lk .legend { flex-wrap: wrap; }
.lk .legend i.muted { background: var(--cds-chart-muted); }
'''
css += '''
.lk .chart[data-draw] { padding-top: 26px; }
.lk .lk-voll-btn { position: absolute; top: 0; right: 0; font: inherit; font-size: var(--cds-font-size-caption); color: var(--color-fg-muted); background: none; border: 1px solid var(--color-border-line); border-radius: 6px; padding: 2px 8px; cursor: pointer; }
.lk .lk-voll-btn:hover { color: var(--color-fg); }
.lk .chart svg .lk-werte text { font-size: 11px; paint-order: stroke; stroke: var(--color-panel); stroke-width: 3px; stroke-linejoin: round; }
.lk .chart svg .lk-werte text.innen { fill: #fff; stroke: none; }
.lk .card.lk-voll { position: fixed; inset: 0; z-index: 2147483000; margin: 0; border: 0; border-radius: 0; overflow: auto; display: flex; flex-direction: column; background: var(--color-panel); padding: 24px 32px; box-sizing: border-box; }
.lk .card.lk-voll .chart { flex: 1 1 auto; min-height: 0; }
'''
css += '''
.lk { --lk-marke: #00a984; }
.lk #kopf { border-top: 4px solid var(--lk-marke); padding-top: var(--cds-pad-md); }
.lk .marke { color: var(--color-fg); margin-bottom: var(--cds-gap-md); }
.lk .marke-logo { display: block; height: 34px; width: auto; max-width: 100%; }
.lk .tabs button[aria-selected=true] { border-bottom-color: var(--lk-marke); }
.lk h3 { font-size: var(--cds-font-size-body); font-weight: var(--cds-font-weight-medium); margin: 0 0 calc(-1 * var(--cds-gap-md)); color: var(--color-fg-muted); }
.lk .tiles.gross .tile .val { font-size: 2.6rem; }
.lk .tile .soll { font-size: var(--cds-font-size-caption); color: var(--color-fg-muted); }
.lk .tile[data-ziel], .lk .tile[data-liste] { cursor: pointer; transition: border-color .15s; }
.lk .tile[data-ziel]:hover, .lk .tile[data-liste]:hover, .lk .tile[data-ziel]:focus-visible, .lk .tile[data-liste]:focus-visible { border-color: var(--lk-marke); outline: none; }
.lk .tile .val.good { color: var(--color-ok); } .lk .tile .val.bad { color: var(--color-bad); }
.lk .subnav { display: flex; flex-wrap: wrap; gap: var(--cds-gap-sm); }
.lk .subnav button { font: inherit; font-size: var(--cds-font-size-caption); color: var(--color-fg); background: var(--color-panel); border: 1px solid var(--color-border-line); border-radius: 999px; padding: 4px 12px; cursor: pointer; }
.lk .subnav button:hover { border-color: var(--lk-marke); }
.lk section.tab + section.tab:not([hidden]) { border-top: 1px solid var(--color-border-line); padding-top: var(--cds-gap-xl); }
.lk td.spark { padding-top: 2px; padding-bottom: 2px; }
.lk td.spark svg { display: block; margin-left: auto; }
.lk .chart svg text.lk-ref { font-size: 11px; paint-order: stroke; stroke: var(--color-panel); stroke-width: 3px; }
.lk .hinweis { font-size: var(--cds-font-size-caption); color: var(--color-fg-muted); border-left: 3px solid var(--lk-marke); padding: 2px 0 2px 10px; margin: 0; }
@media print {
  .lk .tabs, .lk .subnav, .lk .lk-voll-btn, .lk .tip, .lk .fuss { display: none !important; }
  .lk section.tab { break-before: page; border-top: 0 !important; padding-top: 0 !important; }
  .lk section.tab:first-of-type { break-before: auto; }
  .lk .card, .lk .tile, .lk tr { break-inside: avoid; }
  .lk .tw { overflow: visible; }
}
'''
tokens = '''
:root {
  color-scheme: light dark;
  --color-fg: #1c1b19; --color-fg-muted: #6b6963; --color-bg: #faf9f6; --color-panel: #ffffff; --color-border-line: #e3e0d8;
  --color-ok: #1f8a4c; --color-warn: #b7791f; --color-bad: #c0392b;
  --font-anthropic-sans: "Segoe UI", system-ui, -apple-system, Roboto, Arial, sans-serif; --font-anthropic-serif: Georgia, "Times New Roman", serif;
  --cds-font-size-caption: 13px; --cds-font-size-body: 15px; --cds-font-size-heading: 17px; --cds-font-size-title: 30px; --cds-font-weight-medium: 600;
  --cds-gap-xs: 4px; --cds-gap-sm: 8px; --cds-gap-md: 12px; --cds-gap-lg: 16px; --cds-gap-xl: 24px;
  --cds-pad-xs: 4px; --cds-pad-sm: 8px; --cds-pad-md: 12px; --cds-pad-lg: 16px; --cds-pad-xl: 24px; --cds-radius: 8px;
  --cds-chart-muted: #b9b6ad; --cds-chart-grid: #ebe8e1; --cds-chart-axis: #c9c6bd; --cds-chart-reference: #6b6963; --cds-text-secondary: #6b6963;
  --cds-surface-popover: #ffffff; --cds-border: #d9d6ce; --cds-shadow-popover: 0 4px 16px rgba(0,0,0,.14);
  --lk-c1: #2a78d6; --lk-c2: #e07b2e; --lk-c3: #1f9e8f; --lk-c4: #8a63c7; --lk-c5: #c9506b; --lk-c6: #7a8b2c;
}
@media (prefers-color-scheme: dark) {
  :root {
    --color-fg: #eceae4; --color-fg-muted: #a3a097; --color-bg: #191816; --color-panel: #22211e; --color-border-line: #3a3833;
    --color-ok: #4cc27e; --color-warn: #e0a84a; --color-bad: #ef7a6c;
    --cds-chart-muted: #6e6b64; --cds-chart-grid: #302e2a; --cds-chart-axis: #4a4842; --cds-chart-reference: #a3a097; --cds-text-secondary: #a3a097;
    --cds-surface-popover: #2b2a26; --cds-border: #45433d; --cds-shadow-popover: 0 4px 16px rgba(0,0,0,.5);
    --lk-c1: #5b9cf0; --lk-c2: #f09a54; --lk-c3: #45c2b2; --lk-c4: #ab8ae6; --lk-c5: #e87992; --lk-c6: #a8bd4f;
  }
}
html, body { margin: 0; background: var(--color-bg); }
body { padding: 24px clamp(12px, 3vw, 40px) 48px; font-size: var(--cds-font-size-body); }
.lk { max-width: 1400px; margin: 0 auto; }
.lk .dash-select { font: inherit; color: var(--color-fg); background-color: var(--color-panel); border: 1px solid var(--color-border-line); border-radius: 6px; padding: 6px 10px; min-width: 9em; }
.lk .fuss { color: var(--color-fg-muted); font-size: var(--cds-font-size-caption); }
'''

# --- Seitenkörper aus dem Überblick -------------------------------------------------------------
body = src[src.index('<div class="lk"'):src.index('<script>')].rstrip()
assert body.endswith('</div>')
body = re.sub(r' data-(source|field|row|row-key|where)="[^"]*"', '', body)       # Herkunftsmarken braucht nur Claude
body = rep(body, '<header id="kopf">\n    <h1>', '<header id="kopf">\n    <div class="marke">' + LOGO + '</div>\n    <h1>')
body = rep(body, '''<option value="alle">2024–2026</option>
      </select></label>''', '''<option value="alle">2024–2026</option>
      </select></label>
    <label>Quartal
      <select class="dash-select" data-param="quartal" aria-label="Quartal">
        <option value="">Alle Quartale</option><option value="1">Q1</option><option value="2">Q2</option><option value="3">Q3</option><option value="4">Q4</option>
      </select></label>
    <label>Monat
      <select class="dash-select" data-param="monat" aria-label="Monat">
        <option value="">Alle Monate</option><option value="01">Januar</option><option value="02">Februar</option><option value="03">März</option><option value="04">April</option><option value="05">Mai</option><option value="06">Juni</option><option value="07">Juli</option><option value="08">August</option><option value="09">September</option><option value="10">Oktober</option><option value="11">November</option><option value="12">Dezember</option>
      </select></label>''')
body = rep(body, '<option value="0">0 (ohne Reaktionszeit)</option>\n      </select></label>', '<option value="0">0 (ohne Reaktionszeit)</option>\n      </select></label>\n    <label>Übersicht und BSC je\n      <select class="dash-select" data-param="bsc_periode" aria-label="Übersicht und BSC je Zeitraum">\n        <option value="monat">Monat</option><option value="quartal">Quartal</option><option value="jahr">Jahr</option>\n      </select></label>')
body = rep(body, '(bei 2026: 01.01. bis Datenstand). Bei „2024–2026“ und 2024 gibt es keinen Vergleich.',
           'mit gleichem Quartal oder Monat (im laufenden Jahr jeweils nur bis zum Tag des Datenstands). Für das erste Jahr und für „alle Jahre“ gibt es keinen Vergleich.')
body = rep(body, ' · Aufträge ab 01.01.2024</p>', ' · Aufträge ab 01.01.2024 · Daten erzeugt am <span id="lk-erzeugt">—</span> · <span id="version">Version 1.1</span></p>')

S = lambda d: '<span data-draw="%s">—</span>' % d
B = lambda d: '<b data-draw="%s">—</b>' % d


def tile(label, draw, sub, cls=''):
    return ('<div class="card tile"><div class="lbl">%s</div><div class="val%s" data-draw="%s">—</div><div class="chg neutral">%s</div></div>'
            % (label, ' ' + cls if cls else '', draw, sub))


def tiles(*t):
    return '<div class="tiles">' + ''.join(t) + '</div>'


def legend(*items):
    return '<div class="legend">' + ''.join('<span><i %s></i>%s</span>' % ('class="muted"' if s == 'muted' else 'data-draw="%s"' % s, t) for s, t in items) + '</div>'


def card(title, inner, sub=''):
    return '<section class="card"><h2>%s</h2>%s%s</section>' % (title, '<p class="sub">%s</p>' % sub if sub else '', inner)


def chart(draw, kw=False):
    return '<div class="chart%s" data-draw="%s"></div>' % (' kw' if kw else '', draw)


def table(draw, cols):
    th = ''.join('<th%s>%s</th>' % (' class="l"' if c.startswith('<') else '', c.lstrip('<')) for c in cols)
    return '<div class="tw"><table><thead><tr>%s</tr></thead><tbody data-draw="%s"></tbody></table></div>' % (th, draw)


def grid(*c):
    return '<div class="grid2">' + ''.join(c) + '</div>'


def tab(tid, title, sub, *parts, defs=''):
    d = '<details><summary>Definitionen und Abweichungen zum Power-BI-Bericht</summary>%s</details>' % defs if defs else ''
    return '<section class="tab" id="%s" hidden><div><h2>%s</h2><p class="sub">%s</p></div>%s%s</section>' % (tid, title, sub, ''.join(parts), d)


BSC_TAB = ('<section class="tab" id="bsc" hidden><div><h2>Balanced Scorecard (BSC)</h2>'
  '<p class="sub">Die Spitzenkennzahlen (HoQ 1) und ihre Einzelkennzahlen (HoQ 2) je Monat, Quartal oder Jahr, gerechnet aus den Daten der anderen Reiter; die von Hand gepflegten Kennzahlen, SOLL-Werte, Zielwerte und Gewichtungen kommen aus den manuellen Daten. Es wirkt der Filter Jahr; die BSC gilt für das ganze Labor. Die Kacheln zeigen ' + B('bsc_q') + '.</p>'
  '<p class="hinweis">Prüfansicht: Drucken im Browser (Strg + P) ergibt einen Bericht mit jedem Reiter auf einer eigenen Seite, mit allen Formeln und Erläuterungen aufgeklappt; als Drucker „Als PDF speichern“ wählen. Die Einteilung nach Monat, Quartal oder Jahr wählt der Filter „Übersicht und BSC je“ oben.</p></div>'
  + tiles(tile('Termintreue', 'bsc_termintreue', 'SOLL mindestens ' + S('bsc_termintreue_soll')),
          tile('Budgeteinhaltung', 'bsc_budgeteinhaltung', 'SOLL mindestens ' + S('bsc_budgeteinhaltung_soll')),
          tile('Qualitätslevel', 'bsc_qualitaetslevel', 'SOLL mindestens ' + S('bsc_qualitaetslevel_soll')))
  + '<section class="card"><h2>Kennzahlen je Zeitraum</h2><p class="sub">Grün: SOLL erreicht, rot: unter SOLL. Ein Strich bedeutet, dass für den Zeitraum Daten fehlen.</p>'
    '<div class="tw"><table><thead><tr data-draw="tb_bsc_kopf"></tr></thead><tbody data-draw="tb_bsc"></tbody></table></div></section>'
  '<details><summary>Formeln und Herkunft der Kennzahlen</summary>'
  '<p><b>Termintreue</b> = (Reaktionszeit S + Reaktionszeit M + Reaktionszeit L) / 3 × Gewichtung Reaktionszeit + Pünktlichkeit × Gewichtung Pünktlichkeit. <b>Budgeteinhaltung</b> = Erfüllungsgrad Plankosten × Gewichtung + Erfüllungsgrad Vergabe × Gewichtung + Erfüllungsgrad Auftragsquote × Gewichtung + Erfüllungsgrad Instandhaltungsquote × Gewichtung. Der Erfüllungsgrad Plankosten ist 100 % minus die Abweichung der Plankostenerfüllung vom Zielwert, nach oben wie nach unten. Der Erfüllungsgrad Auftragsquote ist die Auftragsquote im Verhältnis zum Zielwert, ohne Obergrenze: Eine Übererfüllung bei den Aufträgen gleicht Schwächen der anderen drei Kennzahlen aus. Der Erfüllungsgrad Instandhaltungsquote ist die Instandhaltungsquote im Verhältnis zum Zielwert, ebenfalls ohne Obergrenze. Die Eigenleistungsquote ist 100 % minus Vergabequote; ihr SOLL ergibt sich aus der maximalen Vergabequote. Der Erfüllungsgrad Vergabe ist 100 %, solange die Vergabequote die maximale Vergabequote nicht überschreitet; darüber ist er die Eigenleistungsquote im Verhältnis zu ihrem SOLL (Beispiel: Vergabequote 30 % ergibt 70 / 80 = 87,5 %). Die Spalte SOLL zeigt Mindestwerte (≥) und bei der Rückweisung einen Höchstwert (≤). <b>Qualitätslevel</b> = Dienstleistungsquote × Gewichtung + (1 − |Methodeneinsatz − Zielwert|) × Gewichtung + (1 − Rückweisung) × Gewichtung. Gewichtungen, Zielwerte und SOLL-Werte stehen im Blatt „BSC_Vorgaben“ der manuellen Daten.</p>'
  '<p><b>Herkunft der Einzelkennzahlen:</b> Reaktionszeit S ist S_Babtec; Reaktionszeit M und L sowie die Pünktlichkeit (Mittel aus M und L) kommen aus dem Reiter Termintreue. Reaktionszeit, Pünktlichkeit und Plankostenerfüllung gibt es nur für M und L, weil das Labor nur dort plant. Plankostenerfüllung ist die Gesamtquote (Summe IST / Summe PLAN) der M- und L-Aufträge. Auftragsquote ist die Quote über QLA, QLG und QLM. Instandhaltungsquote ist der Anteil der auf Laboraufträge (S, M, L) und auf WE+FP gebuchten Stunden an den Soll-Stunden, also die Leistung, für die das Labor im Sinne eines Profitcenters Geld bekommen würde; alle gebuchten Stunden zu den Soll-Stunden heißen Buchungsquote. Vergabequote ist die extern eingekaufte Leistung gemessen an der gesamten erbrachten Leistung des Labors. Dienstleistungsquote, Methodeneinsatz und Rückweisung werden von Hand im Blatt „BSC_Quartal“ gepflegt; für Quartale ohne Eintrag bleibt das Qualitätslevel leer.</p>'
  '<p>Alle Kennzahlen sind je gewähltem Zeitraum aus den Einzeldaten gerechnet, nicht als Mittelwert kleinerer Zeiträume. Die von Hand gepflegten Kennzahlen sind je Quartal erfasst: Ein Monat übernimmt den Wert seines Quartals, ein Jahr den Mittelwert seiner Quartale. Im laufenden Zeitraum sind die Werte vorläufig.</p></details></section>')


def ktt(id_, liste, titel, lbl, draw, n, d, wort, soll=None):
    s = ' data-soll="%s"' % soll if soll else ''
    zeile = ('<div class="soll">SOLL ≥ ' + S('lk_soll_' + soll) + '</div>') if soll else ('<div class="soll">SOLL noch offen</div>' if liste is not None and draw == 'tk_l' else '')
    kl = (' data-liste="%s" role="button" tabindex="0" title="%s"' % (liste, titel)) if liste is not None else ''
    return ('<div class="card tile" id="%s"%s><div class="lbl">%s</div><div class="val"%s data-draw="%s">—</div><div class="chg neutral">%s von %s %s</div>%s</div>'
            % (id_, kl, lbl, s, draw, S(n), S(d), wort, zeile))


TT_KACHELN = ('<div class="tiles">'
  + ktt('tt-k-s', 's', 'Liste der Aufträge über 48 Stunden zeigen', 'S_Babtec: Prüfgruppen ≤ 48 h', 'tk_s', 'tk_s_n', 'tk_s_d', 'Aufträgen', 'soll_reaktion_s')
  + ktt('tt-k-si', None, '', 'S_Babtec_inkl_LMS: ≤ 48 h', 'tk_si', 'tk_si_n', 'tk_si_d', 'Aufträgen')
  + ktt('tt-k-m', '', 'Liste der M-Aufträge über 14 Tage zeigen', 'Reaktionszeit M: ≤ 14 Tage', 'tk_m', 'tk_m_n', 'tk_m_d', 'Aufträgen', 'soll_reaktion_m')
  + ktt('tt-k-l', 'l_frist', 'Liste der L-Aufträge über 70 Tage zeigen', 'Reaktionszeit L: ≤ 70 Tage', 'tk_l', 'tk_l_n', 'tk_l_d', 'Aufträgen')
  + ktt('tt-k-pm', 'm_termin', 'Liste der verspäteten M-Aufträge zeigen', 'Pünktlichkeit M', 'tk_pm', 'tk_pm_n', 'tk_pm_d', 'mit Termin', 'soll_puenktlich_m')
  + ktt('tt-k-pl', 'l_termin', 'Liste der verspäteten L-Aufträge zeigen', 'Pünktlichkeit L', 'tk_pl', 'tk_pl_n', 'tk_pl_d', 'mit Termin', 'soll_puenktlich_l')
  + '</div><p class="hinweis">Ein Klick auf eine Kachel zeigt unten die Aufträge, die die Vorgabe verfehlt haben. Die gestrichelten Linien in den Diagrammen markieren das SOLL.</p>')

TT_LISTE = ('<section class="card" id="tt-abweichungen"><h2>Aufträge außerhalb der Vorgabe</h2>'
  '<p class="sub">Im gewählten Zeitraum abgeschlossene Aufträge, die die gewählte Vorgabe verfehlt haben, größte Abweichung zuerst; gefunden: ' + B('tt_liste_n') + ', gezeigt höchstens 200. Bei M und L zählen Aufträge ohne Bearbeitungsbeginn als außerhalb der Frist. Bei S ist es die schnellste Prüfgruppe des Babtec-Auftrags; dort wirkt der Laborfilter nicht.</p>'
  '<div class="filters"><label>Vorgabe <select class="dash-select" data-param="tt_liste" aria-label="Vorgabe für die Liste"><option value="">M: Reaktionszeit über 14 Tage</option><option value="l_frist">L: Reaktionszeit über 70 Tage</option><option value="m_termin">M: nach dem zugesagten Termin</option><option value="l_termin">L: nach dem zugesagten Termin</option><option value="s">S_Babtec: über 48 Stunden</option></select></label></div>'
  + table('tb_tt_liste', ['Auftrag', '<Bezeichnung', '<Labor', 'Abschluss', '<Vorgabe', 'Ist']) + '</section>')


def ku(id_, ziel, lbl, f, soll, gross=False):
    return ('<div class="card tile" id="%s" data-ziel="%s" role="button" tabindex="0"><div class="lbl">%s</div><div class="val" data-draw="ue_v_%s">—</div><div class="soll">%s</div><div class="chg" data-draw="ue_d_%s"></div></div>'
            % (id_, ziel, lbl, f, soll, f))


UEBERSICHT = ('<section class="tab" id="uebersicht"><div id="ue-kopf"><h2>Übersicht</h2>'
  '<p class="sub">Alle Kennzahlen der Balanced Scorecard für ' + B('ue_zeitraum') + ', verglichen mit dem Zeitraum davor. Grün: SOLL erreicht, rot: SOLL verfehlt; Kennzahlen ohne SOLL bleiben schwarz. Es wirkt der Filter Jahr, die Einteilung wählt „Übersicht und BSC je“; die Werte gelten für das ganze Labor. Ein Klick auf eine Kachel öffnet die Einzelheiten.</p>'
  '<p class="lead">SOLL erreicht: ' + B('ue_ok') + ' von ' + B('ue_mit') + ' Kennzahlen mit SOLL. Verfehlt: ' + B('ue_rot') + '.</p></div>'
  '<div class="tiles gross">'
  + ku('ue-k-termintreue', 'termintreue', 'Termintreue (HoQ 1)', 'termintreue', 'SOLL ≥ ' + S('ue_s_termintreue'))
  + ku('ue-k-budget', 'budget', 'Budgeteinhaltung (HoQ 1)', 'budgeteinhaltung', 'SOLL ≥ ' + S('ue_s_budgeteinhaltung'))
  + ku('ue-k-qualitaet', 'bsc', 'Qualitätslevel (HoQ 1)', 'qualitaetslevel', 'SOLL ≥ ' + S('ue_s_qualitaetslevel'))
  + '</div><h3>Termintreue</h3><div class="tiles">'
  + ku('ue-k-s', 'termintreue', 'Reaktionszeit S (≤ 48 h)', 's', 'SOLL ≥ ' + S('ue_s_s'))
  + ku('ue-k-m', 'termintreue', 'Reaktionszeit M (≤ 14 Tage)', 'm', 'SOLL ≥ ' + S('ue_s_m'))
  + ku('ue-k-l', 'termintreue', 'Reaktionszeit L (≤ 70 Tage)', 'l', 'SOLL noch offen')
  + ku('ue-k-pm', 'termintreue', 'Pünktlichkeit M', 'puenktlich_m', 'SOLL ≥ ' + S('ue_s_puenktlich_m'))
  + ku('ue-k-pl', 'termintreue', 'Pünktlichkeit L', 'puenktlich_l', 'SOLL ≥ ' + S('ue_s_puenktlich_l'))
  + '</div><h3>Budgeteinhaltung</h3><div class="tiles">'
  + ku('ue-k-pk', 'plankosten', 'Plankostenerfüllung (IST / PLAN)', 'plankosten', 'Ziel ' + S('ue_z_ziel_plankosten') + ', Abweichung in beide Richtungen zählt')
  + ku('ue-k-vq', 'vergabequote', 'Vergabequote (extern)', 'vergabequote', 'höchstens ' + S('ue_s_vergabequote'))
  + ku('ue-k-aq', 'auftragsquote', 'Auftragsquote', 'auftragsquote', 'Ziel ' + S('ue_z_ziel_auftragsquote') + ', ohne Ampel')
  + ku('ue-k-iq', 'instandhaltungsquote', 'Instandhaltungsquote', 'instandhaltungsquote', 'Ziel ' + S('ue_z_ziel_instandhaltungsquote') + ', ohne Ampel')
  + '</div><h3>Qualitätslevel</h3><div class="tiles">'
  + ku('ue-k-dl', 'bsc', 'Dienstleistungsquote', 'dienstleistungsquote', 'SOLL noch offen · von Hand gepflegt')
  + ku('ue-k-me', 'bsc', 'Methodeneinsatz', 'methodeneinsatz', 'Ziel ' + S('ue_z_ziel_methodeneinsatz') + ' · von Hand gepflegt')
  + ku('ue-k-rw', 'bsc', 'Rückweisung', 'rueckweisung', 'SOLL ≤ ' + S('ue_s_rueckweisung') + ' · von Hand gepflegt')
  + '</div><p class="sub">Grundlage ist der letzte abgeschlossene Zeitraum; im laufenden Zeitraum sind die Werte noch vorläufig und stehen im Reiter BSC. Die Auftragszahlen (Eingang, Abschlüsse, Durchlaufzeit, überfällige Aufträge) stehen im Reiter „Aufträge“.</p></section>')

BUDGET = ('<section class="tab" id="budget" hidden><div><h2>Budgeteinhaltung (HoQ 1)</h2>'
  '<p class="sub">Die Budgeteinhaltung setzt sich aus vier Einzelkennzahlen zusammen, die unten nacheinander folgen: Plankostenerfüllung, Auftragsquote, Vergabequote sowie Buchungs- und Instandhaltungsquote. Wie sie gewichtet in die Spitzenkennzahl eingehen, steht im Reiter BSC.</p></div>'
  '<div class="subnav" role="navigation" aria-label="Einzelkennzahlen der Budgeteinhaltung"><button type="button" data-ziel="plankosten">Plankostenerfüllung</button><button type="button" data-ziel="auftragsquote">Auftragsquote</button><button type="button" data-ziel="vergabequote">Vergabequote</button><button type="button" data-ziel="instandhaltungsquote">Buchungs- und Instandhaltungsquote</button></div></section>')


GRP = ['Aufträge', 'PLAN', 'IST', 'Abweichung', 'Gesamtquote', 'Ø Quoten', 'Im Plan']
SD = ['Angelegt', 'Gewertet', 'Same-Day', 'Quote', '≤ 24 h']
tabs = [
 ('bsc', 'BSC', BSC_TAB),
 ('termintreue', 'Termintreue (HoQ 1)', tab('termintreue', 'Termintreue (HoQ 1)',
    'Alle Werte nach Kalenderwoche des technischen Abschlusses. Es wirken die Filter Jahr, Quartal, Monat und Labor; der Filter Priorität wirkt hier nicht, weil jede Kennzahl ihre Priorität fest vorgibt. Die Prüfgruppen-Kennzahlen (Babtec) kennen kein Labor und zeigen immer alle Bereiche.',
    TT_KACHELN,
    grid(card('Reaktionszeit S: ≤ 48 h', legend(('leg0', 'S_Babtec'), ('leg1', 'S_Babtec_inkl_LMS')) + chart('ch_tt_s', True), 'Anteil der Babtec-Aufträge (Wareneingangs- und Fertigungsprüfung), deren Prüfgruppe höchstens 48 Stunden nach Anlage abgeschlossen wurde (S_Babtec), und derselbe Anteil einschließlich der S-Aufträge aus der LMS-Auftragsliste (S_Babtec_inkl_LMS)'),
         card('Durchlaufzeit Wareneingangsprüfung in Stunden', legend(('leg0', 'Mittelwert'), ('leg1', 'Median')) + chart('ch_tt_dlz', True)),
         card('Reaktionszeit M: Aufträge ≤ 14 Tage', chart('ch_tt_m', True), 'Anteil der abgeschlossenen M-Aufträge mit Abschluss höchstens 14 Tage nach Bearbeitungsbeginn'),
         card('Pünktlichkeit M', chart('ch_tt_pm', True), 'Anteil der abgeschlossenen M-Aufträge mit Abschluss bis zum zugesagten Termin'),
         card('Reaktionszeit L: Aufträge ≤ 70 Tage', chart('ch_tt_l', True), 'Anteil der abgeschlossenen L-Aufträge mit Abschluss höchstens 70 Tage nach Bearbeitungsbeginn'),
         card('Pünktlichkeit L', chart('ch_tt_pl', True), 'Anteil der abgeschlossenen L-Aufträge mit Abschluss bis zum zugesagten Termin')),
    TT_LISTE,
    defs='<p><b>Kalenderwoche mit Jahr:</b> ISO-Kalenderwochen mit ihrem Jahr. <b>Reaktionszeit L:</b> Aufträge, die schon vor dem geplanten Bearbeitungsbeginn abgeschlossen waren, zählen wie bei M als fristgerecht. <b>Pünktlichkeit:</b> im Nenner nur Aufträge mit zugesagtem Termin. <b>Durchlaufzeit:</b> zusätzlich zum Mittelwert der Median.</p><p>Unverändert: Abschlüsse vom 04. bis 06.04.2026 bleiben bei den Prüfgruppen ausgenommen (Sammelabschluss). „S_Babtec“ misst die Babtec-Prüfgruppen (Abschluss höchstens 48 Stunden nach Anlage). „S_Babtec_inkl_LMS“ nimmt die S-Aufträge aus der LMS-Auftragsliste dazu (Abschluss höchstens 48 Stunden nach Bearbeitungsbeginn); der Laborfilter wirkt dabei nur auf den LMS-Teil. Die Kacheln summieren die Wochenwerte.</p>')),
 ('plankosten', 'Plankostenerfüllung (HoQ 2)', tab('plankosten', 'Plankostenerfüllung (HoQ 2)',
    'IST-Kosten (gebuchte Stunden × Stundensatz, derzeit 75 €) im Verhältnis zu den PLAN-Kosten (Auftragswert) der abgeschlossenen M- und L-Aufträge, nach Datum des technischen Abschlusses. Kosten plant das Labor nur für M und L; S-Aufträge und Aufträge ohne Reaktionszeit zählen nicht mit. Es wirken alle Filter. Gewertet sind ' + B('pk_n') + ' Aufträge mit Planwert und gebuchten Stunden; ' + B('pk_oh') + ' abgeschlossene Aufträge ohne gebuchte Stunden und ' + B('pk_op') + ' ohne Planwert fehlen.',
    tiles(tile('Plankostenerfüllung gesamt', 'pk_q', 'IST ' + S('pk_ist') + ' / PLAN ' + S('pk_plan')),
          tile('Abweichung IST − PLAN', 'pk_abw', 'über alle gewerteten Aufträge'),
          tile('Aufträge im Plan (≤ 100 %)', 'pk_imp', S('pk_imp_n') + ' von ' + S('pk_imp_d') + ' Aufträgen'),
          tile('Ø der Auftragsquoten (wie Power BI)', 'pk_qm', 'Median ' + S('pk_med'))),
    card('Plankostenerfüllung je Kalenderwoche', legend(('leg0', 'Gesamtquote (Summe IST / Summe PLAN)'), ('leg1', 'Ø der Auftragsquoten (wie Power BI)')) + chart('ch_pk', True), 'Nach Woche des technischen Abschlusses; die gestrichelte Linie markiert 100 %'),
    card('Nach Priorität', table('tb_pk_prio', ['Priorität'] + GRP)),
    card('Nach Labor', table('tb_pk_labor', ['Labor'] + GRP), 'Ein Auftrag mit mehreren Laboren zählt bei jedem beteiligten Labor mit vollem PLAN und IST.'),
    card('Größte Abweichungen vom Plan', table('tb_pk_top', ['Auftrag', '<Bezeichnung', '<Labor', '<Prio', 'Abschluss', 'Stunden', 'PLAN', 'IST', 'Abweichung', 'Quote']), 'Die 20 Aufträge mit der größten Abweichung in Euro, nach oben wie nach unten'),
    defs='<p><b>IST-Kosten:</b> alle im LIMS auf die Auftragsnummer gebuchten Stunden × Stundensatz aus dem Blatt „BSC_Vorgaben“. <b>PLAN-Kosten:</b> Feld „Auftragswert berechnet“. <b>Quote:</b> IST / PLAN.</p><p>Korrekturen: nur abgeschlossene M- und L-Aufträge, weil das Labor nur für diese Auftragsarten Kosten plant; Hauptkennzahl ist die Gesamtquote (Summe IST / Summe PLAN), der Mittelwert der Einzelquoten aus Power BI steht daneben; Kalenderwoche mit Jahr.</p>')),
 ('auftragsquote', 'Auftragsquote (HoQ 2)', tab('auftragsquote', 'Auftragsquote (HoQ 2)',
    'Abgeschlossene Aufträge je Labor im Verhältnis zu den Soll-Aufträgen, nach Monat des technischen Abschlusses. Es wirken die Filter Jahr, Quartal, Monat und Labor; der Filter Priorität wirkt hier nicht. Soll-Vorgaben gibt es nur für QLA, QLG und QLM.',
    tiles(tile('Auftragsquote gesamt', 'aq_q', S('aq_n') + ' abgeschlossen / Soll ' + S('aq_d')),
          *[tile(l.upper(), 'aq_' + l, S('aq_%s_n' % l) + ' abgeschlossen / Soll ' + S('aq_%s_d' % l)) for l in ('qla', 'qlg', 'qlm')]),
    card('Auftragsquote je Monat', legend(('leg0', 'QLA'), ('leg1', 'QLG'), ('leg2', 'QLM')) + chart('ch_aq'), 'Die gestrichelte Linie markiert 100 %, also Soll erreicht'),
    card('Abgeschlossen, Soll und Quote je Monat', table('tb_aq', ['Monat', 'QLA abg.', 'QLA Soll', 'QLA Quote', 'QLG abg.', 'QLG Soll', 'QLG Quote', 'QLM abg.', 'QLM Soll', 'QLM Quote', 'Summe abg.', 'Summe Soll', 'Quote'])),
    defs='<p><b>Abgeschlossen:</b> Aufträge mit technischem Abschluss im Monat, alle Prioritäten; ein Auftrag mit mehreren Laboren zählt bei jedem. <b>Soll:</b> manuell gepflegte Soll-Aufträge. <b>Quote:</b> abgeschlossen / Soll.</p><p>Korrekturen: im laufenden Monat ist das Soll anteilig bis zum Datenstand gerechnet; nur Monate und Labore mit Soll-Vorgabe; Abschlüsse und Soll werden beide je Labor addiert.</p>')),
 ('vergabequote', 'Vergabequote (HoQ 2)', tab('vergabequote', 'Vergabequote (HoQ 2)',
    'Anteil der extern vergebenen Leistung an der Gesamtleistung des Labors aus den SAP-Instandhaltungskosten, nach Buchungsmonat. Es wirken die Filter Jahr, Quartal und Monat; Labor und Priorität gibt es in den SAP-Daten nicht. Die Daten beginnen 2025.',
    tiles(tile('Vergabequote', 'vq_q', 'extern / (intern + extern)'), tile('Externe Leistung', 'vq_ext', 'vier Sachkonten, siehe Tabelle unten'),
          tile('Interne Leistung', 'vq_int', 'Personalstunden (94311000)'), tile('Gesamtleistung Labor', 'vq_ges', 'nicht gewertet: ' + S('vq_son'))),
    grid(card('Vergabequote je Monat', legend(('leg0', 'Monat'), ('leg1', 'aufgelaufen im gewählten Zeitraum')) + chart('ch_vq')),
         card('Interne und externe Leistung je Monat', legend(('leg0', 'intern'), ('leg1', 'extern')) + chart('ch_vq_eur'))),
    card('Nach Auftragsart', table('tb_vq_art', ['Auftragsart', 'Intern', 'Extern', 'Gesamt', 'Vergabequote'])),
    card('Monatswerte', table('tb_vq_monat', ['Monat', 'Intern', 'Extern', 'Gesamt', 'Vergabequote', 'aufgelaufen'])),
    card('Sachkonten und ihre Zuordnung', table('tb_vq_konto', ['Sachkonto', '<Zuordnung', 'Positionen', 'Kosten'])),
    defs='<p><b>Interne Leistung:</b> Istkosten auf Sachkonto 94311000. <b>Externe Leistung:</b> Sachkonten 65001000, 63012000, 65602000 und 65200000. <b>Vergabequote:</b> extern / (intern + extern).</p><p>Korrektur: Buchungsmonat statt terminiertem Beginndatum. Buchungsmonate vor 2025 sind ausgelassen, weil der Export nur Aufträge mit Beginn ab 2025 enthält.</p>')),
 ('instandhaltungsquote', 'Buchungs- und Instandhaltungsquote (HoQ 2)', tab('instandhaltungsquote', 'Buchungs- und Instandhaltungsquote (HoQ 2)',
    'Buchungsquote: alle im LIMS gebuchten Stunden im Verhältnis zu den Soll-Stunden. Instandhaltungsquote: nur die auf Laboraufträge (S, M, L) und auf WE+FP gebuchten Stunden im Verhältnis zu den Soll-Stunden, also die Leistung, für die das Labor im Sinne eines Profitcenters Geld bekommen würde. Soll-Stunden = Arbeitstage abzüglich Abwesenheiten, mal FTE, mal 8 Stunden; ausgewertet für QLA, QLG und QLM, je Monat. Es wirken die Filter Jahr, Quartal, Monat und Labor; der Filter Priorität wirkt hier nicht. Die Daten beginnen 2025; Monate mit unvollständig erfassten Abwesenheiten fehlen.',
    tiles(tile('Buchungsquote', 'iq_q', 'IST ' + S('iq_ist') + ' / SOLL ' + S('iq_soll')), tile('Instandhaltungsquote (Laboraufträge und WE+FP)', 'iq_la', S('iq_la_h') + ' auf bezahlte Leistung gebucht'),
          tile('davon auf „Sonstiges“', 'iq_so', S('iq_so_h') + ' der Soll-Stunden'), tile('Quote wie Power BI', 'iq_pbi', 'mit Urlaub und Krankheit: ' + S('iq_abw'))),
    grid(card('Buchungsquote und Instandhaltungsquote je Monat', legend(('leg0', 'Buchungsquote (alle gebuchten Stunden)'), ('leg1', 'Instandhaltungsquote (Stunden auf Laboraufträge und WE+FP)')) + chart('ch_iq')),
         card('Gebuchte Stunden nach Kontierungstyp', legend(('leg0', 'Laborauftrag'), ('leg1', 'WE+FP'), ('leg2', 'Wartung und Kalibrierung'), ('leg3', 'Sonstiges'), ('muted', 'Urlaub und Krankheit')) + chart('ch_iq_typ'), 'In Prozent der Brutto-Stunden des Monats (Arbeitstage × FTE × 8, ohne Abzug von Abwesenheiten). 100 % heißt: Jede Stunde des Monats ist als Arbeit oder als Urlaub oder Krankheit gebucht.')),
    card('Nach Labor', table('tb_iq_labor', ['Labor', 'SOLL', 'IST', 'Quote', 'Laborauftrag', 'WE+FP', 'Wartung', 'Kalibrierung', 'Sonstiges', 'wie Power BI']), 'Alle Anteile in Prozent der Soll-Stunden'),
    card('Monatswerte in Stunden', table('tb_iq_monat', ['Monat', 'SOLL', 'IST', 'Quote', 'Laborauftrag', 'WE+FP', 'Wartung', 'Kalibrierung', 'Sonstiges', 'Urlaub', 'Krankheit'])),
    defs='<p><b>SOLL-Stunden:</b> je Person (Arbeitstage − Abwesenheitstage) × FTE des Monats × 8; die FTE je Mitarbeiter und Monat steht im Blatt „FTE_Monat“. <b>IST-Stunden:</b> im LIMS gebuchte Stunden von QLA, QLG und QLM ohne Urlaub und Krankheit. <b>Buchungsquote:</b> IST / SOLL. <b>Instandhaltungsquote:</b> Stunden auf Laboraufträge und WE+FP / SOLL.</p><p>Korrekturen gegenüber Power BI: Urlaub und Krankheit zählen nicht zum IST, weil das Soll bereits um Abwesenheiten gekürzt ist; nur vollständig erfasste Monate; Schreibvarianten der Kontierung sind dem richtigen Typ zugeordnet.</p>')),
 ('wartung-kalibrierung', 'Wartung und Kalibrierung', tab('wartung-kalibrierung', 'Wartung und Kalibrierung',
    'Abgeschlossene Wartungsaufträge (ZLB3) und Kalibrieraufträge (ZLB4) aus SAP, nach Monat des Ist-Endtermins. Es wirken die Filter Jahr, Quartal und Monat. Die überfälligen Aufträge zeigen den Stand zum Datenstand, unabhängig vom Zeitraum.',
    tiles(tile('Wartungen abgeschlossen', 'wk_w', 'davon pünktlich ' + S('wk_wp')), tile('Kalibrierungen abgeschlossen', 'wk_k', 'davon pünktlich ' + S('wk_kp')),
          tile('Kalibrierung extern', 'wk_ea', S('wk_ke') + ' extern / ' + S('wk_ki') + ' intern'),
          tile('Freigegeben und überfällig', 'wk_uf', S('wk_ufw') + ' Wartung / ' + S('wk_ufk') + ' Kalibrierung, Stand heute', 'bad')),
    grid(card('Abgeschlossene Aufträge je Monat', legend(('leg0', 'Wartung'), ('leg1', 'Kalibrierung intern'), ('leg2', 'Kalibrierung extern'), ('muted', 'Kalibrierung ohne Angabe')) + chart('ch_wk')),
         card('Pünktlich abgeschlossen je Monat', legend(('leg0', 'Wartung'), ('leg1', 'Kalibrierung')) + chart('ch_wk_tt'), 'Anteil der Aufträge mit Ist-Endtermin bis zum Eckendtermin')),
    grid(card('Kalibrierungen nach Bezeichnung', table('tb_wk_kal', ['Bezeichnung', 'Anzahl', 'intern', 'extern', 'pünktlich']), 'Die 15 häufigsten im gewählten Zeitraum'),
         card('Wartungen nach Bezeichnung', table('tb_wk_wartung', ['Bezeichnung', 'Anzahl', 'pünktlich']), 'Die 15 häufigsten im gewählten Zeitraum')),
    card('Freigegebene, überfällige Aufträge', table('tb_wk_ueber', ['Auftrag', '<Art', '<Bezeichnung', '<Kurztext', 'Eckendtermin', 'Tage über']),
         'Ohne Ist-Endtermin und Eckendtermin überschritten; die 25 am längsten überfälligen. Daneben gibt es ' + B('wk_unf') + ' nie freigegebene Aufträge mit abgelaufenem Eckendtermin, die hier nicht mitzählen.'),
    defs='<p><b>Abgeschlossen:</b> Ist-Endtermin im gewählten Zeitraum. <b>Pünktlich:</b> Ist-Endtermin am oder vor dem Eckendtermin. <b>Überfällig:</b> kein Ist-Endtermin und Eckendtermin vor dem Datenstand. <b>Intern/extern:</b> aus dem Kurztext des Kalibrierauftrags.</p>')),
 ('tecsa', 'TecSa', tab('tecsa', 'TecSa – Technische Sauberkeit',
    'Ausgewertete Filter aus der Datenbank der Standardprüfungen des Sauberkeitslabors, nach Prüfdatum. Es wirken die Filter Jahr, Quartal und Monat. Die Daten beginnen im März 2024.',
    tiles(tile('Anzahl Filter', 'ts_n', 'an ' + S('ts_tage') + ' Tagen'), tile('Filter je Tag', 'ts_jt', 'Durchschnitt der Tage mit Filtern'),
          tile('Fertigungsprüfung (FP)', 'ts_fpa', S('ts_fp') + ' Filter'), tile('Wareneingang (WE)', 'ts_wea', S('ts_we') + ' Filter')),
    card('Filter je Kalenderwoche', legend(('leg0', 'Fertigungsprüfung (FP)'), ('leg1', 'Wareneingang (WE)'), ('muted', 'ohne Angabe')) + chart('ch_ts')),
    card('Filter nach Produkt', table('tb_ts_produkt', ['Produkt', 'Filter', 'Anteil', 'FP', 'WE']), 'Die 20 häufigsten Produkte im gewählten Zeitraum'),
    grid(card('Filter nach Wochentag', table('tb_ts_tag', ['Wochentag', 'Filter', 'Tage', 'Filter je Tag'])),
         card('Filter nach Auswertungsart', table('tb_ts_ausw', ['Auswertung', 'Filter', 'Anteil']))),
    defs='<p><b>Filter:</b> eine Zeile der Datenbank mit laufender Nummer; Zeilen ohne laufende Nummer (zum Beispiel Vorrichtungsreinigungen) zählen nicht. Davon haben ' + B('ts_bw') + ' Filter im gewählten Zeitraum das Kennzeichen „Blindwert: Ja“.</p>')),
 ('we', 'WE – Same-Day', tab('we', 'WE – Same-Day-Quote der Wareneingangsprüfung',
    'Anteil der Babtec-Aufträge der Wareneingangsprüfung, die noch am Tag ihrer Anlage technisch abgeschlossen wurden, nach Anlagedatum. Es wirken die Filter Jahr, Quartal und Monat. Im gewählten Zeitraum wurden ' + B('we_auf') + ' Aufträge angelegt; ' + B('we_sam') + ' davon sind nicht gewertet, weil sie erst im Sammelabschluss vom 04.–06.04.2026 geschlossen wurden.',
    tiles(tile('Same-Day-Quote', 'we_q', S('we_sd') + ' von ' + S('we_abg') + ' Aufträgen'), tile('Innerhalb 24 Stunden', 'we_q24', S('we_24') + ' Aufträge')),
    grid(card('Nach Anlagestunde', legend(('leg0', 'am Anlagetag abgeschlossen'), ('leg1', 'innerhalb 24 Stunden')) + chart('ch_we_stunde')),
         card('Nach Anlagemonat', legend(('leg0', 'am Anlagetag abgeschlossen'), ('leg1', 'innerhalb 24 Stunden')) + chart('ch_we_monat'))),
    card('Same-Day-Quote nach Anlagestunde und Wochentag', table('tb_we_matrix', ['Angelegt', 'Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag']), 'Je dunkler, desto höher die Quote; grau gesetzte Werte beruhen auf weniger als 10 Aufträgen'),
    grid(card('Nach Wochentag der Anlage', table('tb_we_tag', ['Wochentag'] + SD)), card('Vergleich der Prüfungsarten', table('tb_we_art', ['Prüfungsart'] + SD))),
    defs='<p><b>Auftrag:</b> eine Babtec-Auftragsnummer mit ihrer ersten Anlage und ihrem ersten technischen Abschluss. <b>Same-Day:</b> Abschluss am Kalendertag der Anlage. <b>Innerhalb 24 Stunden:</b> Abschluss höchstens 24 Stunden nach der Anlage. Aufträge aus dem Sammelabschluss vom 04.–06.04.2026 zählen nicht mit.</p>')),
]

REITER = [('uebersicht', 'Übersicht', ''), ('bsc', 'BSC', ''), ('termintreue', 'Termintreue', ''),
          ('budget', 'Budgeteinhaltung', 'budget plankosten auftragsquote vergabequote instandhaltungsquote'),
          ('wartung-kalibrierung', 'Prüfmittel', ''), ('ueberblick', 'Aufträge', ''), ('we', 'WE – Same-Day', ''), ('tecsa', 'TecSa', '')]
nav = ('  <div class="tabs" role="tablist" id="reiter">\n'
       + ''.join('    <button type="button" role="tab" data-tab="%s"%s aria-selected="%s">%s</button>\n'
                 % (i, ' data-sections="%s"' % g if g else '', 'true' if k == 0 else 'false', n) for k, (i, n, g) in enumerate(REITER)) + '  </div>\n\n')
html_tab = dict((i, h) for i, _, h in tabs)
reihe = ['bsc', 'termintreue', 'BUDGET', 'plankosten', 'auftragsquote', 'vergabequote', 'instandhaltungsquote', 'wartung-kalibrierung', 'tecsa', 'we']
abschnitte = [BUDGET if r == 'BUDGET' else html_tab[r] for r in reihe]
a, b = body.index('  <section class="tiles" id="kennzahlen">'), body.index('  <details id="definitionen">')
body = (body[:a] + nav + '  ' + UEBERSICHT + '\n\n  <section class="tab" id="ueberblick" hidden>\n  <h2>Aufträge</h2>\n' + body[a:b] + '  </section>\n\n'
        + '\n\n'.join('  ' + h for h in abschnitte) + '\n\n' + body[b:-len('</div>')]
        + '  <p class="fuss">Lokale Fassung. Neue Excel-Dateien in den Ordner legen: Läuft „Dashboard starten“, rechnet es neu und diese Seite lädt sich von selbst neu. Sonst „Aktualisieren“ ausführen und die Seite neu laden (F5).</p>\n</div>')

# --- Skripte ------------------------------------------------------------------------------------
scripts = re.findall(r'<script>(.*?)</script>', src, re.S)
assert len(scripts) == 3
scripts[0] = rep(scripts[0], "  sel.addEventListener('change', () => dash.setParams({ [name]: sel.value }));", '''  sel.addEventListener('change', () => {
    const set = { [name]: sel.value };
    // Monat und Quartal passen immer zusammen: ein Monat setzt sein Quartal, ein anderes Quartal löst den Monat.
    const q = document.querySelector('.lk select[data-param="quartal"]'), m = document.querySelector('.lk select[data-param="monat"]');
    if (name === 'monat' && sel.value && q) { set.quartal = String(Math.ceil(Number(sel.value) / 3)); q.value = set.quartal; }
    if (name === 'quartal' && sel.value && m && m.value && String(Math.ceil(Number(m.value) / 3)) !== sel.value) { set.monat = ''; m.value = ''; }
    dash.setParams(set);
  });''')
scripts[0] = rep(scripts[0], "sel.value = v == null ? (name === 'jahr' ? '2026' : '') : String(v);", "sel.value = v == null ? '' : String(v);")
scripts[0] = rep(scripts[0], "const hatVj = jahr !== 'alle' && jahr !== '2024';", "const hatVj = jahr !== 'alle' && auftraege.some((r) => r.erstellt.slice(0, 4) === String(Number(jahr) - 1));")
scripts[0] = rep(scripts[0], "const startY = jahr === 'alle' ? 2024 : Number(jahr)", "const startY = jahr === 'alle' ? Number(auftraege.reduce((m, r) => (r.erstellt < m ? r.erstellt : m), '9999').slice(0, 4)) : Number(jahr)")

tt = (L / 'termintreue.js').read_text(encoding='utf-8')   # bereits auf dem Stand des Dashboards

jahr_js = '''// Jahresauswahl aus den Daten aufbauen, damit neue Jahre ohne Änderung an dieser Datei erscheinen
(() => {
  const sel = document.querySelector('.lk select[data-param="jahr"]');
  const j = dash.jahre.slice().reverse();
  if (sel && j.length) {
    sel.replaceChildren(...j.map((y) => new Option(y, y)), new Option(j.length > 1 ? j[j.length - 1] + '–' + j[0] : 'alle Jahre', 'alle'));
    sel.value = dash.params().jahr;
  }
  const e = document.getElementById('lk-erzeugt');
  if (e && window.LK_ERZEUGT) e.textContent = window.LK_ERZEUGT.slice(8, 10) + '.' + window.LK_ERZEUGT.slice(5, 7) + '.' + window.LK_ERZEUGT.slice(0, 4) + ' ' + window.LK_ERZEUGT.slice(11);
})();'''

neuladen_js = '''// Neue Daten erkennen: aktualisieren.py schreibt nach jedem Lauf die kleine Datei stand.js mit einer neuen Kennung.
(() => {
  const pruefe = () => {
    const s = document.createElement('script');
    s.src = 'stand.js?' + Date.now();
    s.onload = () => { s.remove(); if (window.LK_STAND && window.LK_KENNUNG && window.LK_STAND !== window.LK_KENNUNG) location.reload(); };
    s.onerror = () => s.remove();
    document.head.append(s);
  };
  if (window.LK_KENNUNG) setInterval(pruefe, 5000);
})();'''

d3 = (L / 'vendor' / 'd3.min.js').read_text(encoding='utf-8')
js = [(L / 'shim.js').read_text(encoding='utf-8'), jahr_js, *scripts, (L / 'gemeinsam.js').read_text(encoding='utf-8'), tt, (L / 'abweichungen.js').read_text(encoding='utf-8')] + [(L / f).read_text(encoding='utf-8') for f in
      ('plankosten.js', 'auftragsquote.js', 'vergabequote.js', 'instandhaltungsquote.js', 'wartung.js', 'tecsa.js', 'we.js', 'bsc.js', 'uebersicht.js', 'tabs.js', 'extras.js')] + [neuladen_js]
for s in js:
    assert '</script' not in s
fehlt = '<div id="lk-fehlt" style="font-family:sans-serif;padding:24px" hidden><h2>Daten fehlen</h2><p>Die Datei <b>daten.js</b> wurde nicht gefunden. Sie muss im selben Ordner wie diese HTML-Datei liegen. Bitte <b>Dashboard starten.bat</b> oder <b>Aktualisieren.bat</b> ausführen.</p></div>'
html = ('<!DOCTYPE html>\n<html lang="de">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n<title>Labor-KPI-Dashboard</title>\n<style>'
        + tokens + css + '</style>\n</head>\n<body>\n' + fehlt + '\n' + body + '\n<script src="daten.js"></script>\n<script>' + d3 + '</script>\n'
        + '<script>if (!window.LK_DATEN) { document.getElementById("lk-fehlt").hidden = false; document.querySelector(".lk").hidden = true; }</script>\n'
        + '\n'.join('<script>\n' + s.strip() + '\n</script>' for s in js) + '\n</body>\n</html>\n')
OUT.write_text(html, encoding='utf-8')
print(OUT, len(html))
