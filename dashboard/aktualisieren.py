#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Labor-KPI-Dashboard: Daten aktualisieren.

Liest die Excel-Exporte aus LIMS, SAP und den manuellen Daten und schreibt daraus die Datei
"daten.js", die das Dashboard (Labor-KPI-Dashboard.html) beim Öffnen lädt.

Aufruf:   python aktualisieren.py                    einmal aktualisieren
          python aktualisieren.py --ueberwachen      Ordner beobachten: sobald eine Excel-Datei neu abgelegt
                                                     oder geändert wird, neu rechnen; das geöffnete Dashboard
                                                     lädt sich danach von selbst neu
          python aktualisieren.py "C:\\Pfad\\zum\\Ordner"   Exporte liegen in einem anderen Ordner

Ohne Pfad werden die Excel-Dateien im selben Ordner wie dieses Skript erwartet.

Voraussetzung: Python 3.9 oder neuer mit den Paketen pandas und openpyxl
               (einmalig: pip install pandas openpyxl)
"""
import json
import os
import re
import sys
import time
from pathlib import Path

try:
    import pandas as pd
    import openpyxl  # noqa: F401  (wird von pandas zum Lesen der Excel-Dateien gebraucht)
except ImportError as fehler:
    print('FEHLER: Es fehlt ein Python-Paket (' + str(fehler) + ').')
    print('Bitte einmalig in der Eingabeaufforderung ausführen:   pip install pandas openpyxl')
    sys.exit(2)

# ---------------------------------------------------------------------------------------------
# Einstellungen
# ---------------------------------------------------------------------------------------------
SKRIPT_ORDNER = Path(__file__).resolve().parent
ARGUMENTE = [a for a in sys.argv[1:] if not a.startswith('--')]
UEBERWACHEN = '--ueberwachen' in sys.argv[1:]
ORDNER = Path(ARGUMENTE[0]) if ARGUMENTE else SKRIPT_ORDNER             # Ordner mit den Excel-Exporten
AUSGABE = SKRIPT_ORDNER / 'daten.js'                                    # liegt neben der HTML-Datei
STAND = SKRIPT_ORDNER / 'stand.js'                                      # kleine Datei, an der das Dashboard neue Daten erkennt
PRUEF_ABSTAND = 5                                                       # Sekunden zwischen zwei Blicken in den Ordner

DATEIEN = {
    'auftrag': 'LMS_Auftrag.xlsx',
    'pruefgruppe': 'LMS_Prüfgruppe.xlsx',
    'stunden': 'LMS_gebuchte_Stunden.xlsx',
    'manuell': 'manuelle_Daten.xlsx',
    'sap_kosten': 'SAP_Instandhaltungskosten.xlsx',
    'sap_wk': 'Tabelle von Basis.xlsx',
    # Für TecSa wird die erste Datei genommen, die es gibt (Export oder die Datenbank selbst).
    # Hier darf auch ein vollständiger Pfad stehen, z. B. r'\\server\ordner\Datenbank.xlsm':
    'tecsa': ['TecSa_DB_Standardprüfung.xlsx', 'Datenbank.xlsm'],
}
FREIWILLIG = {'tecsa'}             # fehlt diese Datei, bleibt nur der Reiter TecSa leer
AB_JAHR = '2024-01-01'            # Aufträge und Prüfgruppen ab diesem Datum
LABORE = ['QLA', 'QLG', 'QLM']    # Labore mit Soll-Vorgaben
SAMMEL_VON, SAMMEL_BIS = '2026-04-04', '2026-04-07'   # Sammelabschluss alter Prüfgruppen (bis ausschließlich); wird aus dem Blatt BSC_Vorgaben überschrieben


def pfad(schluessel):
    namen = DATEIEN[schluessel]
    for name in ([namen] if isinstance(namen, str) else namen):
        p = ORDNER / name
        if p.exists():
            return p
    return None


def tag(x):
    return None if pd.isna(x) else x.strftime('%Y-%m-%d')


# ---------------------------------------------------------------------------------------------
# LMS_Auftrag: eine Zeile je Auftrag
# ---------------------------------------------------------------------------------------------
def lese_auftraege(datei):
    d = pd.read_excel(datei).drop_duplicates()
    k = 'Auftragsnummer formatiert'
    labore = d.dropna(subset=['Abkürzung']).groupby(k)['Abkürzung'].apply(lambda s: ';'.join(sorted(set(s))))
    o = d.drop(columns=['Abkürzung']).drop_duplicates(k).set_index(k)
    o['labore'] = labore
    o = o[o['Erstellt am'] >= AB_JAHR].reset_index()
    prio = {'S (48 h)': 'S', 'M (14 d)': 'M', 'L (70 d)': 'L', '0 (ohne Reaktionszeit)': '0'}
    rows = []
    for r in o.to_dict('records'):
        art = r['Art der Anfrage']
        rows.append({
            'auftrag': r[k], 'prio': prio.get(r['Art'], 'ohne'),
            'anfrageart': str(art).replace('_x000d_', '').strip() if pd.notna(art) else 'ohne Angabe',
            'labore': r['labore'] if isinstance(r['labore'], str) else '',
            'bezeichnung': r['Bezeichnung'],
            'erstellt': tag(r['Erstellt am']), 'abschluss': tag(r['Techn_ Abschluss']), 'termin': tag(r['Zugesagter Termin']),
            'wert': None if pd.isna(r['Auftragswert berechnet']) else round(float(r['Auftragswert berechnet']), 2),
            # Tage vom Bearbeitungsbeginn bis zum technischen Abschluss (negativ = Abschluss vor geplantem Beginn)
            'tage_ab_beginn': None if pd.isna(r['Techn_ Abschluss']) or pd.isna(r['Bearbeitungsbeginn'])
            else round((r['Techn_ Abschluss'] - r['Bearbeitungsbeginn']).total_seconds() / 86400, 2),
        })
    return rows


# ---------------------------------------------------------------------------------------------
# LMS_Prüfgruppe: abgeschlossene Prüfgruppen und Same-Day-Zählung je Auftrag
# ---------------------------------------------------------------------------------------------
def lese_pruefgruppen(datei):
    roh = pd.read_excel(datei)
    art = {'Wareneingangsprüfung': 'WE', 'Fertigungsprüfung': 'FP'}

    d = roh[(roh['Status'] == '8 - Prüfung abgeschlossen') & roh['Techn_ Abschluss'].notna() & roh['Babtech_Auftragsnummer'].notna()]
    d = d[d['Techn_ Abschluss'] >= AB_JAHR]
    pruefgruppen = [{
        'auftrag': r['Babtech_Auftragsnummer'], 'art': art.get(r['Babtec_Prüfungsart'], 'ohne'),
        'erstellt': r['Erstellt am'].strftime('%Y-%m-%dT%H:%M'), 'abschluss': r['Techn_ Abschluss'].strftime('%Y-%m-%dT%H:%M'),
        'dauer_h': round((r['Techn_ Abschluss'] - r['Erstellt am']).total_seconds() / 3600, 2),
    } for r in d.to_dict('records')]

    # je Auftrag: erste Anlage, erster technischer Abschluss
    a = roh[roh['Babtech_Auftragsnummer'].notna()].groupby('Babtech_Auftragsnummer').agg(
        erstellt=('Erstellt am', 'min'), abschluss=('Techn_ Abschluss', 'min'), art=('Babtec_Prüfungsart', 'first')).reset_index()
    a = a[a['erstellt'] >= AB_JAHR].copy()
    a['art'] = a['art'].map(art).fillna('ohne Angabe')
    a['sammel'] = (a['abschluss'] >= SAMMEL_VON) & (a['abschluss'] < SAMMEL_BIS)
    gewertet = a['abschluss'].notna() & ~a['sammel']
    a['abg'] = gewertet.astype(int)
    a['same'] = (gewertet & (a['abschluss'].dt.normalize() == a['erstellt'].dt.normalize())).astype(int)
    a['in24'] = (gewertet & ((a['abschluss'] - a['erstellt']) <= pd.Timedelta(hours=24))).astype(int)
    a['monat'] = a['erstellt'].dt.strftime('%Y-%m')
    a['wt'] = a['erstellt'].dt.dayofweek
    a['stunde'] = a['erstellt'].dt.hour
    g = a.groupby(['monat', 'wt', 'stunde', 'art']).agg(auftraege=('abg', 'size'), abgeschlossen=('abg', 'sum'), same_day=('same', 'sum'),
                                                        in24=('in24', 'sum'), sammel=('sammel', 'sum')).reset_index()
    we_sameday = [{c: (r[c] if c in ('monat', 'art') else int(r[c])) for c in g.columns} for r in g.to_dict('records')]
    return pruefgruppen, we_sameday


# ---------------------------------------------------------------------------------------------
# LMS_gebuchte_Stunden: je Auftrag und je Monat/Labor/Kontierungstyp
# ---------------------------------------------------------------------------------------------
def kontierungstyp(k, n):
    if k.startswith('URLAUB') or k.startswith('URALAUB'):
        return 'Urlaub'                     # auch Schreibvarianten wie "Urlaub_xy"
    if k == 'KRANKHEIT':
        return 'Krankheit'
    if k in ('KALIBRIERTÄTIGKEITEN', 'CALIBRATION'):
        return 'Kalibrierung'
    if k == 'WARTUNGSTÄTIGKEITEN':
        return 'Wartung'
    if k == 'WE+FP':
        return 'WE+FP'
    if 'TM-' in n and 'OR' in n:
        return 'Laborauftrag'
    return 'Sonstiges'


def lese_stunden(datei):
    h = pd.read_excel(datei)
    txt = h['Sonstiges/Arbeitspaket/Auftrag'].astype(str).str.strip()
    nr = txt.str.split(' ').str[0].str.split('+').str[0]            # Auftragsnummer ohne Teilauftrag hinter dem "+"
    ist_auftrag = nr.str.upper().str.contains('TM-') & nr.str.upper().str.contains('OR')

    a = h[ist_auftrag].assign(auftrag=nr[ist_auftrag], labor=h['Laborbereich'].fillna('ohne'))
    g = a.groupby(['auftrag', 'labor']).agg(stunden=('Anzahl', 'sum'), buchungen=('Anzahl', 'size'),
                                            erste=('Datum', 'min'), letzte=('Datum', 'max')).reset_index()
    stunden_auftrag = [{'auftrag': r.auftrag, 'labor': r.labor, 'stunden': round(float(r.stunden), 2), 'buchungen': int(r.buchungen),
                        'erste': r.erste.strftime('%Y-%m-%d'), 'letzte': r.letzte.strftime('%Y-%m-%d')} for r in g.itertuples()]

    m = h.copy()
    m['typ'] = [kontierungstyp(k, n) for k, n in zip(txt.str.upper(), nr.str.upper())]
    m['monat'] = m['Datum'].dt.strftime('%Y-%m')
    m = m[m['Laborbereich'].isin(LABORE) & (m['monat'] >= '2025-01')]
    g = m.groupby(['monat', 'Laborbereich', 'typ'])['Anzahl'].agg(['sum', 'size']).reset_index()
    stunden_monat = [{'monat': r['monat'], 'labor': r['Laborbereich'], 'typ': r['typ'], 'stunden': round(float(r['sum']), 2),
                      'buchungen': int(r['size'])} for r in g.to_dict('records')]
    return stunden_auftrag, stunden_monat


# ---------------------------------------------------------------------------------------------
# manuelle_Daten: Soll-Aufträge und Soll-Stunden (ohne Personennamen)
# ---------------------------------------------------------------------------------------------
def lese_manuell(datei):
    d = pd.read_excel(datei, sheet_name='Aufträge_pro_Bereich')
    d = d[(d['YYYY-MM'] >= AB_JAHR) & (d['YYYY-MM'] <= '2030-12-31')]
    soll_auftraege = [{'monat': r['YYYY-MM'].strftime('%Y-%m'), 'labor': lab, 'soll': int(r[lab])}
                      for r in d.to_dict('records') for lab in LABORE if lab in r and pd.notna(r[lab])]

    blaetter = pd.ExcelFile(datei).sheet_names
    ab = pd.read_excel(datei, sheet_name='Abwesenheit_SF')
    at = pd.read_excel(datei, sheet_name='Arbeitstage').iloc[:, :2].dropna()
    tage = dict(zip(at['Monat'].astype(str), at['Arbeitstage']))
    # FTE je Mitarbeiter und Monat aus Blatt "FTE_Monat" (gleiche Area und gleicher Name wie in Abwesenheit_SF).
    # Fehlt das Blatt, ein Monat oder ist eine Zelle leer, gilt die feste FTE aus Abwesenheit_SF.
    fte_monat = None
    if 'FTE_Monat' in blaetter:
        fm = pd.read_excel(datei, sheet_name='FTE_Monat')
        fm.columns = [str(c) for c in fm.columns]
        fte_monat = fm.drop_duplicates(['Area', 'Name']).set_index(['Area', 'Name'])
    ab.columns = [str(c) for c in ab.columns]
    schluessel = list(zip(ab['Area'], ab['Name'])) if 'Name' in ab.columns else None
    soll_stunden = []
    for m in [c for c in ab.columns if c not in ('Area', 'Name', 'FTE')]:
        if m not in tage:
            continue
        fte = pd.to_numeric(ab['FTE'], errors='coerce')
        if fte_monat is not None and schluessel is not None and m in fte_monat.columns:
            vorgabe = pd.to_numeric(fte_monat[m].reindex(schluessel), errors='coerce')
            vorgabe.index = ab.index
            fte = vorgabe.fillna(fte)
        fte = fte.fillna(0)
        werte = pd.to_numeric(ab[m], errors='coerce')
        for lab in LABORE:
            im_labor = (ab['Area'] == lab) & (fte > 0)             # nur Personen, die in diesem Monat im Labor sind
            if not im_labor.any():
                continue
            f, w = fte[im_labor], werte[im_labor]
            abw = w.fillna(0).clip(upper=tage[m])                   # Abwesenheit höchstens so viele Tage wie Arbeitstage
            soll_stunden.append({
                'monat': m, 'labor': lab, 'personen': int(im_labor.sum()), 'fte': round(float(f.sum()), 3),
                'arbeitstage': int(tage[m]), 'abwesenheit_erfasst': int(w.notna().sum()),
                'brutto_stunden': round(float((tage[m] * f * 8).sum()), 1),
                'abwesenheit_stunden': round(float((abw * f * 8).sum()), 1),
                'soll_stunden': round(float(((tage[m] - abw) * f * 8).sum()), 1)})
    return soll_auftraege, soll_stunden, *lese_bsc(datei, blaetter)


# Blatt BSC_Vorgaben: Kennzahl -> (Schlüssel, Faktor). SOLL und Zielwerte stehen als Anteil im Blatt und werden zu Prozent.
VORGABEN_ZAHL = {
    'SOLL Termintreue': ('soll_termintreue', 100), 'SOLL Budgeteinhaltung': ('soll_budgeteinhaltung', 100), 'SOLL Qualitätslevel': ('soll_qualitaetslevel', 100),
    'Zielwert Methodeneinsatz': ('ziel_methodeneinsatz', 100), 'Zielwert Plankostenerfüllung': ('ziel_plankosten', 100),
    'Zielwert Auftragsquote': ('ziel_auftragsquote', 100), 'Zielwert Instandhaltungsquote': ('ziel_instandhaltungsquote', 100),
    'Maximale Vergabequote': ('max_vergabequote', 100), 'Stundensatz': ('stundensatz', 1),
    'SOLL Reaktionszeit S': ('soll_reaktion_s', 100), 'SOLL Reaktionszeit M': ('soll_reaktion_m', 100), 'SOLL Pünktlichkeit M': ('soll_puenktlich_m', 100), 'SOLL Pünktlichkeit L': ('soll_puenktlich_l', 100), 'Maximale Rückweisung': ('max_rueckweisung', 100),
    'Gewichtung Reaktionszeit': ('g_reaktionszeit', 1), 'Gewichtung Pünktlichkeit': ('g_puenktlichkeit', 1),
    'Gewichtung Plankostenerfüllung': ('g_plankosten', 1), 'Gewichtung Vergabequote': ('g_vergabequote', 1),
    'Gewichtung Auftragsquote': ('g_auftragsquote', 1), 'Gewichtung Instandhaltungsquote': ('g_instandhaltungsquote', 1),
    'Gewichtung Dienstleistungsquote': ('g_dienstleistungsquote', 1), 'Gewichtung Methodeneinsatz': ('g_methodeneinsatz', 1), 'Gewichtung Rückweisung': ('g_rueckweisung', 1),
}
VORGABEN_TEXT = {'Sachkonten extern': 'sachkonten_extern', 'Sachkonten intern': 'sachkonten_intern',
                 'Sammelabschluss Babtec von': 'sammel_von', 'Sammelabschluss Babtec bis': 'sammel_bis'}


def lese_bsc(datei, blaetter):
    """Von Hand gepflegte BSC-Kennzahlen je Quartal und die Vorgaben (SOLL, Zielwerte, Gewichtungen, feste Werte)."""
    quartal, vorgaben = [], []
    if 'BSC_Quartal' in blaetter:
        q = pd.read_excel(datei, sheet_name='BSC_Quartal')
        pz = lambda v: None if pd.isna(v) else round(100 * float(v), 2)           # Anteil -> Prozent
        quartal = [{'quartal': str(r['Quartal']).strip(), 'dienstleistungsquote': pz(r['Dienstleistungsquote']),
                    'methodeneinsatz': pz(r['Methodeneinsatz']), 'rueckweisung': pz(r['Rückweisung'])}
                   for r in q.to_dict('records') if isinstance(r['Quartal'], str)]
    if 'BSC_Vorgaben' in blaetter:
        v = pd.read_excel(datei, sheet_name='BSC_Vorgaben')
        for r in v.to_dict('records'):
            k, w = str(r['Kennzahl']).strip(), r['Wert']
            if pd.isna(w):
                continue
            if k in VORGABEN_ZAHL:
                vorgaben.append({'schluessel': VORGABEN_ZAHL[k][0], 'kennzahl': k, 'wert': round(float(w) * VORGABEN_ZAHL[k][1], 4), 'text': None})
            elif k in VORGABEN_TEXT:
                if hasattr(w, 'strftime'):
                    w = w.strftime('%Y-%m-%d')                                      # von Excel in ein Datum umgewandelt
                elif isinstance(w, float) and w.is_integer():
                    w = int(w)                                                      # einzelnes Sachkonto als Zahl
                vorgaben.append({'schluessel': VORGABEN_TEXT[k], 'kennzahl': k, 'wert': None, 'text': str(w).strip()})
    return quartal, vorgaben


# ---------------------------------------------------------------------------------------------
# SAP_Instandhaltungskosten: je Buchungsmonat, Auftragsart, Sachkonto, Arbeitsplatz
# ---------------------------------------------------------------------------------------------
def lese_sap_kosten(datei):
    d = pd.read_excel(datei)
    ist = 'Istkosten (übergreifende Währung)'
    d['monat'] = d['Geschäftsjahr'].astype(str) + '-' + d['Buchungsmonat'].astype(str).str.zfill(2)
    d['beginn_monat'] = pd.to_datetime(d['Terminiertes Beginndatum']).dt.strftime('%Y-%m')
    g = d.groupby(['monat', 'beginn_monat', 'Instandhaltungsauftragsart', 'Sachkonto', 'Verantwortlicher Arbeitsplatz'], dropna=False)[ist] \
         .agg(['sum', 'size']).reset_index()
    return [{'monat': r['monat'], 'beginn_monat': r['beginn_monat'], 'auftragsart': r['Instandhaltungsauftragsart'],
             'sachkonto': str(r['Sachkonto']), 'arbeitsplatz': r['Verantwortlicher Arbeitsplatz'],
             'kosten': round(float(r['sum']), 2), 'positionen': int(r['size'])} for r in g.to_dict('records')]


# ---------------------------------------------------------------------------------------------
# Tabelle von Basis (SAP): Wartung (ZLB3) und Kalibrierung (ZLB4)
# ---------------------------------------------------------------------------------------------
def lese_wartung_kalibrierung(datei):
    d = pd.read_excel(datei)
    d = d[d['Auftragsart'].isin(['ZLB3', 'ZLB4'])].copy()
    d['art'] = d['Auftragsart'].map({'ZLB3': 'Wartung', 'ZLB4': 'Kalibrierung'})
    kt = d['Kurztext'].fillna('').astype(str).str.lower()
    d['ie'] = ['' if a == 'Wartung' else 'extern' if 'extern' in k else 'intern' if 'intern' in k else 'ohne Angabe' for a, k in zip(d['art'], kt)]
    d['bezeichnung'] = d['Bezeichnung'].fillna('ohne Bezeichnung')
    stand = d['Istendtermin'].max()

    abg = d[d['Istendtermin'] >= AB_JAHR].copy()
    abg['monat'] = abg['Istendtermin'].dt.strftime('%Y-%m')
    abg['p'] = (abg['Istendtermin'] <= abg['Eckendtermin']).astype(int)      # pünktlich: Ist-Ende bis zum Eckendtermin
    g = abg.groupby(['monat', 'art', 'ie', 'bezeichnung']).agg(anzahl=('Auftrag', 'size'), puenktlich=('p', 'sum')).reset_index()
    abgeschlossen = [{'monat': r['monat'], 'art': r['art'], 'ie': r['ie'], 'bezeichnung': r['bezeichnung'],
                      'anzahl': int(r['anzahl']), 'puenktlich': int(r['puenktlich'])} for r in g.to_dict('records')]

    off = d[d['Istendtermin'].isna() & (d['Eckendtermin'] < stand)]
    offen = [{'auftrag': str(r['Auftrag']), 'art': r['art'], 'ie': r['ie'], 'bezeichnung': r['bezeichnung'],
              'kurztext': r['Kurztext'] if isinstance(r['Kurztext'], str) else '',
              'eckende': r['Eckendtermin'].strftime('%Y-%m-%d'), 'freigegeben': bool(pd.notna(r['Freigabe Ist'])),
              'tage_ueber': int((stand - r['Eckendtermin']).days)} for r in off.to_dict('records')]
    return abgeschlossen, offen


# ---------------------------------------------------------------------------------------------
# TecSa: Datenbank der Standardprüfungen
# ---------------------------------------------------------------------------------------------
MONATE = {'Januar': 1, 'Februar': 2, 'März': 3, 'April': 4, 'Mai': 5, 'Juni': 6, 'Juli': 7, 'August': 8,
          'September': 9, 'Oktober': 10, 'November': 11, 'Dezember': 12}


def tecsa_datum(s):
    """Text wie "Mittwoch, 19. März 2025" oder ein echtes Excel-Datum."""
    if isinstance(s, pd.Timestamp):
        return s
    m = re.search(r'(\d{1,2})\.\s*(\w+)\s+(\d{4})', str(s))
    if m and m.group(2) in MONATE:
        return pd.Timestamp(int(m.group(3)), MONATE[m.group(2)], int(m.group(1)))
    return pd.to_datetime(s, errors='coerce', dayfirst=True)


def lese_tecsa(datei):
    xl = pd.ExcelFile(datei)
    blatt = 'DB Standardprüfung' if 'DB Standardprüfung' in xl.sheet_names else xl.sheet_names[0]
    kopf = pd.read_excel(xl, sheet_name=blatt, header=None, nrows=30)
    zeile = next(i for i in range(len(kopf)) if 'LfdNr' in [str(v).strip() for v in kopf.iloc[i].tolist()])   # Kopfzeile suchen
    d = pd.read_excel(xl, sheet_name=blatt, header=zeile)
    d['LfdNr'] = pd.to_numeric(d['LfdNr'], errors='coerce')
    d = d[d['LfdNr'].notna() & (d['LfdNr'] > 0)].copy()             # ein Filter = eine laufende Nummer
    d['dt'] = d['Datum'].map(tecsa_datum)
    d = d[d['dt'].notna()]
    d['datum'] = d['dt'].dt.strftime('%Y-%m-%d')
    d['produkt'] = d['Produkt'].fillna('-').astype(str).str.strip().replace({'-': 'ohne Produkt'})
    d['art'] = d['FP/WE'].where(d['FP/WE'].isin(['FP', 'WE']), 'ohne Angabe')
    d['auswertung'] = (d['Auswertung'].fillna('ohne Angabe').astype(str).str.replace('_x000D_\n', ' ').str.replace('\n', ' ')
                       .str.replace('_', ' ').str.replace(r'\s+', ' ', regex=True).str.strip())
    d['blindwert'] = d['Blindwert(ja/nein)'].astype(str).str.strip().str.lower().eq('ja')
    g = d.groupby(['datum', 'produkt', 'art', 'auswertung', 'blindwert']).size().reset_index(name='filter')
    return [{'datum': r['datum'], 'produkt': r['produkt'], 'art': r['art'], 'auswertung': r['auswertung'],
             'blindwert': bool(r['blindwert']), 'filter': int(r['filter'])} for r in g.to_dict('records')]


# ---------------------------------------------------------------------------------------------
def schreibe(datei, text):
    """Erst in eine Hilfsdatei schreiben, dann umbenennen: das Dashboard sieht nie eine halb geschriebene Datei."""
    tmp = datei.with_suffix(datei.suffix + '.tmp')
    tmp.write_text(text, encoding='utf-8')
    os.replace(tmp, datei)


def aktualisiere():
    """Liest alle Exporte und schreibt daten.js. Rückgabe True bei Erfolg; bei einem Fehler bleibt der alte Stand erhalten."""
    global SAMMEL_VON, SAMMEL_BIS
    print('Exporte aus:', ORDNER)
    fehlend = [str(DATEIEN[k]) for k in DATEIEN if k not in FREIWILLIG and pfad(k) is None]
    if fehlend:
        print('\nFEHLER: Diese Dateien fehlen im Ordner:')
        for f in fehlend:
            print('  -', f)
        print('\nEs wurde nichts geändert.')
        return False

    daten = {}

    def manuell():
        global SAMMEL_VON, SAMMEL_BIS
        daten.update(zip(('soll_auftraege', 'soll_stunden', 'bsc_manuell', 'bsc_vorgaben'), lese_manuell(pfad('manuell'))))
        vg = {r['schluessel']: r['text'] for r in daten['bsc_vorgaben'] if r['text']}
        if vg.get('sammel_von') and vg.get('sammel_bis'):                         # Sammelabschluss aus dem Blatt BSC_Vorgaben
            SAMMEL_VON = vg['sammel_von'][:10]
            SAMMEL_BIS = (pd.Timestamp(vg['sammel_bis'][:10]) + pd.Timedelta(days=1)).strftime('%Y-%m-%d')

    def tecsa():
        if pfad('tecsa') is None:
            print('    (keine TecSa-Datei im Ordner - der Reiter TecSa bleibt leer)')
            daten.update(tecsa=[])
        else:
            daten.update(tecsa=lese_tecsa(pfad('tecsa')))

    schritte = [
        ('manuelle_Daten', manuell),                            # zuerst: liefert die Vorgaben für die anderen Schritte
        ('LMS_Auftrag', lambda: daten.update(auftraege=lese_auftraege(pfad('auftrag')))),
        ('LMS_Prüfgruppe', lambda: daten.update(zip(('pruefgruppen', 'we_sameday'), lese_pruefgruppen(pfad('pruefgruppe'))))),
        ('LMS_gebuchte_Stunden', lambda: daten.update(zip(('stunden_auftrag', 'stunden_monat'), lese_stunden(pfad('stunden'))))),
        ('SAP_Instandhaltungskosten', lambda: daten.update(sap_kosten=lese_sap_kosten(pfad('sap_kosten')))),
        ('Tabelle von Basis', lambda: daten.update(zip(('wk_abgeschlossen', 'wk_offen'), lese_wartung_kalibrierung(pfad('sap_wk'))))),
        ('TecSa', tecsa),
    ]
    for name, schritt in schritte:
        print('  lese', name, '...', flush=True)
        try:
            schritt()
        except PermissionError:
            print('\nFEHLER:', name, 'ist gesperrt. Bitte die Datei in Excel schließen. Es wurde nichts geändert.')
            return False
        except Exception as e:                                  # verständliche Meldung statt langem Fehlertext
            print('\nFEHLER beim Lesen von', name + ':', repr(e))
            print('Vermutlich hat sich der Aufbau der Datei geändert (Spaltenname, Blattname). Es wurde nichts geändert.')
            return False

    jetzt = pd.Timestamp.now()
    erzeugt, kennung = jetzt.strftime('%Y-%m-%d %H:%M'), jetzt.strftime('%Y%m%d%H%M%S')
    schreibe(AUSGABE, '// Erzeugt von aktualisieren.py am ' + erzeugt + ' - nicht von Hand ändern.\n'
             'window.LK_ERZEUGT = ' + json.dumps(erzeugt) + ';\n'
             'window.LK_KENNUNG = ' + json.dumps(kennung) + ';\n'
             'window.LK_DATEN = ' + json.dumps(daten, ensure_ascii=False, separators=(',', ':')) + ';\n')
    schreibe(STAND, 'window.LK_STAND = ' + json.dumps(kennung) + ';\n')      # daran erkennt das geöffnete Dashboard neue Daten
    print('\nFertig:', AUSGABE, '(%.1f MB)' % (AUSGABE.stat().st_size / 1e6))
    for k, v in daten.items():
        print('  %-18s %7d Zeilen' % (k, len(v)))
    return True


def fingerabdruck():
    """Änderungszeit und Größe aller Excel-Dateien; ändert sich etwas davon, wird neu gerechnet."""
    werte = []
    for k in DATEIEN:
        p = pfad(k)
        if p is not None:
            try:
                s = p.stat()
                werte.append((str(p), s.st_mtime_ns, s.st_size))
            except OSError:
                werte.append((str(p), 0, 0))
    return tuple(werte)


def ueberwache():
    print('\nDer Ordner wird beobachtet. Dieses Fenster offen lassen; zum Beenden schließen oder Strg+C drücken.')
    letzter = fingerabdruck()
    try:
        while True:
            time.sleep(PRUEF_ABSTAND)
            jetzt = fingerabdruck()
            if jetzt == letzter:
                continue
            time.sleep(PRUEF_ABSTAND)                           # warten, bis die Datei fertig kopiert ist
            if fingerabdruck() != jetzt:
                continue                                        # wird noch geschrieben, beim nächsten Durchlauf erneut prüfen
            print('\n' + time.strftime('%H:%M:%S') + '  Geänderte Datei erkannt, rechne neu ...')
            if aktualisiere():
                print('Das geöffnete Dashboard lädt sich in wenigen Sekunden neu.')
            letzter = jetzt
            print('\nDer Ordner wird weiter beobachtet ...')
    except KeyboardInterrupt:
        print('\nBeobachtung beendet.')


def main():
    print('Labor-KPI-Dashboard: Daten aktualisieren')
    ok = aktualisiere()
    if UEBERWACHEN:
        ueberwache()
        return 0
    if ok:
        print('\nJetzt Labor-KPI-Dashboard.html im Browser öffnen oder neu laden (F5).')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
