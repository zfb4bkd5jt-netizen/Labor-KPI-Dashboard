import json, datetime as dt
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter
A=json.load(open('auftraege.json'))['rows']; W=json.load(open('wk_offen.json'))['rows']
stand=dt.date(2026,11,4)
D=lambda s: dt.date.fromisoformat(s) if s else None
la=[r for r in A if not r['abschluss'] and (stand-D(r['erstellt'])).days>365]
la.sort(key=lambda r:r['erstellt'])
wk=sorted([r for r in W if r['freigegeben']], key=lambda r:-r['tage_ueber'])
print(len(la),len(wk))
wb=Workbook(); f=Font(name='Arial',size=10); fb=Font(name='Arial',size=10,bold=True,color='FFFFFF'); fill=PatternFill('solid',fgColor='1F3864')
def blatt(ws,titel,hinweis,kopf,zeilen,breiten,datumsp,zahlsp):
    ws['A1']=titel; ws['A1'].font=Font(name='Arial',size=12,bold=True)
    ws['A2']=hinweis; ws['A2'].font=Font(name='Arial',size=9,italic=True)
    for i,k in enumerate(kopf,1):
        c=ws.cell(4,i,k); c.font=fb; c.fill=fill; c.alignment=Alignment(vertical='center',wrap_text=True)
    for z in zeilen:
        ws.append(z)
    for row in ws.iter_rows(min_row=5):
        for c in row:
            c.font=f
            if c.column in datumsp: c.number_format='DD.MM.YYYY'
            if c.column in zahlsp: c.number_format='#,##0'
    for i,b in enumerate(breiten,1): ws.column_dimensions[get_column_letter(i)].width=b
    ws.freeze_panes='A5'; ws.auto_filter.ref=f"A4:{get_column_letter(len(kopf))}{ws.max_row}"
ws=wb.active; ws.title='Laboraufträge offen >1 Jahr'
blatt(ws,f'Offene Laboraufträge, älter als ein Jahr ({len(la)})',
 'Quelle: LMS_Auftrag.xlsx, Datenstand 04.11.2026. Kriterium: kein technischer Abschluss und „Erstellt am“ vor mehr als 365 Tagen. Nur Aufträge ab Erstelljahr 2024.',
 ['Auftrag','Priorität','Art der Anfrage','Labor(e)','Bezeichnung','Erstellt am','Zugesagter Termin','Alter in Tagen','Auftragswert (€)','Klärung (abschließen / stornieren / läuft noch)'],
 [[r['auftrag'],r['prio'],r['anfrageart'],r['labore'].replace(';',', '),r['bezeichnung'],D(r['erstellt']),D(r['termin']),(stand-D(r['erstellt'])).days,r['wert'],None] for r in la],
 [18,9,26,14,48,13,13,10,14,40],{6,7},{8,9})
ws2=wb.create_sheet('Wartung+Kalibrierung überfällig')
blatt(ws2,f'Freigegebene Wartungs- und Kalibrieraufträge mit überschrittenem Eckendtermin ({len(wk)})',
 'Quelle: Tabelle von Basis.xlsx (SAP), Datenstand 03.11.2026. Kriterium: Auftragsart ZLB3/ZLB4, freigegeben, kein Ist-Endtermin, Eckendtermin vor dem Datenstand.',
 ['Auftrag','Art','intern/extern','Bezeichnung','Kurztext','Eckendtermin','Tage überfällig','Klärung (abschließen / stornieren / läuft noch)'],
 [[r['auftrag'],r['art'],r['ie'],r['bezeichnung'],r['kurztext'],D(r['eckende']),r['tage_ueber'],None] for r in wk],
 [14,14,13,34,50,13,10,40],{6},{7})
wb.save('ausgabe/Altlasten_offene_Auftraege.xlsx')
from collections import Counter
print(Counter(r['prio'] for r in la), Counter(r['labore'] for r in la).most_common(6), Counter(r['erstellt'][:4] for r in la))
print(Counter(r['art'] for r in wk), max(r['tage_ueber'] for r in wk))
