# Baut die Prüf-Excel: leitet die BSC-Kennzahlen für ein Quartal mit sichtbaren Excel-Formeln aus den Rohexporten her.
import sys, re
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter as L
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.comments import Comment

EXP = '/home/claude/lab/lokal/test_exporte/'
OUT = sys.argv[1]
VON, BIS = pd.Timestamp('2026-04-01'), pd.Timestamp('2026-06-30')
MONATE = [202604, 202605, 202606]
QUARTAL = '2026-Q2'

F = 'Arial'
f_norm = Font(name=F, size=10)
f_blau = Font(name=F, size=10, color='0000FF')
f_gruen = Font(name=F, size=10, color='008000')
f_kopf = Font(name=F, size=10, bold=True, color='FFFFFF')
f_titel = Font(name=F, size=14, bold=True)
f_fett = Font(name=F, size=10, bold=True)
f_klein = Font(name=F, size=9, italic=True, color='555555')
fill_roh = PatternFill('solid', fgColor='5B6B7F')     # Spalte aus dem Export
fill_form = PatternFill('solid', fgColor='1F6F43')    # Spalte mit Formel
fill_gelb = PatternFill('solid', fgColor='FFF2CC')
fill_hell = PatternFill('solid', fgColor='EEF3F8')
duenn = Side(style='thin', color='BBBBBB')
rahmen = Border(top=duenn, bottom=duenn, left=duenn, right=duenn)
wrap = Alignment(wrap_text=True, vertical='top')
PCT = '0.0%'
DT = 'DD.MM.YYYY HH:MM'
D = 'DD.MM.YYYY'
NUM2 = '#,##0.00'
EUR = '#,##0 "€";-#,##0 "€";"-"'

wb = Workbook()

def kopf(ws, spalten, zeile=1):
    """spalten: Liste (Titel, Art 'roh'|'formel', Breite, Hinweis)"""
    for i, (t, art, br, hinweis) in enumerate(spalten, 1):
        c = ws.cell(zeile, i, t)
        c.font = f_kopf; c.fill = fill_roh if art == 'roh' else fill_form
        c.alignment = Alignment(wrap_text=True, vertical='center')
        ws.column_dimensions[L(i)].width = br
        if hinweis:
            c.comment = Comment(hinweis, 'Prüf-Excel')
    ws.row_dimensions[zeile].height = 42
    ws.freeze_panes = ws.cell(zeile + 1, 1)

def zelle(ws, r, c, v, fmt=None, font=None):
    x = ws.cell(r, c, v)
    x.font = font or f_norm
    if fmt: x.number_format = fmt
    return x

# ---------------------------------------------------------------------------------------- Vorgaben
vg = wb.active; vg.title = 'Vorgaben'
md = EXP + 'manuelle_Daten.xlsx'
bv = pd.read_excel(md, sheet_name='BSC_Vorgaben')
bvw = dict(zip(bv['Kennzahl'].astype(str).str.strip(), bv['Wert']))
at = pd.read_excel(md, sheet_name='Arbeitstage').iloc[:, :2].dropna()
tage = dict(zip(at['Monat'].astype(str), at['Arbeitstage']))
apb = pd.read_excel(md, sheet_name='Aufträge_pro_Bereich')
apb['m'] = apb['YYYY-MM'].dt.year * 100 + apb['YYYY-MM'].dt.month

vg['A1'] = 'Vorgaben und Parameter'; vg['A1'].font = f_titel
vg['A2'] = 'Blaue Werte sind Eingaben. Sie stammen aus den manuellen Daten (Blatt BSC_Vorgaben, Arbeitstage, Aufträge_pro_Bereich) bzw. aus den festen Regeln des Dashboards. Ändert man sie hier, rechnet die ganze Mappe neu.'
vg['A2'].font = f_klein; vg['A2'].alignment = wrap; vg.merge_cells('A2:D2'); vg.row_dimensions[2].height = 40
for col, w in zip('ABCD', (38, 18, 14, 70)):
    vg.column_dimensions[col].width = w
N = {}   # Name -> Zellbezug
zeilen = [
    ('Zeitraum von', VON.to_pydatetime(), D, 'Erster Tag des geprüften Quartals', 'von'),
    ('Zeitraum bis', BIS.to_pydatetime(), D, 'Letzter Tag des geprüften Quartals', 'bis'),
    ('Frist S (Stunden)', 48, '0', 'Reaktionszeit S: Prüfgruppe höchstens so viele Stunden nach Anlage abgeschlossen', 'frist_s'),
    ('Frist M (Tage)', 14, '0', 'Reaktionszeit M: Abschluss höchstens so viele Tage nach Bearbeitungsbeginn', 'frist_m'),
    ('Frist L (Tage)', 70, '0', 'Reaktionszeit L: Abschluss höchstens so viele Tage nach Bearbeitungsbeginn', 'frist_l'),
    ('Sammelabschluss Babtec von', pd.Timestamp(str(bvw.get('Sammelabschluss Babtec von', '2026-04-04'))[:10]).to_pydatetime(), D, 'Prüfgruppen, die an diesen Tagen abgeschlossen wurden, werden nicht gewertet', 'sammel_von'),
    ('Sammelabschluss Babtec bis', pd.Timestamp(str(bvw.get('Sammelabschluss Babtec bis', '2026-04-06'))[:10]).to_pydatetime(), D, '', 'sammel_bis'),
    ('Stundensatz', float(bvw.get('Stundensatz', 75)), '#,##0.00 "€"', 'IST-Kosten der Plankostenerfüllung = gebuchte Stunden × Stundensatz', 'satz'),
    ('Stunden je Arbeitstag', 8, '0', 'für die Soll-Stunden', 'h_tag'),
    ('Zielwert Plankostenerfüllung', float(bvw['Zielwert Plankostenerfüllung']), PCT, 'Erfüllungsgrad = 100 % − |Plankostenerfüllung − Zielwert|', 'ziel_pk'),
    ('Maximale Vergabequote', float(bvw['Maximale Vergabequote']), PCT, 'SOLL der Eigenleistungsquote = 100 % − maximale Vergabequote', 'max_vq'),
    ('Zielwert Auftragsquote', float(bvw.get('Zielwert Auftragsquote', 1)), PCT, 'Erfüllungsgrad = Auftragsquote / Zielwert, ohne Obergrenze', 'ziel_aq'),
    ('Zielwert Instandhaltungsquote', float(bvw.get('Zielwert Instandhaltungsquote', 0.65)), PCT, 'Erfüllungsgrad = Instandhaltungsquote / Zielwert, ohne Obergrenze', 'ziel_iq'),
    ('Zielwert Methodeneinsatz', float(bvw['Zielwert Methodeneinsatz']), PCT, 'Qualitätslevel bewertet die Abweichung vom Zielwert', 'ziel_me'),
    ('Gewichtung Reaktionszeit', float(bvw['Gewichtung Reaktionszeit']), '0.00', 'Termintreue', 'g_rz'),
    ('Gewichtung Pünktlichkeit', float(bvw['Gewichtung Pünktlichkeit']), '0.00', 'Termintreue', 'g_pu'),
    ('Gewichtung Plankostenerfüllung', float(bvw['Gewichtung Plankostenerfüllung']), '0.00', 'Budgeteinhaltung', 'g_pk'),
    ('Gewichtung Vergabequote', float(bvw['Gewichtung Vergabequote']), '0.00', 'Budgeteinhaltung (wirkt auf die Eigenleistungsquote)', 'g_vq'),
    ('Gewichtung Auftragsquote', float(bvw['Gewichtung Auftragsquote']), '0.00', 'Budgeteinhaltung', 'g_aq'),
    ('Gewichtung Instandhaltungsquote', float(bvw['Gewichtung Instandhaltungsquote']), '0.00', 'Budgeteinhaltung', 'g_iq'),
    ('Gewichtung Dienstleistungsquote', float(bvw['Gewichtung Dienstleistungsquote']), '0.00', 'Qualitätslevel', 'g_dl'),
    ('Gewichtung Methodeneinsatz', float(bvw['Gewichtung Methodeneinsatz']), '0.00', 'Qualitätslevel', 'g_me'),
    ('Gewichtung Rückweisung', float(bvw['Gewichtung Rückweisung']), '0.00', 'Qualitätslevel', 'g_rw'),
    ('SOLL Termintreue', float(bvw['SOLL Termintreue']), PCT, 'Mindestwert', 'soll_tt'),
    ('SOLL Budgeteinhaltung', float(bvw['SOLL Budgeteinhaltung']), PCT, 'Mindestwert', 'soll_be'),
    ('SOLL Qualitätslevel', float(bvw['SOLL Qualitätslevel']), PCT, 'Mindestwert', 'soll_ql'),
]
r = 4
for t, c in (('Parameter', 'A'), ('Wert', 'B'), ('', 'C'), ('Bedeutung', 'D')):
    vg[c + '3'] = t; vg[c + '3'].font = f_fett
for name, wert, fmt, bed, key in zeilen:
    zelle(vg, r, 1, name); zelle(vg, r, 2, wert, fmt, f_blau); zelle(vg, r, 4, bed).alignment = wrap
    N[key] = "Vorgaben!$B$%d" % r
    r += 1
r += 1
vg.cell(r, 1, 'Sachkonten extern (Vergabequote)').font = f_fett
ext = [k for k in re.split(r'[;,\s]+', str(bvw.get('Sachkonten extern', '65001000; 63012000; 65602000; 65200000'))) if k]
intn = [k for k in re.split(r'[;,\s]+', str(bvw.get('Sachkonten intern', '94311000'))) if k]
r += 1; e0 = r
for k in ext:
    zelle(vg, r, 1, k, '@', f_blau); r += 1
N['ext'] = "Vorgaben!$A$%d:$A$%d" % (e0, r - 1)
r += 1
vg.cell(r, 1, 'Sachkonten intern (Vergabequote)').font = f_fett
r += 1; i0 = r
for k in intn:
    zelle(vg, r, 1, k, '@', f_blau); r += 1
N['int'] = "Vorgaben!$A$%d:$A$%d" % (i0, r - 1)
r += 1
vg.cell(r, 1, 'Monat (JJJJMM)').font = f_fett
for j, t in enumerate(('Arbeitstage', 'Soll-Aufträge QLA', 'Soll-Aufträge QLG', 'Soll-Aufträge QLM'), 2):
    vg.cell(r, j, t).font = f_fett
vg.column_dimensions['E'].width = 16
r += 1; m0 = r
for m in MONATE:
    zelle(vg, r, 1, m, '0', f_blau)
    zelle(vg, r, 2, int(tage[f'{m // 100}-{m % 100:02d}']), '0', f_blau)
    row = apb[apb['m'] == m].iloc[0]
    for j, lab in enumerate(('QLA', 'QLG', 'QLM'), 3):
        zelle(vg, r, j, int(row[lab]), '0', f_blau)
    r += 1
N['mon'] = "Vorgaben!$A$%d:$A$%d" % (m0, r - 1)
N['tage'] = "Vorgaben!$B$%d:$B$%d" % (m0, r - 1)
N['soll_qla'] = "Vorgaben!$C$%d:$C$%d" % (m0, r - 1)
N['soll_qlg'] = "Vorgaben!$D$%d:$D$%d" % (m0, r - 1)
N['soll_qlm'] = "Vorgaben!$E$%d:$E$%d" % (m0, r - 1)

# ---------------------------------------------------------------------------------------- D_Pruefgruppen
pg = pd.read_excel(EXP + 'LMS_Prüfgruppe.xlsx')
pg = pg[(pg['Status'] == '8 - Prüfung abgeschlossen') & pg['Techn_ Abschluss'].notna() & pg['Babtech_Auftragsnummer'].notna()]
pg = pg[(pg['Techn_ Abschluss'] >= VON) & (pg['Techn_ Abschluss'] < BIS + pd.Timedelta(days=1))].copy()
tag = pg['Techn_ Abschluss'].dt.normalize()
pg['_sammel'] = ((tag >= pd.Timestamp('2026-04-04')) & (tag <= pd.Timestamp('2026-04-06'))).astype(int)
pg['_kw'] = pg['Techn_ Abschluss'].dt.isocalendar().week.astype(int)
pg['_dauer'] = ((pg['Techn_ Abschluss'] - pg['Erstellt am']).dt.total_seconds() / 3600).round(2)
pg = pg.sort_values(['_sammel', '_kw', 'Babtech_Auftragsnummer', '_dauer']).reset_index(drop=True)
ws = wb.create_sheet('D_Pruefgruppen')
kopf(ws, [
    ('Babtec-Auftragsnummer', 'roh', 18, 'LMS_Prüfgruppe: Babtech_Auftragsnummer'),
    ('Prüfungsart', 'roh', 20, 'LMS_Prüfgruppe: Babtec_Prüfungsart'),
    ('Erstellt am', 'roh', 17, 'LMS_Prüfgruppe: Erstellt am'),
    ('Techn. Abschluss', 'roh', 17, 'LMS_Prüfgruppe: Techn_ Abschluss'),
    ('Dauer in Stunden', 'formel', 11, '(Abschluss − Anlage) × 24, auf 2 Stellen gerundet'),
    ('Im Zeitraum (1/0)', 'formel', 10, 'Abschlusstag zwischen Zeitraum von und bis'),
    ('Sammelabschluss (1/0)', 'formel', 12, 'Abschlusstag im Sammelabschluss: wird nicht gewertet'),
    ('Kalenderwoche (ISO)', 'formel', 11, 'WEEKNUM(...;21) = ISO-Kalenderwoche'),
    ('Schlüssel KW|Auftrag', 'formel', 22, 'Gezählt wird je Kalenderwoche und Auftrag'),
    ('Gewertet (1/0)', 'formel', 10, '1 = erste Zeile eines Schlüssels unter den gewerteten Prüfgruppen. Die Zeilen sind nach Sammelabschluss, Kalenderwoche, Auftrag und Dauer sortiert: Bitte die Sortierung nicht ändern.'),
    ('≤ Frist (1/0)', 'formel', 10, '1 = mindestens eine Prüfgruppe dieses Schlüssels wurde innerhalb der Frist S abgeschlossen'),
])
n0 = 2
for i, x in enumerate(pg.to_dict('records')):
    r = n0 + i
    zelle(ws, r, 1, x['Babtech_Auftragsnummer'])
    zelle(ws, r, 2, x['Babtec_Prüfungsart'])
    zelle(ws, r, 3, x['Erstellt am'].to_pydatetime(), DT)
    zelle(ws, r, 4, x['Techn_ Abschluss'].to_pydatetime(), DT)
    zelle(ws, r, 5, f'=ROUND((D{r}-C{r})*24,2)', NUM2)
    zelle(ws, r, 6, f'=IF(AND(INT(D{r})>={N["von"]},INT(D{r})<={N["bis"]}),1,0)', '0')
    zelle(ws, r, 7, f'=IF(AND(INT(D{r})>={N["sammel_von"]},INT(D{r})<={N["sammel_bis"]}),1,0)', '0')
    zelle(ws, r, 8, f'=WEEKNUM(D{r},21)', '0')
    zelle(ws, r, 9, f'=H{r}&"|"&A{r}')
    prev = f'I{r-1}' if r > n0 else '""'
    prevg = f'G{r-1}' if r > n0 else '1'
    zelle(ws, r, 10, f'=IF(AND(F{r}=1,G{r}=0,OR(I{r}<>{prev},{prevg}=1)),1,0)', '0')
    zelle(ws, r, 11, f'=IF(J{r}=1,IF(E{r}<={N["frist_s"]},1,0),0)', '0')
pg_n = n0 + len(pg) - 1
ws.auto_filter.ref = f'A1:K{pg_n}'
PG = lambda c: f"D_Pruefgruppen!${c}$2:${c}${pg_n}"

# ---------------------------------------------------------------------------------------- D_Auftraege
a = pd.read_excel(EXP + 'LMS_Auftrag.xlsx').drop_duplicates()
k = 'Auftragsnummer formatiert'
labs = a.dropna(subset=['Abkürzung']).groupby(k)['Abkürzung'].apply(lambda s: ';'.join(sorted(set(s))))
o = a.drop(columns=['Abkürzung']).drop_duplicates(k).set_index(k)
o['labore'] = labs
o = o[(o['Erstellt am'] >= '2024-01-01') & (o['Techn_ Abschluss'] >= VON) & (o['Techn_ Abschluss'] < BIS + pd.Timedelta(days=1))].reset_index()
o = o.sort_values(['Art', k]).reset_index(drop=True)
ws = wb.create_sheet('D_Auftraege')

# Buchungen der Aufträge (alle Zeitpunkte), für die IST-Stunden der Plankostenerfüllung
h = pd.read_excel(EXP + 'LMS_gebuchte_Stunden.xlsx')
txt = h['Sonstiges/Arbeitspaket/Auftrag'].astype(str).str.strip()
nr = txt.str.split(' ').str[0].str.split('+').str[0]
ist_auftrag = nr.str.upper().str.contains('TM-') & nr.str.upper().str.contains('OR')
hb = h[ist_auftrag & nr.isin(set(o[k]))].copy().sort_values(['Datum']).reset_index(drop=True)
hb_n = 1 + len(hb)
HB = lambda c: f"D_Buchungen_Auftraege!${c}$2:${c}${hb_n}"

kopf(ws, [
    ('Auftrag', 'roh', 20, 'LMS_Auftrag: Auftragsnummer formatiert (eine Zeile je Auftrag, Dubletten entfernt)'),
    ('Art (Priorität)', 'roh', 18, 'LMS_Auftrag: Art'),
    ('Labore', 'roh', 14, 'LMS_Auftrag: Abkürzung, alle Labore eines Auftrags zusammengefasst'),
    ('Bearbeitungsbeginn', 'roh', 17, 'LMS_Auftrag: Bearbeitungsbeginn'),
    ('Techn. Abschluss', 'roh', 17, 'LMS_Auftrag: Techn_ Abschluss'),
    ('Zugesagter Termin', 'roh', 13, 'LMS_Auftrag: Zugesagter Termin'),
    ('Auftragswert (PLAN)', 'roh', 13, 'LMS_Auftrag: Auftragswert berechnet'),
    ('Prio', 'formel', 7, 'Kurzform der Art: S, M, L oder 0'),
    ('Im Zeitraum (1/0)', 'formel', 10, 'Abschlusstag zwischen Zeitraum von und bis'),
    ('Tage ab Beginn', 'formel', 10, 'Techn. Abschluss − Bearbeitungsbeginn in Tagen, auf 2 Stellen gerundet; negativ = vor dem Beginn abgeschlossen'),
    ('In Frist (1/0)', 'formel', 9, 'M: höchstens Frist M, L: höchstens Frist L; ohne Bearbeitungsbeginn = 0'),
    ('Mit Termin (1/0)', 'formel', 9, 'zugesagter Termin vorhanden'),
    ('Pünktlich (1/0)', 'formel', 9, 'Abschlusstag am oder vor dem zugesagten Termin'),
    ('Buchungen', 'formel', 9, 'Anzahl der Buchungen auf diesen Auftrag (Blatt D_Buchungen_Auftraege)'),
    ('Gebuchte Stunden', 'formel', 10, 'Summe aller auf den Auftrag gebuchten Stunden, unabhängig von Datum und Labor'),
    ('IST-Kosten', 'formel', 12, 'Gebuchte Stunden × Stundensatz'),
    ('Plankosten gewertet (1/0)', 'formel', 11, 'M oder L, im Zeitraum abgeschlossen, Auftragswert > 0 und mindestens eine Buchung'),
])
P = {'S (48 h)': 'S', 'M (14 d)': 'M', 'L (70 d)': 'L', '0 (ohne Reaktionszeit)': '0'}
for i, x in enumerate(o.to_dict('records')):
    r = 2 + i
    zelle(ws, r, 1, x[k]); zelle(ws, r, 2, x['Art']); zelle(ws, r, 3, x['labore'] if isinstance(x['labore'], str) else '')
    if pd.notna(x['Bearbeitungsbeginn']): zelle(ws, r, 4, x['Bearbeitungsbeginn'].to_pydatetime(), DT)
    zelle(ws, r, 5, x['Techn_ Abschluss'].to_pydatetime(), DT)
    if pd.notna(x['Zugesagter Termin']): zelle(ws, r, 6, x['Zugesagter Termin'].to_pydatetime(), D)
    if pd.notna(x['Auftragswert berechnet']): zelle(ws, r, 7, round(float(x['Auftragswert berechnet']), 2), NUM2)
    zelle(ws, r, 8, f'=IF(LEFT(B{r},1)="S","S",IF(LEFT(B{r},1)="M","M",IF(LEFT(B{r},1)="L","L",IF(LEFT(B{r},1)="0","0","ohne"))))')
    zelle(ws, r, 9, f'=IF(AND(INT(E{r})>={N["von"]},INT(E{r})<={N["bis"]}),1,0)', '0')
    zelle(ws, r, 10, f'=IF(D{r}="","",ROUND(E{r}-D{r},2))', NUM2)
    zelle(ws, r, 11, f'=IF(J{r}="",0,IF(AND(H{r}="M",J{r}<={N["frist_m"]}),1,IF(AND(H{r}="L",J{r}<={N["frist_l"]}),1,0)))', '0')
    zelle(ws, r, 12, f'=IF(F{r}="",0,1)', '0')
    zelle(ws, r, 13, f'=IF(L{r}=1,IF(INT(E{r})<=INT(F{r}),1,0),0)', '0')
    zelle(ws, r, 14, f'=COUNTIF({HB("E")},A{r})', '0')
    zelle(ws, r, 15, f'=SUMIF({HB("E")},A{r},{HB("B")})', NUM2)
    zelle(ws, r, 16, f'=O{r}*{N["satz"]}', EUR)
    zelle(ws, r, 17, f'=IF(AND(OR(H{r}="M",H{r}="L"),I{r}=1,N(G{r})>0,N{r}>0),1,0)', '0')
au_n = 1 + len(o)
ws.auto_filter.ref = f'A1:Q{au_n}'
AU = lambda c: f"D_Auftraege!${c}$2:${c}${au_n}"

# ---------------------------------------------------------------------------------------- D_Buchungen_Auftraege
ws = wb.create_sheet('D_Buchungen_Auftraege')
kopf(ws, [
    ('Kontierung', 'roh', 46, 'LMS_gebuchte_Stunden: Sonstiges/Arbeitspaket/Auftrag'),
    ('Stunden', 'roh', 9, 'LMS_gebuchte_Stunden: Anzahl'),
    ('Laborbereich', 'roh', 11, 'LMS_gebuchte_Stunden: Laborbereich'),
    ('Datum', 'roh', 12, 'LMS_gebuchte_Stunden: Datum'),
    ('Auftragsnummer', 'formel', 20, 'Erstes Wort der Kontierung, ohne Teilauftrag hinter dem „+“'),
])
for i, x in enumerate(hb.to_dict('records')):
    r = 2 + i
    zelle(ws, r, 1, str(x['Sonstiges/Arbeitspaket/Auftrag']).strip()); zelle(ws, r, 2, float(x['Anzahl']), NUM2)
    zelle(ws, r, 3, x['Laborbereich'] if isinstance(x['Laborbereich'], str) else ''); zelle(ws, r, 4, x['Datum'].to_pydatetime(), D)
    zelle(ws, r, 5, f'=LEFT(TRIM(A{r}),MIN(FIND(" ",TRIM(A{r})&" "),FIND("+",TRIM(A{r})&"+"))-1)')
ws.auto_filter.ref = f'A1:E{hb_n}'

# ---------------------------------------------------------------------------------------- D_Buchungen_Zeitraum
hq = h[(h['Datum'] >= VON) & (h['Datum'] < BIS + pd.Timedelta(days=1)) & h['Laborbereich'].isin(['QLA', 'QLG', 'QLM'])].copy()
hq = hq.sort_values(['Laborbereich', 'Datum']).reset_index(drop=True)
ws = wb.create_sheet('D_Buchungen_Zeitraum')
kopf(ws, [
    ('Kontierung', 'roh', 46, 'LMS_gebuchte_Stunden: Sonstiges/Arbeitspaket/Auftrag'),
    ('Stunden', 'roh', 9, 'LMS_gebuchte_Stunden: Anzahl'),
    ('Laborbereich', 'roh', 11, 'LMS_gebuchte_Stunden: Laborbereich (nur QLA, QLG, QLM)'),
    ('Datum', 'roh', 12, 'LMS_gebuchte_Stunden: Datum'),
    ('Monat (JJJJMM)', 'formel', 10, 'JAHR × 100 + MONAT'),
    ('Erstes Wort', 'formel', 20, 'Erstes Wort der Kontierung in Großbuchstaben, ohne Teilauftrag hinter dem „+“'),
    ('Kontierungstyp', 'formel', 14, 'Urlaub (auch „Urlaub_…“, „Uralaub…“), Krankheit, Kalibrierung (Kalibriertätigkeiten, Calibration), Wartung (Wartungstätigkeiten), WE+FP, Laborauftrag (erstes Wort enthält „TM-“ und „OR“), sonst Sonstiges'),
    ('Arbeitszeit (1/0)', 'formel', 10, '1 = zählt zur Buchungsquote (alles außer Urlaub und Krankheit)'),
    ('Bezahlte Leistung (1/0)', 'formel', 11, '1 = zählt zur Instandhaltungsquote (Laborauftrag oder WE+FP)'),
])
for i, x in enumerate(hq.to_dict('records')):
    r = 2 + i
    zelle(ws, r, 1, str(x['Sonstiges/Arbeitspaket/Auftrag']).strip()); zelle(ws, r, 2, float(x['Anzahl']), NUM2)
    zelle(ws, r, 3, x['Laborbereich']); zelle(ws, r, 4, x['Datum'].to_pydatetime(), D)
    zelle(ws, r, 5, f'=YEAR(D{r})*100+MONTH(D{r})', '0')
    zelle(ws, r, 6, f'=UPPER(LEFT(TRIM(A{r}),MIN(FIND(" ",TRIM(A{r})&" "),FIND("+",TRIM(A{r})&"+"))-1))')
    u = f'UPPER(TRIM(A{r}))'
    zelle(ws, r, 7, f'=IF(OR(LEFT({u},6)="URLAUB",LEFT({u},7)="URALAUB"),"Urlaub",IF({u}="KRANKHEIT","Krankheit",'
                    f'IF(OR({u}="KALIBRIERTÄTIGKEITEN",{u}="CALIBRATION"),"Kalibrierung",IF({u}="WARTUNGSTÄTIGKEITEN","Wartung",'
                    f'IF({u}="WE+FP","WE+FP",IF(AND(ISNUMBER(SEARCH("TM-",F{r})),ISNUMBER(SEARCH("OR",F{r}))),"Laborauftrag","Sonstiges"))))))')
    zelle(ws, r, 8, f'=IF(OR(G{r}="Urlaub",G{r}="Krankheit"),0,1)', '0')
    zelle(ws, r, 9, f'=IF(OR(G{r}="Laborauftrag",G{r}="WE+FP"),1,0)', '0')
hq_n = 1 + len(hq)
ws.auto_filter.ref = f'A1:I{hq_n}'
HQ = lambda c: f"D_Buchungen_Zeitraum!${c}$2:${c}${hq_n}"

# ---------------------------------------------------------------------------------------- D_Soll_Stunden
ab = pd.read_excel(md, sheet_name='Abwesenheit_SF'); ab.columns = [str(c) for c in ab.columns]
fm = pd.read_excel(md, sheet_name='FTE_Monat'); fm.columns = [str(c) for c in fm.columns]
fmi = fm.drop_duplicates(['Area', 'Name']).set_index(['Area', 'Name'])
ws = wb.create_sheet('D_Soll_Stunden')
kopf(ws, [
    ('Zeile in Abwesenheit_SF', 'roh', 11, 'Zeilennummer der Person im Blatt Abwesenheit_SF der manuellen Daten (statt des Namens)'),
    ('Area', 'roh', 7, 'Abwesenheit_SF: Area'),
    ('Monat (JJJJMM)', 'roh', 10, ''),
    ('FTE fest', 'roh', 8, 'Abwesenheit_SF: FTE'),
    ('FTE des Monats', 'roh', 9, 'FTE_Monat: Wert des Monats (leer = es gilt die feste FTE)'),
    ('Abwesenheits-tage', 'roh', 11, 'Abwesenheit_SF: Wert des Monats (leer = noch nicht erfasst)'),
    ('FTE gilt', 'formel', 8, 'FTE des Monats, sonst FTE fest'),
    ('Im Labor (1/0)', 'formel', 9, '1 = FTE > 0'),
    ('Erfasst (1/0)', 'formel', 9, '1 = Abwesenheit für den Monat eingetragen (auch 0)'),
    ('Arbeitstage', 'formel', 9, 'aus den Vorgaben'),
    ('Abwesenheit begrenzt', 'formel', 10, 'höchstens so viele Tage wie Arbeitstage'),
    ('Soll-Stunden', 'formel', 10, '(Arbeitstage − Abwesenheit) × FTE × Stunden je Arbeitstag'),
    ('Brutto-Stunden', 'formel', 10, 'Arbeitstage × FTE × Stunden je Arbeitstag'),
])
r = 2
for m in MONATE:
    col = f'{m // 100}-{m % 100:02d}'
    for idx, x in ab.iterrows():
        if x['Area'] not in ('QLA', 'QLG', 'QLM'): continue
        zelle(ws, r, 1, idx + 2, '0'); zelle(ws, r, 2, x['Area']); zelle(ws, r, 3, m, '0')
        zelle(ws, r, 4, float(x['FTE']) if pd.notna(pd.to_numeric(x['FTE'], errors='coerce')) else 0, '0.000')
        v = fmi[col].get((x['Area'], x['Name'])) if col in fmi.columns else None
        if v is not None and pd.notna(pd.to_numeric(v, errors='coerce')): zelle(ws, r, 5, float(v), '0.000')
        w = pd.to_numeric(x.get(col), errors='coerce')
        if pd.notna(w): zelle(ws, r, 6, float(w), '0.0')
        zelle(ws, r, 7, f'=IF(E{r}="",D{r},E{r})', '0.000')
        zelle(ws, r, 8, f'=IF(G{r}>0,1,0)', '0')
        zelle(ws, r, 9, f'=IF(F{r}="",0,1)', '0')
        zelle(ws, r, 10, f'=INDEX({N["tage"]},MATCH(C{r},{N["mon"]},0))', '0')
        zelle(ws, r, 11, f'=MIN(N(F{r}),J{r})', '0.0')
        zelle(ws, r, 12, f'=IF(H{r}=1,(J{r}-K{r})*G{r}*{N["h_tag"]},0)', NUM2)
        zelle(ws, r, 13, f'=IF(H{r}=1,J{r}*G{r}*{N["h_tag"]},0)', NUM2)
        r += 1
ss_n = r - 1
ws.auto_filter.ref = f'A1:M{ss_n}'
SS = lambda c: f"D_Soll_Stunden!${c}$2:${c}${ss_n}"

# ---------------------------------------------------------------------------------------- Monat_Labor
ws = wb.create_sheet('Monat_Labor')
ws['A1'] = 'Soll- und Ist-Stunden je Monat und Labor'; ws['A1'].font = f_titel
ws['A2'] = 'Ein Monat zählt nur, wenn die Abwesenheiten aller Personen des Labors erfasst sind (Spalte „Vollständig“).'; ws['A2'].font = f_klein
hdr = ['Monat', 'Labor', 'Personen im Labor', 'Abwesenheit erfasst', 'Vollständig (1/0)', 'Soll-Stunden', 'Brutto-Stunden',
       'Gebucht: Arbeitszeit', 'Gebucht: bezahlte Leistung', 'Gebucht: Urlaub und Krankheit']
for j, t in enumerate(hdr, 1):
    c = ws.cell(4, j, t); c.font = f_kopf; c.fill = fill_form; c.alignment = Alignment(wrap_text=True, vertical='center')
    ws.column_dimensions[L(j)].width = 14
ws.row_dimensions[4].height = 32
r = 5
for m in MONATE:
    for lab in ('QLA', 'QLG', 'QLM'):
        zelle(ws, r, 1, m, '0'); zelle(ws, r, 2, lab)
        zelle(ws, r, 3, f'=COUNTIFS({SS("B")},B{r},{SS("C")},A{r},{SS("H")},1)', '0', f_gruen)
        zelle(ws, r, 4, f'=COUNTIFS({SS("B")},B{r},{SS("C")},A{r},{SS("H")},1,{SS("I")},1)', '0', f_gruen)
        zelle(ws, r, 5, f'=IF(D{r}>=C{r},1,0)', '0')
        zelle(ws, r, 6, f'=SUMIFS({SS("L")},{SS("B")},B{r},{SS("C")},A{r})', NUM2, f_gruen)
        zelle(ws, r, 7, f'=SUMIFS({SS("M")},{SS("B")},B{r},{SS("C")},A{r})', NUM2, f_gruen)
        zelle(ws, r, 8, f'=SUMIFS({HQ("B")},{HQ("C")},B{r},{HQ("E")},A{r},{HQ("H")},1)', NUM2, f_gruen)
        zelle(ws, r, 9, f'=SUMIFS({HQ("B")},{HQ("C")},B{r},{HQ("E")},A{r},{HQ("I")},1)', NUM2, f_gruen)
        zelle(ws, r, 10, f'=SUMIFS({HQ("B")},{HQ("C")},B{r},{HQ("E")},A{r},{HQ("H")},0)', NUM2, f_gruen)
        r += 1
ml_n = r - 1
ML = lambda c: f"Monat_Labor!${c}$5:${c}${ml_n}"

# ---------------------------------------------------------------------------------------- D_SAP
s = pd.read_excel(EXP + 'SAP_Instandhaltungskosten.xlsx')
s['_m'] = s['Geschäftsjahr'] * 100 + s['Buchungsmonat']
s = s[s['_m'].isin(MONATE)].copy().sort_values(['_m', 'Sachkonto']).reset_index(drop=True)
ws = wb.create_sheet('D_SAP')
kopf(ws, [
    ('Geschäftsjahr', 'roh', 10, 'SAP: Geschäftsjahr'),
    ('Buchungsmonat', 'roh', 10, 'SAP: Buchungsmonat'),
    ('Auftragsart', 'roh', 34, 'SAP: Instandhaltungsauftragsart'),
    ('Instandhaltungsauftrag', 'roh', 14, 'SAP: Instandhaltungsauftrag'),
    ('Sachkonto', 'roh', 30, 'SAP: Sachkonto'),
    ('Istkosten', 'roh', 12, 'SAP: Istkosten (übergreifende Währung)'),
    ('Monat (JJJJMM)', 'formel', 10, 'Geschäftsjahr × 100 + Buchungsmonat'),
    ('Zuordnung', 'formel', 14, 'extern / intern, wenn eines der Sachkonten aus den Vorgaben im Text vorkommt; sonst nicht gewertet'),
])
for i, x in enumerate(s.to_dict('records')):
    r = 2 + i
    zelle(ws, r, 1, int(x['Geschäftsjahr']), '0'); zelle(ws, r, 2, int(x['Buchungsmonat']), '0')
    zelle(ws, r, 3, x['Instandhaltungsauftragsart']); zelle(ws, r, 4, x['Instandhaltungsauftrag'] if pd.notna(x['Instandhaltungsauftrag']) else '')
    zelle(ws, r, 5, x['Sachkonto']); zelle(ws, r, 6, float(x['Istkosten (übergreifende Währung)']), NUM2)
    zelle(ws, r, 7, f'=A{r}*100+B{r}', '0')
    zelle(ws, r, 8, f'=IF(SUMPRODUCT(--ISNUMBER(SEARCH({N["ext"]},E{r})))>0,"extern",IF(SUMPRODUCT(--ISNUMBER(SEARCH({N["int"]},E{r})))>0,"intern","nicht gewertet"))')
sap_n = 1 + len(s)
ws.auto_filter.ref = f'A1:H{sap_n}'
SA = lambda c: f"D_SAP!${c}$2:${c}${sap_n}"

# ---------------------------------------------------------------------------------------- D_Qualitaet
bq = pd.read_excel(md, sheet_name='BSC_Quartal')
qz = bq[bq['Quartal'].astype(str).str.strip() == QUARTAL].iloc[0]
ws = wb.create_sheet('D_Qualitaet')
kopf(ws, [('Quartal', 'roh', 12, 'BSC_Quartal'), ('Dienstleistungsquote', 'roh', 16, 'BSC_Quartal'), ('Methodeneinsatz', 'roh', 16, 'BSC_Quartal'), ('Rückweisung', 'roh', 14, 'BSC_Quartal')])
zelle(ws, 2, 1, QUARTAL)
for j, c in enumerate(('Dienstleistungsquote', 'Methodeneinsatz', 'Rückweisung'), 2):
    zelle(ws, 2, j, float(qz[c]), PCT, f_blau)

# ---------------------------------------------------------------------------------------- Ergebnis
er = wb.create_sheet('Ergebnis', 0)
er['A1'] = f'Prüfrechnung der BSC-Kennzahlen für {QUARTAL} (01.04.–30.06.2026)'; er['A1'].font = f_titel
er['A2'] = ('Jede Kennzahl wird mit Formeln aus den Datenblättern hergeleitet. Spalte F enthält den Wert, den das Labor-KPI-Dashboard für '
            'dasselbe Quartal zeigt (Stand 20.11.2026, Daten bis 04.11.2026). Wie im Dashboard wird jede Einzelkennzahl auf eine Nachkommastelle '
            '(in Prozent) gerundet, bevor sie weiterverrechnet wird.')
er['A2'].font = f_klein; er['A2'].alignment = wrap; er.merge_cells('A2:H2'); er.row_dimensions[2].height = 42
for col, w in zip('ABCDEFGH', (34, 70, 13, 13, 12, 12, 11, 14)):
    er.column_dimensions[col].width = w
hdr = ['Kennzahl', 'Rechenweg', 'Zähler', 'Nenner', 'Prüfwert', 'Dashboard', 'Differenz', 'Ergebnis']
for j, t in enumerate(hdr, 1):
    c = er.cell(4, j, t); c.font = f_kopf; c.fill = fill_form; c.alignment = Alignment(wrap_text=True, vertical='center')
DB = {'s': .878, 'm': .637, 'l': .538, 'pm': .869, 'pl': .731, 'pu': .800, 'tt': .742,
      'pk': 1.045, 'pke': .955, 'vq': .061, 'eig': .939, 'aq': 1.140, 'aqe': 1.140, 'iq': .607, 'iqe': .934, 'be': .992,
      'dl': 1.0, 'me': 0.0, 'rw': 0.0, 'ql': .908}
R = {}
zeilen = []
def gruppe(t):
    zeilen.append(('G', t))
def kz(key, name, weg, zaehler, nenner, wert):
    zeilen.append(('K', key, name, weg, zaehler, nenner, wert))

gruppe('Termintreue (HoQ 1)')
kz('s', 'Reaktionszeit S (S_Babtec)', 'Gewertete Schlüssel KW|Auftrag mit Abschluss ≤ 48 h / alle gewerteten Schlüssel (Blatt D_Pruefgruppen, Sammelabschluss ausgenommen)',
   f'=SUM({PG("K")})', f'=SUM({PG("J")})', '=ROUND(C{r}/D{r},3)')
kz('m', 'Reaktionszeit M', 'M-Aufträge im Zeitraum mit Abschluss ≤ 14 Tage nach Bearbeitungsbeginn / alle M-Aufträge im Zeitraum',
   f'=COUNTIFS({AU("H")},"M",{AU("I")},1,{AU("K")},1)', f'=COUNTIFS({AU("H")},"M",{AU("I")},1)', '=ROUND(C{r}/D{r},3)')
kz('l', 'Reaktionszeit L', 'L-Aufträge im Zeitraum mit Abschluss ≤ 70 Tage nach Bearbeitungsbeginn / alle L-Aufträge im Zeitraum',
   f'=COUNTIFS({AU("H")},"L",{AU("I")},1,{AU("K")},1)', f'=COUNTIFS({AU("H")},"L",{AU("I")},1)', '=ROUND(C{r}/D{r},3)')
kz('pm', 'Pünktlichkeit M', 'M-Aufträge im Zeitraum mit Abschluss am oder vor dem zugesagten Termin / M-Aufträge mit Termin',
   f'=COUNTIFS({AU("H")},"M",{AU("I")},1,{AU("M")},1)', f'=COUNTIFS({AU("H")},"M",{AU("I")},1,{AU("L")},1)', '=ROUND(C{r}/D{r},3)')
kz('pl', 'Pünktlichkeit L', 'L-Aufträge im Zeitraum mit Abschluss am oder vor dem zugesagten Termin / L-Aufträge mit Termin',
   f'=COUNTIFS({AU("H")},"L",{AU("I")},1,{AU("M")},1)', f'=COUNTIFS({AU("H")},"L",{AU("I")},1,{AU("L")},1)', '=ROUND(C{r}/D{r},3)')
kz('pu', 'Pünktlichkeit', 'Mittelwert aus Pünktlichkeit M und Pünktlichkeit L', None, None, '=ROUND(AVERAGE({pm},{pl}),3)')
kz('tt', 'Termintreue', '(S + M + L) / 3 × Gewichtung Reaktionszeit + Pünktlichkeit × Gewichtung Pünktlichkeit', None, None,
   f'=ROUND(AVERAGE({{s}},{{m}},{{l}})*{N["g_rz"]}+{{pu}}*{N["g_pu"]},3)')
gruppe('Budgeteinhaltung (HoQ 1)')
kz('pk', 'Plankostenerfüllung (M und L)', 'Summe IST-Kosten / Summe PLAN-Kosten der gewerteten M- und L-Aufträge (Blatt D_Auftraege, Spalte Q = 1)',
   f'=SUMIFS({AU("P")},{AU("Q")},1)', f'=SUMIFS({AU("G")},{AU("Q")},1)', '=ROUND(C{r}/D{r},3)')
kz('pke', 'Erfüllungsgrad Plankosten', '100 % − |Plankostenerfüllung − Zielwert|, mindestens 0', None, None, f'=ROUND(MAX(0,1-ABS({{pk}}-{N["ziel_pk"]})),3)')
kz('vq', 'Vergabequote', 'Externe Leistung / (interne + externe Leistung), SAP nach Buchungsmonat (Blatt D_SAP)',
   f'=SUMIFS({SA("F")},{SA("H")},"extern")', f'=SUMIFS({SA("F")},{SA("H")},"extern")+SUMIFS({SA("F")},{SA("H")},"intern")', '=ROUND(C{r}/D{r},3)')
kz('eig', 'Eigenleistungsquote', '100 % − Vergabequote', None, None, '=ROUND(1-{vq},3)')
kz('aq', 'Auftragsquote', 'Abgeschlossene Aufträge im Zeitraum je Labor QLA, QLG, QLM (mehrere Labore zählen je Labor) / Soll-Aufträge der drei Monate',
   f'=COUNTIFS({AU("C")},"*QLA*",{AU("I")},1)+COUNTIFS({AU("C")},"*QLG*",{AU("I")},1)+COUNTIFS({AU("C")},"*QLM*",{AU("I")},1)',
   f'=SUM({N["soll_qla"]})+SUM({N["soll_qlg"]})+SUM({N["soll_qlm"]})', '=ROUND(C{r}/D{r},3)')
kz('aqe', 'Erfüllungsgrad Auftragsquote', 'Auftragsquote / Zielwert, ohne Obergrenze', None, None, f'=ROUND({{aq}}/{N["ziel_aq"]},3)')
kz('iq', 'Instandhaltungsquote', 'Gebuchte Stunden auf Laboraufträge und WE+FP / Soll-Stunden, nur vollständig erfasste Monate (Blatt Monat_Labor)',
   f'=SUMIFS({ML("I")},{ML("E")},1)', f'=SUMIFS({ML("F")},{ML("E")},1)', '=ROUND(C{r}/D{r},3)')
kz('iqe', 'Erfüllungsgrad Instandhaltungsquote', 'Instandhaltungsquote / Zielwert, ohne Obergrenze', None, None, f'=ROUND({{iq}}/{N["ziel_iq"]},3)')
kz('be', 'Budgeteinhaltung', 'Erfüllungsgrad Plankosten × G + Eigenleistungsquote × G + Erfüllungsgrad Auftragsquote × G + Erfüllungsgrad Instandhaltungsquote × G', None, None,
   f'=ROUND({{pke}}*{N["g_pk"]}+{{eig}}*{N["g_vq"]}+{{aqe}}*{N["g_aq"]}+{{iqe}}*{N["g_iq"]},3)')
gruppe('Qualitätslevel (HoQ 1)')
kz('dl', 'Dienstleistungsquote', 'von Hand erfasst (Blatt D_Qualitaet)', None, None, '=D_Qualitaet!$B$2')
kz('me', 'Methodeneinsatz', 'von Hand erfasst (Blatt D_Qualitaet)', None, None, '=D_Qualitaet!$C$2')
kz('rw', 'Rückweisung', 'von Hand erfasst (Blatt D_Qualitaet)', None, None, '=D_Qualitaet!$D$2')
kz('ql', 'Qualitätslevel', 'Dienstleistungsquote × G + (100 % − |Methodeneinsatz − Zielwert|) × G + (100 % − Rückweisung) × G', None, None,
   f'=ROUND({{dl}}*{N["g_dl"]}+(1-ABS(ABS({{me}})-{N["ziel_me"]}))*{N["g_me"]}+{N["g_rw"]}*(1-ABS({{rw}})),3)')
gruppe('Zusätzlich zur Kontrolle (nicht in der BSC)')
kz('bq', 'Buchungsquote', 'Gebuchte Arbeitszeit (ohne Urlaub und Krankheit) / Soll-Stunden, nur vollständig erfasste Monate',
   f'=SUMIFS({ML("H")},{ML("E")},1)', f'=SUMIFS({ML("F")},{ML("E")},1)', '=ROUND(C{r}/D{r},3)')

r = 5
for z in zeilen:
    if z[0] == 'G':
        c = er.cell(r, 1, z[1]); c.font = f_fett
        for j in range(1, 9): er.cell(r, j).fill = fill_hell
        r += 1; continue
    R[z[1]] = r; r += 1
r = 5
for z in zeilen:
    if z[0] == 'G':
        r += 1; continue
    _, key, name, weg, zaehler, nenner, wert = z
    zelle(er, r, 1, name, font=f_fett if key in ('tt', 'be', 'ql') else None)
    zelle(er, r, 2, weg).alignment = wrap
    if zaehler: zelle(er, r, 3, zaehler, NUM2 if key in ('pk', 'vq', 'iq', 'bq') else '#,##0', f_gruen)
    if nenner: zelle(er, r, 4, nenner, NUM2 if key in ('pk', 'vq', 'iq', 'bq') else '#,##0', f_gruen)
    form = wert.replace('{r}', str(r))
    for kk, rr in R.items():
        form = form.replace('{' + kk + '}', f'$E${rr}')
    zelle(er, r, 5, form, PCT, f_fett if key in ('tt', 'be', 'ql') else None)
    if key in DB:
        zelle(er, r, 6, DB[key], PCT, f_blau)
        zelle(er, r, 7, f'=E{r}-F{r}', '+0.0%;-0.0%;0.0%')
        zelle(er, r, 8, f'=IF(ABS(G{r})<0.00049,"stimmt","abweichend")')
    for j in range(1, 9):
        er.cell(r, j).border = rahmen; er.cell(r, j).alignment = Alignment(vertical='center', wrap_text=(j == 2))
    er.row_dimensions[r].height = 30
    r += 1
r += 1
er.cell(r, 1, 'Einschränkungen dieser Prüfung').font = f_fett; r += 1
for t in [
    'Die Datenblätter enthalten nur die Zeilen, die für das Quartal gebraucht werden. Diese Auswahl und das Zusammenfassen der Labore eines Auftrags (LMS_Auftrag hat eine Zeile je Auftrag und Labor) sind vorab geschehen und hier nicht als Formel nachvollziehbar.',
    'D_Pruefgruppen enthält nur Prüfgruppen mit Status „8 - Prüfung abgeschlossen“, mit Babtec-Auftragsnummer und Abschluss im Quartal. Die Zeilen sind sortiert; die Spalte „Gewertet“ setzt diese Sortierung voraus.',
    'D_Auftraege enthält nur Aufträge, die ab 2024 angelegt und im Quartal technisch abgeschlossen wurden.',
    'D_Soll_Stunden nennt statt der Namen die Zeilennummer im Blatt Abwesenheit_SF der manuellen Daten.',
    'Die Werte in Spalte F sind abgeschrieben, nicht verknüpft. Nach einer Änderung im Dashboard oder in den Daten müssen sie neu übertragen werden.',
]:
    c = er.cell(r, 1, '• ' + t); c.font = f_norm; c.alignment = wrap; er.merge_cells(start_row=r, start_column=1, end_row=r, end_column=8)
    er.row_dimensions[r].height = 28; r += 1
er.freeze_panes = 'A5'

# ---------------------------------------------------------------------------------------- Anleitung
an = wb.create_sheet('Anleitung', 0)
an.column_dimensions['A'].width = 120
tx = [
    ('Prüf-Excel: BSC-Kennzahlen des Labors für ' + QUARTAL, f_titel),
    ('Zweck: Diese Mappe rechnet die Kennzahlen der Balanced Scorecard für ein Quartal unabhängig vom Dashboard nach. Jeder Schritt steht als Excel-Formel in einer Zelle und lässt sich mit Filtern und der Formelanzeige (Strg + #) nachvollziehen.', f_norm),
    ('', f_norm),
    ('So prüfst du', f_fett),
    ('1. Blatt „Ergebnis“: Prüfwert (Spalte E) und Dashboard-Wert (Spalte F) vergleichen. „stimmt“ heißt: gleiche Zahl auf eine Nachkommastelle.', f_norm),
    ('2. Für jede Kennzahl die Rechenregel in Spalte B lesen und mit deiner Absicht vergleichen.', f_norm),
    ('3. In den Datenblättern Stichproben ziehen: Filter setzen, einzelne Zeilen gegen den Export oder das LIMS prüfen. Die Kommentare in den Spaltenköpfen sagen, woher eine Spalte kommt und was eine Formel tut.', f_norm),
    ('4. Regeln ändern: Werte im Blatt „Vorgaben“ (blau) ändern, die Mappe rechnet neu. So siehst du, was eine andere Frist, Gewichtung oder ein anderer Zielwert bewirkt.', f_norm),
    ('', f_norm),
    ('Farben', f_fett),
    ('Graue Spaltenköpfe: Werte aus dem Export, unverändert. Grüne Spaltenköpfe: Formeln.', f_norm),
    ('Blaue Schrift: Eingaben (Vorgaben, von Hand erfasste Werte, Werte aus dem Dashboard). Schwarze Schrift: Formeln. Grüne Schrift: Formeln, die auf ein anderes Blatt verweisen.', f_norm),
    ('', f_norm),
    ('Blätter', f_fett),
    ('Ergebnis – alle Kennzahlen mit Rechenweg, Prüfwert und Vergleich mit dem Dashboard', f_norm),
    ('Vorgaben – Zeitraum, Fristen, Stundensatz, Sachkonten, Zielwerte, Gewichtungen, SOLL, Arbeitstage und Soll-Aufträge', f_norm),
    ('D_Pruefgruppen – Babtec-Prüfgruppen mit Abschluss im Quartal (Reaktionszeit S)', f_norm),
    ('D_Auftraege – im Quartal abgeschlossene LIMS-Aufträge (Reaktionszeit M und L, Pünktlichkeit, Plankosten, Auftragsquote)', f_norm),
    ('D_Buchungen_Auftraege – alle Stundenbuchungen auf diese Aufträge, auch vor dem Quartal (IST-Kosten)', f_norm),
    ('D_Buchungen_Zeitraum – alle Stundenbuchungen von QLA, QLG und QLM im Quartal mit Kontierungstyp (Instandhaltungs- und Buchungsquote)', f_norm),
    ('D_Soll_Stunden – Soll-Stunden je Person und Monat aus den manuellen Daten, ohne Namen', f_norm),
    ('Monat_Labor – Soll- und Ist-Stunden je Monat und Labor, mit Prüfung, ob die Abwesenheiten vollständig erfasst sind', f_norm),
    ('D_SAP – SAP-Instandhaltungskosten mit Buchungsmonat im Quartal und Zuordnung intern/extern (Vergabequote)', f_norm),
    ('D_Qualitaet – die von Hand erfassten Werte des Qualitätslevels', f_norm),
    ('', f_norm),
    ('Quellen: LMS_Auftrag, LMS_Prüfgruppe, LMS_gebuchte_Stunden (Datenstand 04.11.2026), SAP_Instandhaltungskosten, manuelle_Daten (Stand 19.11.2026).', f_klein),
    ('Vertraulich: Die Mappe enthält Auftragsnummern, Bezeichnungen und Kosten.', f_klein),
]
for i, (t, f) in enumerate(tx, 1):
    c = an.cell(i, 1, t); c.font = f; c.alignment = Alignment(wrap_text=True, vertical='top')

wb.save(OUT)
print('Zeilen: Prüfgruppen', len(pg), 'Aufträge', len(o), 'Buchungen Aufträge', len(hb), 'Buchungen Zeitraum', len(hq), 'Soll', ss_n - 1, 'SAP', len(s))
