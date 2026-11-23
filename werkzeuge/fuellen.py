import re, zipfile, shutil, sys
from xml.sax.saxutils import escape

GEMEIN = {
 'A6': 'Leadership Labor',
 'D6': 'Wird jährlich in Relation zu vorhandenen Ressourcen und Managementvorgaben festgelegt',
 'H6': 'Bei Prozesskennzahlen erfolgt quartalsweise Rückmeldung mittels Tool zur Reifegradcontrolling der Prozesslandschaft.',
 'K6': 'Director Laboratory',
 'E10': 'Labor-KPI-Dashboard (Reiter BSC), Excel',
 'L10': 'Director Laboratory',
 'L14': 'Director Laboratory',
 'A18': 'Labor-KPI-Dashboard, Reiter BSC (Kacheln und Tabelle je Monat, Quartal oder Jahr)\nReifegrad-Tool Prozesslandschaft',
 'H18': 'mind. quartalsweise',
 'J18': 'Reifegrad-Tool Prozesslandschaft - \njahresweise',
 'L18': 'Director Laboratory',
}
AGG = 'Monat, Quartal, Jahr; jeweils aus den Einzeldaten des Zeitraums gerechnet, nicht als Mittelwert der Monate. Gesamtes Labor.'

KPI = {
'Termintreue': {
 'A3': 'Termintreue',
 'B3': 'Die Termintreue fasst die zeitbezogenen KPIs des Labors zusammen: die Reaktionszeiten der Auftragsarten S, M und L sowie die Pünktlichkeit gegenüber dem zugesagten Termin. Sie zeigt, wie zuverlässig das Labor Aufträge in der vorgegebenen Frist und zum zugesagten Termin abschließt. Angabe in Prozent.',
 'H3': '(Reaktionszeit S + Reaktionszeit M + Reaktionszeit L) / 3 × Gewichtung Reaktionszeit + Pünktlichkeit × Gewichtung Pünktlichkeit\n\nGewichtung Reaktionszeit 0,5, Gewichtung Pünktlichkeit 0,5',
 'F6': '>= 65 %',
 'A10': 'Labor-Management-System dacore (Export LMS_Auftrag), Babtec-Prüfgruppen (Export LMS_Prüfgruppe), manuelle Daten (Blatt BSC_Vorgaben)',
 'G10': 'Monat, Quartal, Jahr (nach Datum des technischen Abschlusses)',
 'J10': 'monatlich',
 'A14': ('Reaktionszeit S (S_Babtec): Anteil der Babtec-Aufträge der Wareneingangs- und Fertigungsprüfung, deren Prüfgruppe höchstens 48 Stunden nach Anlage technisch abgeschlossen wurde; gezählt je Kalenderwoche und Auftrag. Abschlüsse im Sammelabschluss vom 04.–06.04.2026 werden nicht gewertet.\n'
         'Reaktionszeit M / L: Anteil der im Zeitraum abgeschlossenen M- bzw. L-Aufträge, die höchstens 14 bzw. 70 Kalendertage nach Bearbeitungsbeginn technisch abgeschlossen wurden.\n'
         'Pünktlichkeit: Mittelwert aus Pünktlichkeit M und Pünktlichkeit L. Je Auftragsart der Anteil der abgeschlossenen Aufträge mit zugesagtem Termin, deren technischer Abschluss am oder vor dem Termin liegt. Nur M und L, weil das Labor nur für diese Auftragsarten plant.\n'
         'Termintreue = Mittelwert der drei Reaktionszeiten × 0,5 + Pünktlichkeit × 0,5. Gewichtungen und SOLL stehen im Blatt BSC_Vorgaben der manuellen Daten.'),
 'E18': AGG,
 'A22': 'Ist-Werte 2026 (Datenstand 04.11.2026): Q1 81,6 %, Q2 74,2 %, Q3 81,3 %, Q4 (laufend) 73,1 %; Jahr 78,4 %.\n2025: 78,1 % (Q1 68,6 %, Q2 82,7 %, Q3 83,0 %, Q4 77,6 %).',
 'E22': 'Abweichend vom bisherigen Power-BI-Bericht: Kalenderwochen mit Jahr; im Nenner der Pünktlichkeit nur Aufträge mit zugesagtem Termin; L-Aufträge, die vor dem Bearbeitungsbeginn abgeschlossen sind, zählen als fristgerecht. Die Babtec-Prüfgruppen kennen kein Labor.',
 'I22': '-',
 'row': {14: 105, 22: 80.1},
},
'Budgeteinhaltung': {
 'A3': 'Budgeteinhaltung',
 'B3': 'Die Budgeteinhaltung fasst die monetären und kapazitätsbezogenen KPIs des Labors zusammen: Plankostenerfüllung, Vergabequote (als Eigenleistungsquote), Auftragsquote und Instandhaltungsquote. Jede Einzelkennzahl geht als Erfüllungsgrad gegenüber ihrem Zielwert ein. Angabe in Prozent.',
 'H3': 'Erfüllungsgrad Plankosten × G + Eigenleistungsquote × G + Erfüllungsgrad Auftragsquote × G + Erfüllungsgrad Instandhaltungsquote × G\n\nGewichtung G je 0,25',
 'F6': '>= 80 %',
 'A10': 'Labor-Management-System dacore (Exporte LMS_Auftrag, LMS_gebuchte_Stunden), SAP (Instandhaltungskosten), manuelle Daten (Soll-Aufträge, Abwesenheiten, FTE je Monat, Arbeitstage, BSC_Vorgaben)',
 'G10': 'Monat, Quartal, Jahr (nach technischem Abschluss, Buchungsmonat bzw. Monat der Stundenbuchung)',
 'J10': 'monatlich',
 'A14': ('Erfüllungsgrad Plankosten = 100 % − |Plankostenerfüllung − 100 %|. Plankostenerfüllung = Summe IST-Kosten / Summe PLAN-Kosten der abgeschlossenen M- und L-Aufträge; IST = gebuchte Stunden × Stundensatz (75 €), PLAN = Auftragswert. Unter- und Überschreitung zählen gleich.\n'
         'Eigenleistungsquote = 100 % − Vergabequote. Vergabequote = externe Leistung / (interne + externe Leistung) aus SAP nach Buchungsmonat; extern: Sachkonten 65001000, 63012000, 65602000, 65200000; intern: 94311000. Ziel: Vergabequote höchstens 20 %.\n'
         'Erfüllungsgrad Auftragsquote = Auftragsquote / Zielwert 100 %, ohne Obergrenze. Auftragsquote = abgeschlossene Aufträge von QLA, QLG und QLM / Soll-Aufträge; der laufende Monat zählt anteilig.\n'
         'Erfüllungsgrad Instandhaltungsquote = Instandhaltungsquote / Zielwert 65 %, ohne Obergrenze. Instandhaltungsquote = auf Laboraufträge (S, M, L) und WE+FP gebuchte Stunden / Soll-Stunden; Soll-Stunden = (Arbeitstage − Abwesenheitstage) × FTE des Monats × 8 h; nur Monate mit vollständig erfassten Abwesenheiten.\n'
         'Stundensatz, Sachkonten, Zielwerte, Gewichtungen und SOLL stehen im Blatt BSC_Vorgaben der manuellen Daten.'),
 'E18': AGG,
 'A22': 'Ist-Werte 2026 (Datenstand 04.11.2026): Q1 101,2 %, Q2 99,2 %, Q3 98,2 %, Q4 (laufend) 97,7 %; Jahr 99,9 %.\n2025: 87,6 % (Q1 87,7 %, Q2 81,6 %, Q3 91,3 %, Q4 89,5 %).',
 'E22': 'Eine Übererfüllung von Auftrags- und Instandhaltungsquote gleicht Schwächen der anderen Einzelkennzahlen aus; Werte über 100 % sind daher möglich. WE+FP wird erst seit März 2026 gebucht; davor enthält die Instandhaltungsquote nur Laboraufträge.',
 'I22': 'SOLL (80 %) und Gewichtungen an die neuen Erfüllungsgrade anpassen; Rechenweg der Instandhaltungsquote abschließend festlegen; SAP-Buchung Oktober 2026 (interne Leistung 697.559 €) klären. – Director Laboratory, Termin offen',
 'row': {14: 125, 22: 80.1},
},
'Qualitätslevel': {
 'A3': 'Qualitätslevel',
 'B3': 'Das Qualitätslevel fasst die qualitätsbezogenen KPIs des Labors zusammen: Dienstleistungsquote, Methodeneinsatz und Rückweisung. Es zeigt, wie weit das Labor Aufträge im eigenen Laborscope abdeckt, Methoden in großen Aufträgen einsetzt und Ergebnisse ohne Rückweisung durch den Auftraggeber liefert. Angabe in Prozent.',
 'H3': 'Dienstleistungsquote × G + (100 % − |Methodeneinsatz − Zielwert|) × G + (100 % − Rückweisung) × G\n\nGewichtung G je 0,33, Zielwert Methodeneinsatz 25 %',
 'F6': '>= 80 %',
 'A10': 'Manuelle Erhebung durch die Laborleitung; Eintrag in den manuellen Daten (Blatt BSC_Quartal), Vorgaben im Blatt BSC_Vorgaben',
 'G10': 'Quartal',
 'J10': 'quartalsweise',
 'A14': ('Dienstleistungsquote: Anzahl der Aufträge innerhalb der im Laborscope beschriebenen Verfahren und Grenzen bezogen auf die Gesamtauftragsanzahl.\n'
         'Methodeneinsatz: Anzahl der Aufträge mit Methodeneinsatz bezogen auf die Gesamtanzahl der großen Aufträge; bewertet wird die Abweichung vom Zielwert 25 %, nach oben wie nach unten.\n'
         'Rückweisung: Anzahl der vom Auftraggeber zurückgewiesenen Aufträge bezogen auf die Gesamtauftragsanzahl.\n'
         'Die drei Werte werden je Quartal von Hand eingetragen. Ein Monat übernimmt den Wert seines Quartals, ein Jahr den Mittelwert seiner Quartale. Gewichtungen, Zielwert und SOLL stehen im Blatt BSC_Vorgaben der manuellen Daten.'),
 'E18': 'Quartal, Jahr (Mittelwert der Quartale). Gesamtes Labor.',
 'A22': 'Ist-Werte: 2025 bis Q2 2026 je 90,8 % (Datenstand 04.11.2026). Ab Q3 2026 sind noch keine Werte eingetragen.',
 'E22': 'Die Gewichtungen summieren sich auf 0,99; der Höchstwert ist daher 99 %. Die Eingangswerte stehen seit 2025 unverändert auf 100 % / 0 % / 0 %, das Ergebnis ist damit konstant 90,8 %.',
 'I22': 'Werte ab Q3 2026 erheben; Erhebungsweg der drei Eingangswerte festlegen; Methodeneinsatz (0 % gegenüber Zielwert 25 %) bewerten. – Director Laboratory, Termin offen',
 'row': {14: 100, 22: 80.1},
},
}

def setze(xml, ref, text):
    pat = re.compile(r'<c r="' + ref + r'"((?:(?!/>)[^>])*?)(?:\s*/>|>.*?</c>)', re.S)
    m = pat.search(xml); assert m, ref
    attrs = re.sub(r'\s+t="[^"]*"', '', m.group(1)).rstrip()
    neu = '<c r="%s"%s t="inlineStr"><is><t xml:space="preserve">%s</t></is></c>' % (ref, attrs, escape(text))
    return xml[:m.start()] + neu + xml[m.end():]

def zeile(xml, r, ht):
    pat = re.compile(r'(<row r="%d"[^>]*?)\sht="[^"]*"' % r)
    assert pat.search(xml), r
    return pat.sub(lambda m: m.group(1) + ' ht="%s"' % ht, xml, count=1)

def baue(src, ziel, name, png):
    k = KPI[name]
    zin = zipfile.ZipFile(src); teile = {n: zin.read(n) for n in zin.namelist()}; zin.close()
    xml = teile['xl/worksheets/sheet1.xml'].decode('utf-8')
    for ref, t in {**GEMEIN, **{a: b for a, b in k.items() if a != 'row'}}.items():
        xml = setze(xml, ref, t)
    # Bemerkungen in derselben Schrift wie Besonderheiten (die Vorlage setzt dort den grauen Platzhalterstil)
    s22 = re.search(r'<c r="E22" s="(\d+)"', xml).group(1)
    xml = re.sub(r'<c r="A22" s="\d+"', '<c r="A22" s="%s"' % s22, xml, count=1)
    for r, ht in k['row'].items():
        xml = zeile(xml, r, ht)
    bild = open(png, 'rb').read()
    if 'xl/drawings/drawing1.xml' in teile:
        # Platzhalter: Beispielbild ersetzen, Hinweisrechteck "ggf. grafische Darstellung" entfernen
        dr = teile['xl/drawings/drawing1.xml'].decode('utf-8')
        dr = re.sub(r'<xdr:twoCellAnchor>(?:(?!</xdr:twoCellAnchor>).)*?<xdr:sp .*?</xdr:twoCellAnchor>', '', dr, flags=re.S)
        assert 'ggf. grafische' not in dr and '<xdr:pic>' in dr
        teile['xl/drawings/drawing1.xml'] = dr.encode('utf-8')
        rel = teile['xl/drawings/_rels/drawing1.xml.rels'].decode()
        tgt = re.search(r'Target="\.\./media/([^"]+)"', rel).group(1)
        teile['xl/media/' + tgt] = bild
    else:
        # Budget-Datei ohne Zeichnung: Grafik an derselben Stelle wie in der Vorlage einfügen
        teile['xl/media/kpi_grafik.png'] = bild
        teile['xl/drawings/drawing1.xml'] = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<xdr:wsDr xmlns:xdr="http://schemas.openxmlformats.org/drawingml/2006/spreadsheetDrawing" xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"><xdr:twoCellAnchor editAs="oneCell"><xdr:from><xdr:col>2</xdr:col><xdr:colOff>297656</xdr:colOff><xdr:row>17</xdr:row><xdr:rowOff>50030</xdr:rowOff></xdr:from><xdr:to><xdr:col>3</xdr:col><xdr:colOff>762000</xdr:colOff><xdr:row>17</xdr:row><xdr:rowOff>1160838</xdr:rowOff></xdr:to><xdr:pic><xdr:nvPicPr><xdr:cNvPr id="4" name="Grafik 3"/><xdr:cNvPicPr><a:picLocks noChangeAspect="1"/></xdr:cNvPicPr></xdr:nvPicPr><xdr:blipFill><a:blip xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" r:embed="rId1"/><a:stretch><a:fillRect/></a:stretch></xdr:blipFill><xdr:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="1583531" cy="1110808"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></xdr:spPr></xdr:pic><xdr:clientData/></xdr:twoCellAnchor></xdr:wsDr>').encode()
        teile['xl/drawings/_rels/drawing1.xml.rels'] = b'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="../media/kpi_grafik.png"/></Relationships>'
        srel = teile['xl/worksheets/_rels/sheet1.xml.rels'].decode()
        assert 'rIdKpiDr' not in srel
        srel = srel.replace('</Relationships>', '<Relationship Id="rIdKpiDr" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/drawing" Target="../drawings/drawing1.xml"/></Relationships>')
        teile['xl/worksheets/_rels/sheet1.xml.rels'] = srel.encode()
        assert '<legacyDrawingHF' in xml and '<drawing ' not in xml
        xml = re.sub(r'(<legacyDrawingHF)', r'<drawing r:id="rIdKpiDr"/>\1', xml, count=1)
        ct = teile['[Content_Types].xml'].decode()
        if 'Extension="png"' not in ct:
            ct = ct.replace('<Default ', '<Default Extension="png" ContentType="image/png"/><Default ', 1)
        ct = ct.replace('</Types>', '<Override PartName="/xl/drawings/drawing1.xml" ContentType="application/vnd.openxmlformats-officedocument.drawing+xml"/></Types>')
        teile['[Content_Types].xml'] = ct.encode()
    teile['xl/worksheets/sheet1.xml'] = xml.encode('utf-8')
    zout = zipfile.ZipFile(ziel, 'w', zipfile.ZIP_DEFLATED)
    zin = zipfile.ZipFile(src)
    namen = zin.namelist() + [n for n in teile if n not in zin.namelist()]
    for n in namen: zout.writestr(n, teile[n])
    zout.close()

baue('/home/claude/kpi_in/KPI_Termintreue.xlsx', '/home/claude/kpi_out/KPI_Termintreue.xlsx', 'Termintreue', 'tt.png')
baue('/home/claude/kpi_in/KPI_Budgeteinhaltung.xlsx', '/home/claude/kpi_out/KPI_Budgeteinhaltung.xlsx', 'Budgeteinhaltung', 'be.png')
baue('/home/claude/kpi_in/KPI_Qualitaetslevel.xlsx', '/home/claude/kpi_out/KPI_Qualitaetslevel.xlsx', 'Qualitätslevel', 'ql.png')
print('fertig')
