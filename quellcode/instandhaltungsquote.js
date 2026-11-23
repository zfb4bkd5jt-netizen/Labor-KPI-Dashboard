// Reiter „Instandhaltungsquote (HoQ 2)“: Kennzahlen der Power-BI-Seite HoQ_2_Instandhaltungsquote.

dash.calc('iq_basis', {
  inputs: ['stunden_monat', 'soll_stunden'],
  title: 'Gebuchte und Soll-Stunden je Monat und Labor',
  description: 'Je Monat und Labor (QLA, QLG, QLM) der Auswahl: Soll-Stunden = (Arbeitstage − Abwesenheitstage) × FTE × 8 und gebuchte Stunden je Kontierungstyp. IST = gebuchte Stunden ohne Urlaub und Krankheit. Monate, in denen die Abwesenheiten noch nicht für alle Personen erfasst sind, fehlen.',
  fn: (stunden_monat, soll_stunden) => {
    const p = dash.params();
    const jahr = p.jahr || '2026', qu = p.quartal || '', mon = p.monat || '', lab = p.labor || '';
    const inP = (mo) => (jahr === 'alle' || mo.slice(0, 4) === jahr) && (!mon || mo.slice(5) === mon) && (!qu || String(Math.ceil(Number(mo.slice(5)) / 3)) === qu);
    const FELD = { Laborauftrag: 'laborauftrag', 'WE+FP': 'we_fp', Wartung: 'wartung', Kalibrierung: 'kalibrierung', Sonstiges: 'sonstiges', Urlaub: 'urlaub', Krankheit: 'krankheit' };
    const map = new Map();
    for (const s of soll_stunden) {
      if (!inP(s.monat) || (lab && s.labor !== lab) || s.abwesenheit_erfasst < s.personen) continue;
      const a = { schluessel: s.monat + ' ' + s.labor, monat: s.monat, labor: s.labor, soll: s.soll_stunden, brutto: s.brutto_stunden };
      for (const f of Object.values(FELD)) a[f] = 0;
      map.set(a.schluessel, a);
    }
    for (const r of stunden_monat) {
      const a = map.get(r.monat + ' ' + r.labor);
      if (a && FELD[r.typ]) a[FELD[r.typ]] += r.stunden;
    }
    return [...map.values()].sort((x, y) => (x.schluessel < y.schluessel ? -1 : 1)).map((a) => {
      for (const f of Object.values(FELD)) a[f] = Math.round(10 * a[f]) / 10;
      const ist = a.laborauftrag + a.we_fp + a.wartung + a.kalibrierung + a.sonstiges;
      return { ...a, ist: Math.round(10 * ist) / 10, ist_mit_abwesenheit: Math.round(10 * (ist + a.urlaub + a.krankheit)) / 10 };
    });
  },
});

dash.calc('iq_auswertung', {
  inputs: ['iq_basis'],
  title: 'Buchungs- und Instandhaltungsquote nach Zeitraum, Monat und Labor',
  description: 'Summen aus den Monatswerten: eine Zeile für den gewählten Zeitraum, eine je Monat und eine je Labor. Buchungsquote (Feld quote) = IST (ohne Urlaub und Krankheit) / SOLL; Instandhaltungsquote (Feld q_instandhaltung) = auf Laboraufträge und WE+FP gebuchte Stunden / SOLL; die Anteile je Kontierungstyp beziehen sich ebenfalls auf die Soll-Stunden. „Quote wie Power BI“ zählt gebuchte Urlaubs- und Krankheitsstunden mit.',
  fn: (iq_basis) => {
    const rows = iq_basis || [];
    const FELDER = ['soll', 'brutto', 'ist', 'ist_mit_abwesenheit', 'laborauftrag', 'we_fp', 'wartung', 'kalibrierung', 'sonstiges', 'urlaub', 'krankheit'];
    const q = (n, d) => (d ? Math.round(1000 * n / d) / 10 : null);
    const zeile = (ebene, name, g) => {
      const o = { schluessel: ebene + ' ' + name, ebene, name };
      for (const f of FELDER) o[f] = Math.round(g.reduce((t, r) => t + r[f], 0));
      o.quote = q(o.ist, o.soll); o.quote_pbi = q(o.ist_mit_abwesenheit, o.soll);
      o.q_laborauftrag = q(o.laborauftrag, o.soll); o.q_we_fp = q(o.we_fp, o.soll); o.q_wartung = q(o.wartung, o.soll);
      o.q_kalibrierung = q(o.kalibrierung, o.soll); o.q_sonstiges = q(o.sonstiges, o.soll);
      o.instandhaltung = o.laborauftrag + o.we_fp; o.q_instandhaltung = q(o.instandhaltung, o.soll);   // bezahlte Leistung: Laborauftrag und WE+FP
      return o;
    };
    const monate = [...new Set(rows.map((r) => r.monat))].sort(), labore = [...new Set(rows.map((r) => r.labor))].sort();
    return [
      zeile('Zeitraum', 'gesamt', rows),
      ...monate.map((m) => zeile('Monat', m, rows.filter((r) => r.monat === m))),
      ...labore.map((l) => zeile('Labor', l, rows.filter((r) => r.labor === l))),
    ];
  },
});

(() => {
  const F = window.LKfmt;
  const std = (v) => F.fInt(v) + ' h';
  const daten = (ebene) => { const s = dash.data('iq_auswertung'); return s.status === 'ok' ? (s.data || []).filter((r) => r.ebene === ebene) : null; };

  [['iq_q', 'quote', F.fPct], ['iq_ist', 'ist', std], ['iq_soll', 'soll', std], ['iq_la', 'q_instandhaltung', F.fPct], ['iq_la_h', 'instandhaltung', std],
   ['iq_so', 'q_sonstiges', F.fPct], ['iq_so_h', 'sonstiges', std], ['iq_pbi', 'quote_pbi', F.fPct], ['iq_abw', 'ist_mit_abwesenheit', std]]
    .forEach(([name, field, fmt]) => dash.draw(name, (el) => { const d = daten('Zeitraum'); const r = d && d[0] && d[0].soll ? d[0] : null; el.textContent = r && r[field] != null ? fmt(r[field]) : '—'; }));
  dash.draw('leg3', (el) => { el.style.background = dash.colors[3]; });

  const rahmen = (el, aria, yMax, yFmt) => {
    const s = dash.data('iq_auswertung');
    el.replaceChildren();
    const hinweis = (t) => { const d = document.createElement('div'); d.className = 'fail'; d.textContent = t; el.append(d); };
    if (s.status !== 'ok') { if (s.status === 'error' || s.status === 'missing') hinweis('Daten konnten nicht geladen werden'); return null; }
    const rows = (s.data || []).filter((r) => r.ebene === 'Monat');
    if (!rows.length) { hinweis('Keine Soll-Stunden in dieser Auswahl (hinterlegt für QLA, QLG und QLM ab 2025, nur vollständig erfasste Monate)'); return null; }
    const W = el.clientWidth || 600, H = window.LKhoehe ? window.LKhoehe(el, 240) : 240, m = { t: 10, r: 10, b: 26, l: 50 };
    const svg = d3.select(el).append('svg').attr('width', '100%').attr('height', H).attr('viewBox', `0 0 ${W} ${H}`).attr('role', 'img').attr('aria-label', aria);
    const x = d3.scaleBand().domain(rows.map((d) => d.name)).range([m.l, W - m.r]).padding(0.25);
    const y = d3.scaleLinear().domain([0, yMax(rows) || 1]).nice().range([H - m.b, m.t]);
    svg.append('g').attr('class', 'grid').attr('transform', `translate(${m.l},0)`).call(d3.axisLeft(y).ticks(5).tickSize(-(W - m.l - m.r)).tickFormat('')).call((g) => g.select('.domain').remove());
    svg.append('g').attr('transform', `translate(${m.l},0)`).call(d3.axisLeft(y).ticks(5).tickFormat(yFmt)).call((g) => g.select('.domain').remove());
    const step = Math.max(1, Math.ceil(rows.length / Math.max(1, Math.floor((W - m.l) / 52))));
    svg.append('g').attr('transform', `translate(0,${H - m.b})`).call(d3.axisBottom(x).tickValues(rows.map((d) => d.name).filter((_, i) => i % step === 0)).tickFormat(F.fMonth).tickSizeOuter(0));
    svg.append('line').attr('x1', m.l).attr('x2', W - m.r).attr('y1', y(100)).attr('y2', y(100)).attr('stroke-dasharray', '4 3').style('stroke', 'var(--cds-chart-reference)');
    const tip = document.createElement('div'); tip.className = 'tip'; tip.hidden = true; el.append(tip);
    const fang = (zeilen) => svg.append('g').selectAll('rect').data(rows).join('rect').attr('x', (d) => x(d.name) - x.step() * 0.125).attr('width', x.step()).attr('y', m.t).attr('height', H - m.t - m.b).style('fill', 'transparent')
      .on('pointermove', (ev, d) => {
        tip.replaceChildren(...[F.fMonth(d.name), ...zeilen(d)].map((l, j) => { const e = document.createElement('div'); if (j === 0) e.style.fontWeight = '600'; e.textContent = l; return e; }));
        tip.hidden = false;
        const b = el.getBoundingClientRect();
        let tx = ev.clientX - b.left + 12; const ty = ev.clientY - b.top + 12;
        if (tx + tip.offsetWidth > b.width) tx = Math.max(0, ev.clientX - b.left - tip.offsetWidth - 12);
        tip.style.left = tx + 'px'; tip.style.top = ty + 'px';
      })
      .on('pointerleave', () => { tip.hidden = true; });
    return { svg, rows, x, y, fang };
  };

  dash.draw('ch_iq', (el) => {
    const c = rahmen(el, 'Buchungsquote und Instandhaltungsquote je Monat in Prozent', (rows) => Math.max(100, d3.max(rows, (d) => Math.max(d.quote || 0, d.quote_pbi || 0))), (v) => v + ' %');
    if (!c) return;
    const mid = (d) => c.x(d.name) + c.x.bandwidth() / 2;
    ['quote', 'q_instandhaltung'].forEach((f, i) => {
      const pts = c.rows.filter((d) => d[f] != null);
      c.svg.append('path').datum(pts).attr('fill', 'none').attr('stroke-width', 2).style('stroke', dash.colors[i]).attr('d', d3.line().x(mid).y((d) => c.y(d[f])));
      c.svg.append('g').selectAll('circle').data(pts).join('circle').attr('cx', mid).attr('cy', (d) => c.y(d[f])).attr('r', 3).style('fill', dash.colors[i]);
    });
    c.fang((d) => ['Buchungsquote: ' + F.fPct(d.quote), 'Instandhaltungsquote: ' + F.fPct(d.q_instandhaltung), 'IST ' + std(d.ist) + ' / SOLL ' + std(d.soll)]);
  });

  // Gestapelt in Prozent der Soll-Stunden; Urlaub und Krankheit gedämpft obenauf
  const TEILE = [['laborauftrag', 'Laborauftrag'], ['we_fp', 'WE+FP'], ['wartung_kal', 'Wartung und Kalibrierung'], ['sonstiges', 'Sonstiges'], ['abwesend', 'Urlaub und Krankheit']];
  dash.draw('ch_iq_typ', (el) => {
    const wert = (d, k) => (k === 'wartung_kal' ? d.wartung + d.kalibrierung : k === 'abwesend' ? d.urlaub + d.krankheit : d[k]);
    const c = rahmen(el, 'Gebuchte Stunden je Monat nach Kontierungstyp in Prozent der Brutto-Stunden (Arbeitstage × FTE × 8), gestapelt', (rows) => Math.max(100, d3.max(rows, (d) => (d.brutto ? 100 * d.ist_mit_abwesenheit / d.brutto : 0))), (v) => v + ' %');
    if (!c) return;
    const g = c.svg.append('g').selectAll('g').data(c.rows.filter((d) => d.brutto)).join('g').attr('transform', (d) => `translate(${c.x(d.name)},0)`);
    TEILE.forEach(([k], i) => {
      g.append('rect').attr('width', c.x.bandwidth())
        .attr('y', (d) => c.y(100 * TEILE.slice(0, i + 1).reduce((t, [kk]) => t + wert(d, kk), 0) / d.brutto))
        .attr('height', (d) => c.y(0) - c.y(100 * wert(d, k) / d.brutto))
        .style('fill', k === 'abwesend' ? 'var(--cds-chart-muted)' : dash.colors[i]);
    });
    c.svg.append('line').attr('x1', c.x.range()[0]).attr('x2', c.x.range()[1]).attr('y1', c.y(100)).attr('y2', c.y(100)).attr('stroke-dasharray', '4 3').style('stroke', 'var(--cds-chart-reference)'); // 100 % über den Balken
    c.fang((d) => TEILE.map(([k, name]) => name + ': ' + std(wert(d, k)) + (d.brutto ? ' (' + F.fPct(Math.round(1000 * wert(d, k) / d.brutto) / 10) + ')' : '')).concat('Gebucht gesamt: ' + std(d.ist_mit_abwesenheit) + (d.brutto ? ' (' + F.fPct(Math.round(1000 * d.ist_mit_abwesenheit / d.brutto) / 10) + ')' : ''), 'Brutto-Stunden: ' + std(d.brutto)));
  });

  const table = (name, ebene, cols, rev) => dash.draw(name, (tb) => {
    tb.replaceChildren();
    let rows = daten(ebene);
    if (!rows) return;
    if (rev) rows = rows.slice().reverse();
    for (const r of rows) {
      const tr = document.createElement('tr');
      tr.setAttribute('data-key', encodeURIComponent(r.schluessel));
      for (const [f, fmt] of cols) { const td = document.createElement('td'); td.textContent = r[f] == null ? '—' : fmt(r[f]); tr.append(td); }
      tb.append(tr);
    }
  });
  table('tb_iq_labor', 'Labor', [['name', String], ['soll', std], ['ist', std], ['quote', F.fPct], ['q_laborauftrag', F.fPct], ['q_we_fp', F.fPct], ['q_wartung', F.fPct], ['q_kalibrierung', F.fPct], ['q_sonstiges', F.fPct], ['quote_pbi', F.fPct]]);
  table('tb_iq_monat', 'Monat', [['name', (v) => F.fMonth(v)], ['soll', std], ['ist', std], ['quote', F.fPct], ['laborauftrag', std], ['we_fp', std], ['wartung', std], ['kalibrierung', std], ['sonstiges', std], ['urlaub', std], ['krankheit', std]], true);
})();
