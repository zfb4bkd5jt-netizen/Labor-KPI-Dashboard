// Reiter „BSC“: Balanced Scorecard je Monat, Quartal oder Jahr.

dash.calc('bsc', {
  inputs: ['auftraege', 'pruefgruppen', 'stunden_auftrag', 'soll_auftraege', 'stunden_monat', 'soll_stunden', 'sap_kosten', 'bsc_manuell', 'bsc_vorgaben'],
  title: 'Balanced Scorecard je Zeitraum',
  description: 'Je Monat, Quartal oder Jahr die Einzelkennzahlen (HoQ 2) aus den Daten der anderen Reiter und daraus die drei Spitzenkennzahlen (HoQ 1). Termintreue = (S + M + L) / 3 × Gewichtung + Pünktlichkeit × Gewichtung. Budgeteinhaltung = Erfüllungsgrad Plankosten, Erfüllungsgrad Vergabe (100 %, solange die Vergabequote die maximale Vergabequote nicht überschreitet), Erfüllungsgrad Auftragsquote (Auftragsquote / Ziel 100 %, ohne Obergrenze: Übererfüllung gleicht Schwächen der anderen Kennzahlen aus) und Erfüllungsgrad Instandhaltungsquote (Stunden auf Laboraufträge und WE+FP / Soll-Stunden, im Verhältnis zum Zielwert 65 %, ohne Obergrenze), jeweils mal Gewichtung. Qualitätslevel = Dienstleistungsquote, (1 − |Methodeneinsatz − Zielwert|) und (1 − Rückweisung), jeweils mal Gewichtung. Die von Hand gepflegten Kennzahlen, SOLL-Werte, Zielwerte und Gewichtungen stammen aus den Blättern BSC_Quartal und BSC_Vorgaben der manuellen Daten. Alle Werte in Prozent.',
  fn: (auftraege, pruefgruppen, stunden_auftrag, soll_auftraege, stunden_monat, soll_stunden, sap_kosten, bsc_manuell, bsc_vorgaben) => {
    const prm = dash.params();
    const jahr = prm.jahr || '2026', art = prm.bsc_periode || 'quartal';
    // Feste Vorgaben; Stundensatz, Sachkonten und Sammelabschluss kommen aus dem Blatt BSC_Vorgaben
    const vz = (k) => (bsc_vorgaben || []).find((x) => x.schluessel === k);
    const vg = (k, d) => { const r = vz(k); return r && r.text ? String(r.text).slice(0, 10) : d; };
    const konten = (k, d) => { const r = vz(k); const l = r && r.text ? String(r.text).split(/[;,\s]+/).filter(Boolean) : []; return l.length ? l : d; };
    const FRIST = { M: 14, L: 70 };                               // Tage ab Bearbeitungsbeginn
    const FRIST_BABTEC_H = 48, SAMMEL_VON = vg('sammel_von', '2026-04-04'), SAMMEL_BIS = vg('sammel_bis', '2026-04-06');
    const SATZ = vz('stundensatz') && vz('stundensatz').wert > 0 ? vz('stundensatz').wert : 75;                                              // € je gebuchter Stunde
    const EXTERN = konten('sachkonten_extern', ['65001000', '63012000', '65602000', '65200000']), INTERN = konten('sachkonten_intern', ['94311000']);
    const LABORE = ['QLA', 'QLG', 'QLM'];
    // Vorgaben aus den manuellen Daten (Blatt BSC_Vorgaben); fehlt dort ein Wert, gilt der hier genannte
    const V = { soll_termintreue: 65, soll_budgeteinhaltung: 80, soll_qualitaetslevel: 80, ziel_methodeneinsatz: 25, ziel_plankosten: 100, ziel_auftragsquote: 100, ziel_instandhaltungsquote: 65, max_vergabequote: 20, soll_reaktion_s: 90, soll_reaktion_m: 50, soll_puenktlich_m: 50, soll_puenktlich_l: 90, max_rueckweisung: 5,
      g_reaktionszeit: 0.5, g_puenktlichkeit: 0.5, g_plankosten: 0.25, g_vergabequote: 0.25, g_auftragsquote: 0.25, g_instandhaltungsquote: 0.25,
      g_dienstleistungsquote: 0.33, g_methodeneinsatz: 0.33, g_rueckweisung: 0.33 };
    for (const r of bsc_vorgaben) if (r.schluessel in V && r.wert != null) V[r.schluessel] = r.wert;

    let stand = '';
    for (const r of auftraege) { if (r.erstellt > stand) stand = r.erstellt; if (r.abschluss && r.abschluss > stand) stand = r.abschluss; }
    const quartal = (d) => d.slice(0, 4) + '-Q' + Math.ceil(Number(d.slice(5, 7)) / 3);
    const zr = (d) => (art === 'monat' ? d.slice(0, 7) : art === 'jahr' ? d.slice(0, 4) : quartal(d));     // Zeitraum eines Datums
    const isoKW = (s) => {
      const d = new Date(s.slice(0, 10) + 'T00:00:00Z');
      d.setUTCDate(d.getUTCDate() - ((d.getUTCDay() + 6) % 7) + 3);
      const y = d.getUTCFullYear();
      return y + '-' + (1 + Math.floor((d - Date.UTC(y, 0, 1)) / 6048e5));
    };
    const Z = new Map();
    const z = (k) => { let a = Z.get(k); if (!a) { a = { zeitraum: k, n: {} }; Z.set(k, a); } return a; };
    const plus = (k, f, v) => { const a = z(k); a.n[f] = (a.n[f] || 0) + v; };

    // Aus der Auftragsliste: Reaktionszeit, Pünktlichkeit und Plankosten nur für M und L (nur dort wird geplant); Auftragsquote für alle
    const std = new Map();
    for (const s of stunden_auftrag) std.set(s.auftrag, (std.get(s.auftrag) || 0) + s.stunden);
    for (const r of auftraege) {
      if (!r.abschluss) continue;
      const k = zr(r.abschluss), p = r.prio.toLowerCase();
      if (r.prio === 'M' || r.prio === 'L') {
        plus(k, p + '_abg', 1);
        if (r.tage_ab_beginn != null && r.tage_ab_beginn <= FRIST[r.prio]) plus(k, p + '_frist', 1);
        if (r.termin) { plus(k, p + '_termin', 1); if (r.abschluss <= r.termin) plus(k, p + '_puenktlich', 1); }
        if (r.wert > 0 && std.has(r.auftrag)) { plus(k, 'plan', r.wert); plus(k, 'ist', std.get(r.auftrag) * SATZ); }
      }
      for (const l of (r.labore || '').split(';')) if (LABORE.includes(l)) plus(k, 'aq_abg', 1);
    }
    // Auftragsquote (Nenner): Soll je Labor und Monat, laufender Monat anteilig
    for (const s of soll_auftraege) {
      if (s.monat > stand.slice(0, 7)) continue;
      let soll = s.soll;
      if (s.monat === stand.slice(0, 7)) soll = s.soll * Number(stand.slice(8, 10)) / new Date(Date.UTC(Number(s.monat.slice(0, 4)), Number(s.monat.slice(5)), 0)).getUTCDate();
      plus(zr(s.monat + '-01'), 'aq_soll', soll);
    }
    // Reaktionszeit S: Babtec-Prüfgruppen, gezählt je Kalenderwoche und Auftrag wie im Reiter Termintreue
    const gesehen = new Set(), schnell = new Set();
    for (const r of pruefgruppen) {
      const tag = r.abschluss.slice(0, 10);
      if (tag >= SAMMEL_VON && tag <= SAMMEL_BIS) continue;
      const k = zr(tag), id = k + '|' + isoKW(tag) + '|' + r.auftrag;
      if (!gesehen.has(id)) { gesehen.add(id); plus(k, 's_abg', 1); }
      if (r.dauer_h <= FRIST_BABTEC_H && !schnell.has(id)) { schnell.add(id); plus(k, 's_frist', 1); }
    }
    // Instandhaltungsquote: Stunden auf Laboraufträge und WE+FP (bezahlte Leistung) / Soll-Stunden, nur vollständig erfasste Monate
    const voll = new Set();
    for (const s of soll_stunden) {
      if (s.abwesenheit_erfasst < s.personen) continue;
      voll.add(s.monat + ' ' + s.labor); plus(zr(s.monat + '-01'), 'iq_soll', s.soll_stunden);
    }
    for (const r of stunden_monat) if ((r.typ === 'Laborauftrag' || r.typ === 'WE+FP') && voll.has(r.monat + ' ' + r.labor)) plus(zr(r.monat + '-01'), 'iq_la', r.stunden);
    // Vergabequote aus den SAP-Kosten nach Buchungsmonat
    for (const r of sap_kosten) {
      if (r.monat < '2025-01') continue;
      const t = EXTERN.some((x) => r.sachkonto.includes(x)) ? 'extern' : INTERN.some((x) => r.sachkonto.includes(x)) ? 'intern' : null;
      if (t) plus(zr(r.monat + '-01'), t, r.kosten);
    }
    // Von Hand gepflegte Kennzahlen sind je Quartal erfasst: ein Monat übernimmt den Wert seines Quartals, ein Jahr den Mittelwert seiner Quartale
    const hand = (k) => {
      const qs = art === 'quartal' ? [k] : art === 'monat' ? [quartal(k + '-01')] : [1, 2, 3, 4].map((q) => k + '-Q' + q);
      const o = {};
      for (const f of ['dienstleistungsquote', 'methodeneinsatz', 'rueckweisung']) {
        const w = bsc_manuell.filter((r) => qs.includes(r.quartal) && r[f] != null).map((r) => r[f]);
        o[f] = w.length ? Math.round(100 * w.reduce((t, v) => t + v, 0) / w.length) / 100 : null;
      }
      return o;
    };

    const p = (n, d) => (d ? Math.round(1000 * n / d) / 10 : null);
    const r1 = (v) => (v == null ? null : Math.round(10 * v) / 10);
    const mittel = (...v) => (v.some((x) => x == null) ? null : v.reduce((t, x) => t + x, 0) / v.length);
    return [...Z.values()]
      .filter((a) => a.zeitraum <= zr(stand) && (jahr === 'alle' || a.zeitraum.slice(0, 4) === jahr))
      .sort((x, y) => (x.zeitraum < y.zeitraum ? -1 : 1))
      .map((a) => {
        const n = a.n, h = hand(a.zeitraum);
        const o = { zeitraum: a.zeitraum, art, laufend: a.zeitraum === zr(stand) };
        o.s = p(n.s_frist || 0, n.s_abg); o.m = p(n.m_frist || 0, n.m_abg); o.l = p(n.l_frist || 0, n.l_abg);
        o.puenktlich_m = p(n.m_puenktlich || 0, n.m_termin); o.puenktlich_l = p(n.l_puenktlich || 0, n.l_termin);
        o.puenktlichkeit = r1(mittel(o.puenktlich_m, o.puenktlich_l));
        o.plankosten = p(n.ist || 0, n.plan);
        o.plankosten_erfuellung = o.plankosten == null ? null : r1(Math.max(0, 100 - Math.abs(o.plankosten - V.ziel_plankosten)));
        o.vergabequote = p(n.extern || 0, (n.extern || 0) + (n.intern || 0));
        o.eigenleistung = o.vergabequote == null ? null : r1(100 - o.vergabequote);
        // Schwelle: 100 %, solange die Vergabequote die maximale Vergabequote nicht überschreitet; darüber Eigenleistungsquote im Verhältnis zu ihrem SOLL
        o.vergabe_erfuellung = o.eigenleistung == null ? null : r1(Math.min(100, 100 * o.eigenleistung / (100 - V.max_vergabequote)));
        o.auftragsquote = p(n.aq_abg || 0, n.aq_soll);
        o.auftragsquote_erfuellung = o.auftragsquote == null ? null : r1(100 * o.auftragsquote / V.ziel_auftragsquote);   // ohne Deckel: Übererfüllung gleicht Schwächen der anderen Kennzahlen aus
        o.instandhaltungsquote = p(n.iq_la || 0, n.iq_soll);
        o.instandhaltungsquote_erfuellung = o.instandhaltungsquote == null ? null : r1(100 * o.instandhaltungsquote / V.ziel_instandhaltungsquote);   // ohne Deckel
        o.dienstleistungsquote = h.dienstleistungsquote; o.methodeneinsatz = h.methodeneinsatz; o.rueckweisung = h.rueckweisung;
        const reaktion = mittel(o.s, o.m, o.l);
        o.termintreue = reaktion == null || o.puenktlichkeit == null ? null : r1(reaktion * V.g_reaktionszeit + o.puenktlichkeit * V.g_puenktlichkeit);
        o.budgeteinhaltung = [o.plankosten_erfuellung, o.vergabe_erfuellung, o.auftragsquote_erfuellung, o.instandhaltungsquote_erfuellung].some((v) => v == null) ? null
          : r1(o.plankosten_erfuellung * V.g_plankosten + o.vergabe_erfuellung * V.g_vergabequote + o.auftragsquote_erfuellung * V.g_auftragsquote + o.instandhaltungsquote_erfuellung * V.g_instandhaltungsquote);
        o.qualitaetslevel = [o.dienstleistungsquote, o.methodeneinsatz, o.rueckweisung].some((v) => v == null) ? null
          : r1(o.dienstleistungsquote * V.g_dienstleistungsquote + (100 - Math.abs(Math.abs(o.methodeneinsatz) - V.ziel_methodeneinsatz)) * V.g_methodeneinsatz + V.g_rueckweisung * (100 - Math.abs(o.rueckweisung)));
        o.soll_termintreue = V.soll_termintreue; o.soll_budgeteinhaltung = V.soll_budgeteinhaltung; o.soll_qualitaetslevel = V.soll_qualitaetslevel;
        o.soll_eigenleistung = 100 - V.max_vergabequote; o.soll_reaktion_s = V.soll_reaktion_s; o.soll_reaktion_m = V.soll_reaktion_m; o.soll_puenktlich_m = V.soll_puenktlich_m; o.soll_puenktlich_l = V.soll_puenktlich_l; o.max_rueckweisung = V.max_rueckweisung;
        return o;
      });
  },
});

(() => {
  const F = window.LKfmt;
  const KOPF = ['termintreue', 'budgeteinhaltung', 'qualitaetslevel'];
  // [HoQ, Bezeichnung, Feld, Spitzenkennzahl?, Feld mit SOLL (mindestens)]
  const ZEILEN = [
    ['HoQ 1', 'Termintreue', 'termintreue', true, 'soll_termintreue'], ['HoQ 1', 'Budgeteinhaltung', 'budgeteinhaltung', true, 'soll_budgeteinhaltung'], ['HoQ 1', 'Qualitätslevel', 'qualitaetslevel', true, 'soll_qualitaetslevel'],
    ['HoQ 2', 'Reaktionszeit S (S_Babtec)', 's', false, 'soll_reaktion_s'], ['HoQ 2', 'Reaktionszeit M', 'm', false, 'soll_reaktion_m'], ['HoQ 2', 'Reaktionszeit L', 'l'],
    ['HoQ 2', 'Pünktlichkeit M', 'puenktlich_m', false, 'soll_puenktlich_m'], ['HoQ 2', 'Pünktlichkeit L', 'puenktlich_l', false, 'soll_puenktlich_l'], ['HoQ 2', 'Pünktlichkeit (Mittel aus M und L)', 'puenktlichkeit'],
    ['HoQ 2', 'Plankostenerfüllung M und L (IST / PLAN)', 'plankosten'], ['HoQ 2', 'Erfüllungsgrad Plankosten (100 % − Abweichung vom Ziel)', 'plankosten_erfuellung'],
    ['HoQ 2', 'Vergabequote (extern)', 'vergabequote'], ['HoQ 2', 'Eigenleistungsquote (100 % − Vergabequote)', 'eigenleistung', false, 'soll_eigenleistung'], ['HoQ 2', 'Erfüllungsgrad Vergabe (100 % bis zur maximalen Vergabequote)', 'vergabe_erfuellung'],
    ['HoQ 2', 'Auftragsquote', 'auftragsquote'], ['HoQ 2', 'Erfüllungsgrad Auftragsquote (Auftragsquote / Ziel, ohne Obergrenze)', 'auftragsquote_erfuellung'],
    ['HoQ 2', 'Instandhaltungsquote (Stunden auf Laboraufträge und WE+FP / Soll-Stunden)', 'instandhaltungsquote'], ['HoQ 2', 'Erfüllungsgrad Instandhaltungsquote (Instandhaltungsquote / Ziel, ohne Obergrenze)', 'instandhaltungsquote_erfuellung'],
    ['HoQ 2', 'Dienstleistungsquote (von Hand)', 'dienstleistungsquote'], ['HoQ 2', 'Methodeneinsatz (von Hand)', 'methodeneinsatz'], ['HoQ 2', 'Rückweisung (von Hand)', 'rueckweisung', false, 'max_rueckweisung', 'max'],
  ];
  const zName = (k) => (k.length === 4 ? k : k.includes('Q') ? k.slice(5) + ' ' + k.slice(0, 4) : F.fMonth(k));
  const rows = () => { const s = dash.data('bsc'); return s.status === 'ok' ? s.data || [] : null; };
  const soll = (feld) => { const r = rows(); return feld && r && r.length && r[0][feld] != null ? r[0][feld] : null; };   // SOLL (min.) aus den manuellen Daten
  // Kleine Verlaufskurve je Kennzahl über die gezeigten Zeiträume
  const verlauf = (werte, name) => {
    const td = document.createElement('td'); td.className = 'spark';
    const pts = werte.map((v, i) => [i, v]).filter((p) => p[1] != null);
    if (pts.length < 2) return td;
    const W = 72, H = 18, lo = d3.min(pts, (p) => p[1]), hi = d3.max(pts, (p) => p[1]);
    const sx = (i) => 3 + i * (W - 6) / Math.max(1, werte.length - 1), sy = (v) => (hi === lo ? H / 2 : H - 3 - (v - lo) * (H - 6) / (hi - lo));
    const svg = d3.create('svg').attr('width', W).attr('height', H).attr('viewBox', `0 0 ${W} ${H}`).attr('role', 'img').attr('aria-label', 'Verlauf ' + name);
    svg.append('path').attr('fill', 'none').attr('stroke-width', 1.5).style('stroke', dash.colors[0]).attr('d', d3.line().x((p) => sx(p[0])).y((p) => sy(p[1]))(pts));
    const l = pts[pts.length - 1];
    svg.append('circle').attr('cx', sx(l[0])).attr('cy', sy(l[1])).attr('r', 2.2).style('fill', dash.colors[0]);
    td.append(svg.node());
    return td;
  };
  const zelle = (tag, text, cls) => { const e = document.createElement(tag); e.textContent = text; if (cls) e.className = cls; return e; };

  // Kacheln: letzter abgeschlossener Zeitraum der Auswahl (sonst der laufende)
  const bezug = () => { const r = rows(); if (!r || !r.length) return null; const fertig = r.filter((x) => !x.laufend); return fertig.length ? fertig[fertig.length - 1] : r[r.length - 1]; };
  dash.draw('bsc_q', (el) => { const r = bezug(); el.textContent = r ? zName(r.zeitraum) + (r.laufend ? ' (laufend)' : '') : '—'; });
  for (const k of KOPF) {
    dash.draw('bsc_' + k, (el) => {
      const r = bezug(), v = r ? r[k] : null, s = soll('soll_' + k);
      el.textContent = v == null ? '—' : F.fPct(v);
      el.classList.remove('good', 'bad');
      if (v != null && s != null) el.classList.add(v >= s ? 'good' : 'bad');
    });
    dash.draw('bsc_' + k + '_soll', (el) => { const s = soll('soll_' + k); el.textContent = s == null ? '—' : F.fPct(s); });
  }

  dash.draw('tb_bsc_kopf', (tr) => {
    const r = rows();
    tr.replaceChildren(zelle('th', 'HoQ'), zelle('th', 'Kennzahl', 'l'), zelle('th', 'SOLL'), zelle('th', 'Verlauf'));
    for (const q of r || []) tr.append(zelle('th', zName(q.zeitraum) + (q.laufend ? ' (laufend)' : '')));
  });
  dash.draw('tb_bsc', (tb) => {
    const r = rows();
    tb.replaceChildren();
    if (!r) return;
    for (const [hoq, name, feld, spitze, sollFeld, art] of ZEILEN) {
      const s = soll(sollFeld);
      const tr = document.createElement('tr');
      tr.append(zelle('td', hoq), zelle('td', name, 'l'), zelle('td', s != null ? (art === 'max' ? '≤ ' : '≥ ') + F.fPct(s) : ''), verlauf(r.map((q) => q[feld]), name));
      for (const q of r) {
        const v = q[feld];
        const td = zelle('td', v == null ? '—' : F.fPct(v));
        if (spitze) td.style.fontWeight = '600';
        if (v != null && s != null) td.classList.add((art === 'max' ? v <= s : v >= s) ? 'good' : 'bad');
        tr.append(td);
      }
      if (spitze) tr.firstChild.nextSibling.style.fontWeight = '600';
      tb.append(tr);
    }
  });
})();
