// Reiter „Termintreue (HoQ 1)“: Kennzahlen der Power-BI-Seite HoQ_1_Termintreue.

dash.calc('tt_woche', {
  inputs: ['auftraege'],
  title: 'Termintreue M und L je Kalenderwoche',
  description: 'Je ISO-Kalenderwoche des technischen Abschlusses: Reaktionszeit (Abschluss höchstens 14 bzw. 70 Tage nach Bearbeitungsbeginn) und Pünktlichkeit (Abschluss bis zum zugesagten Termin) für M- und L-Aufträge, für Jahr und Labor der Auswahl.',
  fn: (auftraege) => {
    const p = dash.params();
    const jahr = p.jahr || '2026', lab = p.labor || '';
    const qu = p.quartal || '', mon = p.monat || '';
    const FRIST = { S: 2, M: 14, L: 70 }; // Tage ab Bearbeitungsbeginn (S: 48 Stunden)
    const isoKW = (s) => {
      const d = new Date(s.slice(0, 10) + 'T00:00:00Z');
      d.setUTCDate(d.getUTCDate() - ((d.getUTCDay() + 6) % 7) + 3); // Donnerstag der Woche
      const y = d.getUTCFullYear();
      const w = 1 + Math.floor((d - Date.UTC(y, 0, 1)) / 6048e5);
      return y + '-KW' + String(w).padStart(2, '0');
    };
    const map = new Map();
    for (const r of auftraege) {
      if (!r.abschluss || !FRIST[r.prio]) continue;
      if (lab && !(r.labore || '').split(';').includes(lab)) continue;
      const t = r.abschluss;
      if ((jahr !== 'alle' && t.slice(0, 4) !== jahr) || (mon && t.slice(5, 7) !== mon) || (qu && String(Math.ceil(Number(t.slice(5, 7)) / 3)) !== qu)) continue;
      const kw = isoKW(t);
      let a = map.get(kw);
      if (!a) { a = { kw, s_abg: 0, s_in_frist: 0, s_mit_termin: 0, s_puenktlich_n: 0, m_abg: 0, m_in_frist: 0, m_mit_termin: 0, m_puenktlich_n: 0, l_abg: 0, l_in_frist: 0, l_mit_termin: 0, l_puenktlich_n: 0 }; map.set(kw, a); }
      const k = r.prio.toLowerCase(), frist = FRIST[r.prio];
      a[k + '_abg']++;
      if (r.tage_ab_beginn != null && r.tage_ab_beginn <= frist) a[k + '_in_frist']++;
      if (r.termin) { a[k + '_mit_termin']++; if (r.abschluss <= r.termin) a[k + '_puenktlich_n']++; }
    }
    const q = (n, d) => (d ? Math.round(1000 * n / d) / 10 : null);
    return [...map.values()].sort((x, y) => (x.kw < y.kw ? -1 : 1)).map((a) => ({
      ...a,
      m_reaktion: q(a.m_in_frist, a.m_abg), m_puenktlich: q(a.m_puenktlich_n, a.m_mit_termin),
      l_reaktion: q(a.l_in_frist, a.l_abg), l_puenktlich: q(a.l_puenktlich_n, a.l_mit_termin),
      s_reaktion: q(a.s_in_frist, a.s_abg),
    }));
  },
});

dash.calc('tt_s_woche', {
  inputs: ['pruefgruppen', 'bsc_vorgaben'],
  title: 'Prüfgruppen (Babtec) je Kalenderwoche',
  description: 'Je ISO-Kalenderwoche des technischen Abschlusses: Anteil der Babtec-Aufträge mit Abschluss innerhalb von 48 Stunden nach Anlage sowie Durchlaufzeit der Wareneingangsprüfung in Stunden (Mittelwert und Median). Der Sammelabschluss vom 04.–06.04.2026 ist ausgenommen.',
  fn: (pruefgruppen, bsc_vorgaben) => {
    const p = dash.params();
    const jahr = p.jahr || '2026', qu = p.quartal || '', mon = p.monat || '';
    const FRIST_H = 48;
    const tx = (k, d) => { const r = (bsc_vorgaben || []).find((x) => x.schluessel === k); return r && r.text ? String(r.text).slice(0, 10) : d; };
    const AUS_VON = tx('sammel_von', '2026-04-04'), AUS_BIS = tx('sammel_bis', '2026-04-06'); // Sammelabschluss alter Prüfgruppen, nicht gewertet; aus dem Blatt BSC_Vorgaben
    const isoKW = (s) => {
      const d = new Date(s.slice(0, 10) + 'T00:00:00Z');
      d.setUTCDate(d.getUTCDate() - ((d.getUTCDay() + 6) % 7) + 3);
      const y = d.getUTCFullYear();
      const w = 1 + Math.floor((d - Date.UTC(y, 0, 1)) / 6048e5);
      return y + '-KW' + String(w).padStart(2, '0');
    };
    const map = new Map();
    for (const r of pruefgruppen) {
      const tag = r.abschluss.slice(0, 10);
      if (tag >= AUS_VON && tag <= AUS_BIS) continue;
      if ((jahr !== 'alle' && tag.slice(0, 4) !== jahr) || (mon && tag.slice(5, 7) !== mon) || (qu && String(Math.ceil(Number(tag.slice(5, 7)) / 3)) !== qu)) continue;
      const kw = isoKW(tag);
      let a = map.get(kw);
      if (!a) { a = { kw, alle: new Set(), schnell: new Set(), we: [] }; map.set(kw, a); }
      a.alle.add(r.auftrag);
      if (r.dauer_h <= FRIST_H) a.schnell.add(r.auftrag);
      if (r.art === 'WE') a.we.push(r.dauer_h);
    }
    return [...map.values()].sort((x, y) => (x.kw < y.kw ? -1 : 1)).map((a) => {
      const s = a.we.slice().sort((x, y) => x - y), m = s.length >> 1;
      return {
        kw: a.kw,
        abg: a.alle.size,
        in48: a.schnell.size,
        anteil48: a.alle.size ? Math.round(1000 * a.schnell.size / a.alle.size) / 10 : null,
        we_n: s.length,
        we_mittel_h: s.length ? Math.round(10 * s.reduce((t, v) => t + v, 0) / s.length) / 10 : null,
        we_median_h: s.length ? Math.round(10 * (s.length % 2 ? s[m] : (s[m - 1] + s[m]) / 2)) / 10 : null,
      };
    });
  },
});

dash.calc('tt_s_gesamt', {
  inputs: ['tt_s_woche', 'tt_woche'],
  title: 'Reaktionszeit S je Kalenderwoche: Babtec und Babtec inklusive LMS',
  description: 'Je ISO-Kalenderwoche: S_Babtec = Anteil der Babtec-Aufträge mit Abschluss innerhalb von 48 Stunden nach Anlage. S_Babtec_inkl_LMS = dieselbe Zählung zuzüglich der S-Aufträge aus der LMS-Auftragsliste (Abschluss höchstens 48 Stunden nach Bearbeitungsbeginn). Der Laborfilter wirkt nur auf den LMS-Teil.',
  fn: (tt_s_woche, tt_woche) => {
    const map = new Map();
    const zeile = (kw) => { let a = map.get(kw); if (!a) { a = { kw, babtec_abg: 0, babtec_in48: 0, lms_abg: 0, lms_in48: 0 }; map.set(kw, a); } return a; };
    for (const r of tt_s_woche || []) { const a = zeile(r.kw); a.babtec_abg += r.abg; a.babtec_in48 += r.in48; }
    for (const r of tt_woche || []) { if (!r.s_abg) continue; const a = zeile(r.kw); a.lms_abg += r.s_abg; a.lms_in48 += r.s_in_frist; }
    const q = (n, d) => (d ? Math.round(1000 * n / d) / 10 : null);
    return [...map.values()].sort((x, y) => (x.kw < y.kw ? -1 : 1)).map((a) => ({ ...a, inkl_abg: a.babtec_abg + a.lms_abg, inkl_in48: a.babtec_in48 + a.lms_in48,
      s_babtec: q(a.babtec_in48, a.babtec_abg), s_babtec_inkl_lms: q(a.babtec_in48 + a.lms_in48, a.babtec_abg + a.lms_abg) }));
  },
});

dash.calc('tt_kpi', {
  inputs: ['tt_woche', 'tt_s_woche'],
  title: 'Termintreue im gewählten Zeitraum',
  description: 'Summen der Wochenwerte über den gewählten Zeitraum: Reaktionszeit und Pünktlichkeit für M und L, Anteil der Prüfgruppen-Aufträge innerhalb 48 Stunden (Summe der Wochenwerte; ein Auftrag mit Abschlüssen in mehreren Wochen zählt je Woche).',
  fn: (tt_woche, tt_s_woche) => {
    const sum = (rows, f) => (rows || []).reduce((t, r) => t + (r[f] || 0), 0);
    const q = (n, d) => (d ? Math.round(1000 * n / d) / 10 : null);
    const o = {};
    for (const k of ['m', 'l']) {
      o[k + '_abg'] = sum(tt_woche, k + '_abg'); o[k + '_in_frist'] = sum(tt_woche, k + '_in_frist');
      o[k + '_mit_termin'] = sum(tt_woche, k + '_mit_termin'); o[k + '_puenktlich_n'] = sum(tt_woche, k + '_puenktlich_n');
      o[k + '_reaktion'] = q(o[k + '_in_frist'], o[k + '_abg']);
      o[k + '_puenktlich'] = q(o[k + '_puenktlich_n'], o[k + '_mit_termin']);
    }
    o.s_abg = sum(tt_s_woche, 'abg'); o.s_in48 = sum(tt_s_woche, 'in48'); o.s_anteil48 = q(o.s_in48, o.s_abg);
    o.s_lms_abg = sum(tt_woche, 's_abg'); o.s_lms_in48 = sum(tt_woche, 's_in_frist');
    o.s_inkl_abg = o.s_abg + o.s_lms_abg; o.s_inkl_in48 = o.s_in48 + o.s_lms_in48; o.s_inkl_anteil48 = q(o.s_inkl_in48, o.s_inkl_abg);
    return [o];
  },
});

(() => {
  const F = window.LKfmt;

  // Kacheln
  const K = () => { const k = dash.data('tt_kpi'); return k.status === 'ok' && k.data && k.data[0] ? k.data[0] : null; };
  [['tk_s', 's_anteil48', F.fPct], ['tk_s_n', 's_in48', F.fInt], ['tk_s_d', 's_abg', F.fInt],
   ['tk_si', 's_inkl_anteil48', F.fPct], ['tk_si_n', 's_inkl_in48', F.fInt], ['tk_si_d', 's_inkl_abg', F.fInt],
   ['tk_m', 'm_reaktion', F.fPct], ['tk_m_n', 'm_in_frist', F.fInt], ['tk_m_d', 'm_abg', F.fInt],
   ['tk_l', 'l_reaktion', F.fPct], ['tk_l_n', 'l_in_frist', F.fInt], ['tk_l_d', 'l_abg', F.fInt],
   ['tk_pm', 'm_puenktlich', F.fPct], ['tk_pm_n', 'm_puenktlich_n', F.fInt], ['tk_pm_d', 'm_mit_termin', F.fInt],
   ['tk_pl', 'l_puenktlich', F.fPct], ['tk_pl_n', 'l_puenktlich_n', F.fInt], ['tk_pl_d', 'l_mit_termin', F.fInt],
  ].forEach(([name, field, fmt]) => dash.draw(name, (el) => { const r = K(); el.textContent = r && r[field] != null ? fmt(r[field]) : '—'; }));

  // Liniendiagramm je Kalenderwoche
  const kwLabel = (k, multi) => (multi ? k.slice(7) + '/' + k.slice(2, 4) : 'KW ' + k.slice(7));
  const line = (name, id, series, opt) => dash.draw(name, (el) => {
    const s = dash.data(id);
    el.replaceChildren();
    if (s.status !== 'ok') {
      if (s.status === 'error' || s.status === 'missing') { const d = document.createElement('div'); d.className = 'fail'; d.textContent = 'Daten konnten nicht geladen werden'; el.append(d); }
      return;
    }
    const rows = s.data || [];
    if (!rows.some((d) => series.some((se) => d[se.field] != null))) { const d = document.createElement('div'); d.className = 'fail'; d.textContent = 'Keine Abschlüsse in dieser Auswahl'; el.append(d); return; }
    const multi = new Set(rows.map((d) => d.kw.slice(0, 4))).size > 1;
    const W = el.clientWidth || 400, H = window.LKhoehe ? window.LKhoehe(el, 210) : 210, m = { t: 10, r: 10, b: 26, l: 46 };
    const svg = d3.select(el).append('svg').attr('width', '100%').attr('height', H).attr('viewBox', `0 0 ${W} ${H}`).attr('role', 'img').attr('aria-label', opt.aria);
    const x = d3.scalePoint().domain(rows.map((d) => d.kw)).range([m.l, W - m.r]).padding(0.3);
    const ref = typeof opt.ref === 'function' ? opt.ref() : opt.ref;   // SOLL-Linie, auch als Funktion (Wert aus den Vorgaben)
    const vals = rows.flatMap((d) => series.map((se) => d[se.field])).filter((v) => v != null).concat(ref != null ? [ref] : []);
    const y = opt.pct
      ? d3.scaleLinear().domain([Math.max(0, Math.floor(d3.min(vals) / 10) * 10), 100]).range([H - m.b, m.t])
      : d3.scaleLinear().domain([0, d3.max(vals) || 1]).nice().range([H - m.b, m.t]);
    const yFmt = (opt.pct || opt.prozent) ? (v) => v + ' %' : F.fInt;
    svg.append('g').attr('class', 'grid').attr('transform', `translate(${m.l},0)`).call(d3.axisLeft(y).ticks(4).tickSize(-(W - m.l - m.r)).tickFormat('')).call((g) => g.select('.domain').remove());
    svg.append('g').attr('transform', `translate(${m.l},0)`).call(d3.axisLeft(y).ticks(4).tickFormat(yFmt)).call((g) => g.select('.domain').remove());
    const step = Math.max(1, Math.ceil(rows.length / Math.max(1, Math.floor((W - m.l) / 58))));
    svg.append('g').attr('transform', `translate(0,${H - m.b})`).call(d3.axisBottom(x).tickValues(rows.map((d) => d.kw).filter((_, i) => i % step === 0)).tickFormat((k) => kwLabel(k, multi)).tickSizeOuter(0));
    const tip = document.createElement('div'); tip.className = 'tip'; tip.hidden = true; el.append(tip);
    if (ref != null) {
      svg.append('line').attr('x1', m.l).attr('x2', W - m.r).attr('y1', y(ref)).attr('y2', y(ref)).attr('stroke-dasharray', '4 3').style('stroke', 'var(--cds-chart-reference)');
      svg.append('text').attr('class', 'lk-ref').attr('x', W - m.r).attr('y', y(ref) - 4).attr('text-anchor', 'end').text((opt.refText || (typeof opt.ref === 'function' ? 'SOLL' : 'Ziel')) + ' ' + F.fPct(ref));
    }
    const r = rows.length > 60 ? 2 : 3;
    series.forEach((se, i) => {
      const pts = rows.filter((d) => d[se.field] != null);
      svg.append('path').datum(pts).attr('fill', 'none').attr('stroke-width', 1.75).style('stroke', dash.colors[i])
        .attr('d', d3.line().x((d) => x(d.kw)).y((d) => y(d[se.field])));
      svg.append('g').selectAll('circle').data(pts).join('circle').attr('cx', (d) => x(d.kw)).attr('cy', (d) => y(d[se.field])).attr('r', r).style('fill', dash.colors[i]);
    });
    // Eine Fangfläche je Woche, damit der Tooltip auch mit dem Finger trifft
    const bw = rows.length > 1 ? x.step() : W - m.l - m.r;
    svg.append('g').selectAll('rect').data(rows).join('rect').attr('x', (d) => x(d.kw) - bw / 2).attr('width', bw).attr('y', m.t).attr('height', H - m.t - m.b).style('fill', 'transparent')
      .on('pointermove', (ev, d) => {
        const lines = ['KW ' + d.kw.slice(7) + ' / ' + d.kw.slice(0, 4), ...opt.tip(d)];
        tip.replaceChildren(...lines.map((l, j) => { const e = document.createElement('div'); if (j === 0) e.style.fontWeight = '600'; e.textContent = l; return e; }));
        tip.hidden = false;
        const b = el.getBoundingClientRect();
        let tx = ev.clientX - b.left + 12; const ty = ev.clientY - b.top + 12;
        if (tx + tip.offsetWidth > b.width) tx = Math.max(0, ev.clientX - b.left - tip.offsetWidth - 12);
        tip.style.left = tx + 'px'; tip.style.top = ty + 'px';
      })
      .on('pointerleave', () => { tip.hidden = true; });
  });

  window.LKline = line; // auch für weitere Reiter
  const pct = (name, id, field, n, d, aria, wort, sollKey) => line(name, id, [{ field }], {
    pct: true, aria, ref: sollKey ? () => window.LKsoll(sollKey) : null,
    tip: (r) => (r[field] == null ? ['keine Abschlüsse'] : [F.fPct(r[field]), F.fInt(r[n]) + ' von ' + F.fInt(r[d]) + ' ' + wort]),
  });
  line('ch_tt_s', 'tt_s_gesamt', [{ field: 's_babtec' }, { field: 's_babtec_inkl_lms' }], {
    pct: true, ref: () => window.LKsoll('soll_reaktion_s'), aria: 'Reaktionszeit S je Kalenderwoche: Anteil innerhalb 48 Stunden, nur Babtec und Babtec inklusive LMS-S-Aufträge',
    tip: (r) => ['S_Babtec: ' + (r.s_babtec == null ? '—' : F.fPct(r.s_babtec) + ' (' + F.fInt(r.babtec_in48) + ' von ' + F.fInt(r.babtec_abg) + ')'),
      'S_Babtec_inkl_LMS: ' + F.fPct(r.s_babtec_inkl_lms) + ' (' + F.fInt(r.inkl_in48) + ' von ' + F.fInt(r.inkl_abg) + ')', 'davon LMS: ' + F.fInt(r.lms_in48) + ' von ' + F.fInt(r.lms_abg)],
  });
  pct('ch_tt_m', 'tt_woche', 'm_reaktion', 'm_in_frist', 'm_abg', 'Anteil der M-Aufträge mit Abschluss innerhalb 14 Tagen je Kalenderwoche', 'M-Aufträgen', 'soll_reaktion_m');
  pct('ch_tt_l', 'tt_woche', 'l_reaktion', 'l_in_frist', 'l_abg', 'Anteil der L-Aufträge mit Abschluss innerhalb 70 Tagen je Kalenderwoche', 'L-Aufträgen');
  pct('ch_tt_pm', 'tt_woche', 'm_puenktlich', 'm_puenktlich_n', 'm_mit_termin', 'Anteil pünktlich abgeschlossener M-Aufträge je Kalenderwoche', 'M-Aufträgen mit Termin', 'soll_puenktlich_m');
  pct('ch_tt_pl', 'tt_woche', 'l_puenktlich', 'l_puenktlich_n', 'l_mit_termin', 'Anteil pünktlich abgeschlossener L-Aufträge je Kalenderwoche', 'L-Aufträgen mit Termin', 'soll_puenktlich_l');
  line('ch_tt_dlz', 'tt_s_woche', [{ field: 'we_mittel_h' }, { field: 'we_median_h' }], {
    pct: false, aria: 'Durchlaufzeit der Wareneingangsprüfung in Stunden je Kalenderwoche, Mittelwert und Median',
    tip: (r) => (r.we_n ? ['Mittelwert: ' + F.fDec(r.we_mittel_h) + ' h', 'Median: ' + F.fDec(r.we_median_h) + ' h', F.fInt(r.we_n) + ' Prüfgruppen'] : ['keine Abschlüsse']),
  });
})();
