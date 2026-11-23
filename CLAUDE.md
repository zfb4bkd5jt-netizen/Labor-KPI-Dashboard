# Labor-KPI-Dashboard – Übergabe an Claude Code

Stand: 23.11.2026, Version 1.2. Auftraggeber und Nutzer: Matthias, Laborleiter des physikalisch-technischen Labors (Thomas Group, rund 32 Mitarbeiter, Labore QLA, QLC, QLG, QLM). Sprache: Deutsch, du-Form.

Das Dashboard ersetzt den Power-BI-Bericht `QL.pbit` (Seiten HoQ_1_Termintreue, HoQ_2_… usw.). Es entstand in der Claude-App als Online-Dashboard; diese Übergabe enthält die eigenständige Offline-Fassung (eine HTML-Datei plus Python-Skript), mit der hier weitergearbeitet wird.

## Feste Regeln

- **Keine Personennamen ins Dashboard.** Personenbezogene Auswertungen (Buchungsquote je Mitarbeiter) bleiben außerhalb, bis die Mitbestimmung geklärt ist. In `daten.js` stehen keine Personen-Auswertungen; Namen können nur in freien Auftragsbezeichnungen vorkommen.
- **Firmendaten sind vertraulich.** Die Excel-Exporte und `daten.js` gehören nicht in Git und nicht in weitergegebene Pakete, außer Matthias sagt es ausdrücklich.
- **Ein neues Offline-Paket (ZIP zum Weitergeben) nur auf Auftrag.** Entwickelt wird am Quellcode; Pakete schnürt Matthias bei bestimmten Versionsständen.
- Version steht im Kopf des Dashboards (`<span id="version">`, gesetzt in `quellcode/bauen.py`). Aktuell 1.2. Versionen: 1.1 = Übergabe aus der Claude-App; 1.2 = Offline-Paket mit mitgeliefertem Python, robustere Start-Skripte (Dashboard-Inhalt unverändert).
- Texte im Dashboard sind Deutsch, sachlich, ohne Fachjargon von Power BI. Zahlen deutsch formatiert (1.234,5 %).

## Ordner

```
dashboard/     Laufende Fassung für den Arbeitsplatz
  Labor-KPI-Dashboard.html   erzeugt von quellcode/bauen.py, nicht von Hand ändern
  aktualisieren.py           liest die Excel-Exporte, schreibt daten.js und stand.js
  Dashboard starten.bat      öffnet das Dashboard und beobachtet den Ordner (--ueberwachen)
  Aktualisieren.bat          rechnet einmal neu
  LIESMICH.txt               Anleitung für Anwender
quellcode/     Woraus die HTML-Datei gebaut wird
  bauen.py                   baut dashboard/Labor-KPI-Dashboard.html (python bauen.py)
  vorlage.html               Kopf, Überblick-Reiter und die drei Inline-Skripte (Filter, Kennzahlen „Aufträge“)
  shim.js                    lokale Nachbildung der Laufzeit „dash“ (calc, draw, data, params, setParams, setLink, colors)
  *.js                       ein Skript je Reiter, siehe unten
  vendor/d3.min.js           d3 v7 (ISC-Lizenz)
werkzeuge/     Einmal-Skripte aus der Entwicklung; Pfade darin zeigen noch auf die alte Umgebung und müssen angepasst werden
  bau_pruefexcel.py          Prüf-Excel: rechnet alle BSC-Kennzahlen mit Excel-Formeln nach
  fuellen.py, grafik.py      füllen die drei KPI-Formblätter (Termintreue, Budgeteinhaltung, Qualitätslevel)
  altlasten.py               Liste alter, nie abgeschlossener Aufträge
logo/          Logo „Thomas | Labor“ (quer und gestapelt, hell und negativ)
portable/      PYTHON_VERSION: Python-Version für das Offline-Paket
build_portable.sh   baut das Offline-Paket mit mitgeliefertem Python (dist/…_portable_Windows.zip)
requirements.txt    pandas, openpyxl (für aktualisieren.py und das Offline-Paket)
.github/workflows/pruefen.yml   automatische Prüfung: HTML passt zum Quellcode, Paket bauen, unter Windows testen
```

Die Excel-Exporte legt Matthias selbst nach `dashboard/` (Dateinamen siehe LIESMICH.txt): LMS_Auftrag, LMS_Prüfgruppe, LMS_gebuchte_Stunden, manuelle_Daten, SAP_Instandhaltungskosten, Tabelle von Basis, TecSa_DB_Standardprüfung (freiwillig).

## Arbeitsablauf

1. Code in `quellcode/*.js` oder `quellcode/bauen.py` ändern.
2. `cd quellcode && python bauen.py` → schreibt `dashboard/Labor-KPI-Dashboard.html`.
3. Daten: `cd dashboard && python aktualisieren.py` (braucht pandas, openpyxl).
4. Prüfen im Browser (Datei öffnen genügt, kein Server nötig). Für automatische Tests eignet sich Playwright: Seite laden, auf Konsolenfehler achten, Kacheltexte auslesen.

**Offline-Paket:** `./build_portable.sh` (aktueller Commit) oder `./build_portable.sh v1.2` (Git-Tag) baut aus den eingecheckten Dateien von `dashboard/` plus dem offiziellen portablen Python für Windows (NuGet-Paket `python`, Version aus `portable/PYTHON_VERSION`) samt pandas und openpyxl ein ZIP. Auf dem Arbeitsplatz ist dann keine Python-Installation nötig; die `.bat`-Dateien nehmen zuerst `python\python.exe` im Ordner, sonst ein installiertes Python. Excel-Exporte und `daten.js` sind nicht in Git und kommen deshalb nie ins Paket. Weitergeben nur auf Auftrag (siehe Feste Regeln). Die HTML-Datei muss nach Änderungen am Quellcode neu gebaut und mit eingecheckt werden, sonst schlägt die automatische Prüfung fehl.

`bauen.py` arbeitet mit Textersetzungen (`rep(...)`), die genau einmal treffen müssen; eine fehlgeschlagene Ersetzung bricht mit AssertionError ab. Die Reiter werden dort mit kleinen Hilfsfunktionen (`tile`, `card`, `chart`, `table`, `tab`) aufgebaut; Übersicht, Termintreue-Kacheln, Abweichungsliste und Budget-Einstieg stehen als `UEBERSICHT`, `TT_KACHELN`, `TT_LISTE`, `BUDGET`.

Die Skripte folgen der Regel „ein Schreiber“: Nur `dash.draw(name, fn)` schreibt in Elemente mit `data-draw="name"`. Ausnahme: Klassen (`good`/`bad`) und `hidden` dürfen auch Hilfsskripte setzen. Der Shim zeichnet verborgene Reiter erst beim Öffnen.

## Reiter und Skripte

| Reiter | Abschnitt(e) | Skript |
|---|---|---|
| Übersicht (Start) | `uebersicht` | uebersicht.js (liest die Rechnung `bsc`) |
| BSC | `bsc` | bsc.js (Rechnung `bsc`, Tabelle mit Verlaufskurven) |
| Termintreue | `termintreue` | termintreue.js, abweichungen.js (Liste `tt_liste`) |
| Budgeteinhaltung | `budget`, `plankosten`, `auftragsquote`, `vergabequote`, `instandhaltungsquote` | plankosten.js, auftragsquote.js, vergabequote.js, instandhaltungsquote.js |
| Prüfmittel | `wartung-kalibrierung` | wartung.js |
| Aufträge | `ueberblick` | Inline-Skripte in vorlage.html |
| WE – Same-Day | `we` | we.js |
| TecSa | `tecsa` | tecsa.js |

Gemeinsam: `gemeinsam.js` (`window.LKsoll(schluessel)` liest SOLL/Ziel aus `bsc_vorgaben`, Ampelfarbe für Elemente mit `data-soll`), `tabs.js` (Reitergruppen über `data-sections`, Sprung über `data-ziel`, beim Drucken alle Reiter und Erläuterungen aufklappen), `extras.js` (Zahlenwerte an allen Diagrammen, Vollbild-Knopf, `window.LKhoehe`). `termintreue.js` stellt `window.LKline` bereit (Liniendiagramm mit optionaler SOLL-Linie `ref`, auch als Funktion).

## Kennzahlen (BSC)

Bezugszeitraum der Kacheln: letzter abgeschlossener Monat/Quartal/Jahr der Auswahl (Filter „Übersicht und BSC je“, Standard Quartal), Vergleich mit dem Zeitraum davor. Alles wird je Zeitraum aus Einzeldaten gerechnet, nicht als Mittel kleinerer Zeiträume. Manuelle Kennzahlen sind je Quartal erfasst (Monat übernimmt sein Quartal, Jahr = Mittel der Quartale).

**HoQ 1**
- Termintreue = Mittel(Reaktionszeit S, M, L) × g_reaktionszeit (0,5) + Pünktlichkeit × g_puenktlichkeit (0,5). SOLL ≥ 65 %.
- Budgeteinhaltung = je 0,25 × Erfüllungsgrad Plankosten, Erfüllungsgrad Vergabe, Erfüllungsgrad Auftragsquote, Erfüllungsgrad Instandhaltungsquote. SOLL ≥ 80 %. (Matthias hat SOLL und Gewichte als „zurückgestellt“ markiert.)
- Qualitätslevel = je 0,33 × Dienstleistungsquote, (100 − |Methodeneinsatz − 25|), (100 − Rückweisung). SOLL ≥ 80 %. Werte von Hand im Blatt BSC_Quartal; Neuaufbau geplant (siehe offene Punkte).

**HoQ 2**
- Reaktionszeit S (S_Babtec): Anteil der Babtec-Aufträge, deren schnellste Prüfgruppe ≤ 48 h nach Anlage abgeschlossen ist; Sammelabschluss 04.–06.04.2026 ausgenommen (Tage in BSC_Vorgaben). SOLL ≥ 90 %.
- Reaktionszeit M: Abschluss ≤ 14 Tage nach Bearbeitungsbeginn; ohne Bearbeitungsbeginn = nicht fristgerecht. SOLL ≥ 50 %.
- Reaktionszeit L: ≤ 70 Tage. SOLL noch offen.
- Pünktlichkeit M/L: Abschluss ≤ zugesagter Termin, Nenner nur Aufträge mit Termin. SOLL M ≥ 50 %, L ≥ 90 %. Pünktlichkeit = Mittel aus M und L.
- Plankostenerfüllung: Σ IST / Σ PLAN der abgeschlossenen M- und L-Aufträge; IST = gebuchte Stunden × Stundensatz (75 €, aus BSC_Vorgaben), PLAN = Auftragswert berechnet. Erfüllungsgrad = 100 − |Quote − 100|.
- Vergabequote = extern / (intern + extern) aus SAP (intern 94311000; extern 65001000, 63012000, 65602000, 65200000; Konten in BSC_Vorgaben), nach Buchungsmonat. Eigenleistung = 100 − Vergabequote. Erfüllungsgrad Vergabe = 100 %, solange Vergabequote ≤ 20 %; darüber Eigenleistung / 80 (Beispiel 30 % → 87,5 %).
- Auftragsquote = abgeschlossene / Soll-Aufträge (QLA, QLG, QLM; laufender Monat anteilig). Erfüllungsgrad = Quote / 100 %, **ohne Obergrenze** (Übererfüllung soll Schwächen ausgleichen). Ziel ohne Ampel.
- Instandhaltungsquote = Stunden auf Laboraufträge (S, M, L) und WE+FP / Soll-Stunden („bezahlte Leistung“). Ziel 65 %, Erfüllungsgrad ohne Obergrenze, ohne Ampel.
- Buchungsquote = alle gebuchten Stunden / Soll-Stunden (nicht in der BSC). Soll-Stunden = (Arbeitstage − Abwesenheitstage) × FTE des Monats (Blatt FTE_Monat) × 8. Urlaub/Krankheit zählen nicht zum IST.
- Rückweisung: SOLL ≤ 5 % (einziger Höchstwert).

Alle SOLL-, Ziel- und Gewichtungswerte kommen aus `manuelle_Daten.xlsx`, Blatt BSC_Vorgaben (Spalte B); fehlt ein Eintrag, gelten die Standardwerte in `bsc.js` (Objekt `V`) und `gemeinsam.js` (`STD`). Neue Schlüssel müssen in `aktualisieren.py` (`VORGABEN_ZAHL`/`VORGABEN_TEXT`) ergänzt werden.

Kontrollwerte (Datenstand 04.11.2026, Quartale 2026): Termintreue Q1 81,6 / Q2 74,2 / Q3 81,3 %; Budgeteinhaltung Q1 102,9 / Q2 100,7 / Q3 100,9 %; Qualitätslevel Q1/Q2 90,8 %. Q3: Reaktionszeit S 86,4 %, M 53,4 %, Pünktlichkeit M 85,1 %, L 97,6 %.

## Offene Punkte

- SOLL Reaktionszeit L (Matthias klärt).
- SOLL Dienstleistungsquote.
- Qualitätslevel neu aufbauen; Vorschlag: Prüfmittelüberwachung, Reklamationsfreiheit, Eignungsprüfungen, Dienstleistungsquote je ¼ – wartet auf die Datenlage.
- SOLL und Gewichte der Budgeteinhaltung (zurückgestellt).
- KPI-Formblätter nachziehen, sobald die Regeln fest sind (das Formblatt Budgeteinhaltung beschreibt noch die alte Eigenleistungsquote).
- SAP-Buchung Oktober und Abwesenheiten QLA klären.
- Das Online-Dashboard in der Claude-App ist inhaltlich auf dem Stand der Version 1.1 (1.2 änderte nur das Offline-Paket), wird aber nicht automatisch mitgezogen.
