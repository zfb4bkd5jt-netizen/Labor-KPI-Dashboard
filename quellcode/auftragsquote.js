// Reiter „Auftragsquote (HoQ 2)“: Kennzahlen der Power-BI-Seite HoQ_2_Auftragsquote.

dash.calc('aq_verlauf', {
  inputs: ['auftraege', 'soll_auftraege'],
  title: 'Auftragsquote je Monat und Labor',
  description: 'Je Monat des technischen Abschlusses: abgeschlossene Aufträge je Labor (alle Prioritäten) im Verhältnis zu den Soll-Aufträgen aus den manuellen Daten. Im laufenden Monat ist das Soll anteilig bis zum Tag des Datenstands gerechnet.',
  fn: (auftraege, soll_auftraege) => {
    const p = dash.params();
    const jahr = p.jahr || '2026', qu = p.quartal || '', mon = p.monat || '', lab = p.labor || '';
    const ALLE = ['QLA', 'QLG', 'QLM'], LABS = ALLE.filter((l) => !lab || l === lab);
    let stand = '';
    for (const r of auftraege) { if (r.erstellt > stand) stand = r.erstellt; if (r.abschluss && r.abschluss > stand) stand = r.abschluss; }
    const inP = (mo) => (jahr === 'alle' || mo.slice(0, 4) === jahr) && (!mon || mo.slice(5) === mon) && (!qu || String(Math.ceil(Number(mo.slice(5)) / 3)) === qu);
    const map = new Map();
    for (const s of soll_auftraege) {
      if (!LABS.includes(s.labor) || s.monat > stand.slice(0, 7) || !inP(s.monat)) continue;
      let a = map.get(s.monat);
      if (!a) {
        a = { monat: s.monat, anteilig: s.monat === stand.slice(0, 7) };
        for (const l of ALLE) { a[l.toLowerCase() + '_abg'] = LABS.includes(l) ? 0 : null; a[l.toLowerCase() + '_soll'] = null; }
        map.set(s.monat, a);
      }
      let soll = s.soll;
      if (a.anteilig) { // laufender Monat: Soll nur für die Tage bis zum Datenstand
        const tage = new Date(Date.UTC(Number(s.monat.slice(0, 4)), Number(s.monat.slice(5)), 0)).getUTCDate();
        soll = Math.round(10 * s.soll * Number(stand.slice(8, 10)) / tage) / 10;
      }
      a[s.labor.toLowerCase() + '_soll'] = soll;
    }
    for (const r of auftraege) {
      if (!r.abschluss) continue;
      const a = map.get(r.abschluss.slice(0, 7));
      if (!a) continue;
      for (const l of (r.labore || '').split(';')) if (LABS.includes(l)) a[l.toLowerCase() + '_abg']++;
    }
    const q = (n, d) => (d ? Math.round(1000 * n / d) / 10 : null);
    return [...map.values()].sort((x, y) => (x.monat < y.monat ? -1 : 1)).map((a) => {
      let abg = 0, soll = 0;
      for (const l of LABS) { const k = l.toLowerCase(); a[k + '_quote'] = q(a[k + '_abg'], a[k + '_soll']); abg += a[k + '_abg']; soll += a[k + '_soll'] || 0; }
      for (const l of ALLE) if (!LABS.includes(l)) a[l.toLowerCase() + '_quote'] = null;
      return { ...a, abg, soll: Math.round(10 * soll) / 10, quote: q(abg, soll) };
    });
  },
});

dash.calc('aq_kpi', {
  inputs: ['aq_verlauf'],
  title: 'Auftragsquote im gewählten Zeitraum',
  description: 'Summen der Monatswerte: abgeschlossene Aufträge und Soll-Aufträge je Labor und gesamt, Quote = abgeschlossen / Soll. In der Gesamtzahl zählt ein Auftrag mit mehreren Laboren bei jedem beteiligten Labor.',
  fn: (aq_verlauf) => {
    const rows = aq_verlauf || [];
    const o = {};
    for (const k of ['qla', 'qlg', 'qlm', '']) {
      const pre = k ? k + '_' : '';
      const aktiv = rows.some((r) => r[pre + 'abg'] != null);
      const abg = rows.reduce((t, r) => t + (r[pre + 'abg'] || 0), 0), soll = Math.round(10 * rows.reduce((t, r) => t + (r[pre + 'soll'] || 0), 0)) / 10;
      o[pre + 'abg'] = aktiv ? abg : null; o[pre + 'soll'] = aktiv ? soll : null;
      o[pre + 'quote'] = aktiv && soll ? Math.round(1000 * abg / soll) / 10 : null;
    }
    return [o];
  },
});

(() => {
  const F = window.LKfmt;
  const LABS = [['qla', 'QLA'], ['qlg', 'QLG'], ['qlm', 'QLM']];
  const sollF = (v) => (Number.isInteger(v) ? F.fInt(v) : F.fDec(v));

  const K = () => { const k = dash.data('aq_kpi'); return k.status === 'ok' && k.data && k.data[0] ? k.data[0] : null; };
  const kachel = (name, field, fmt) => dash.draw(name, (el) => { const r = K(); el.textContent = r && r[field] != null ? fmt(r[field]) : '—'; });
  kachel('aq_q', 'quote', F.fPct); kachel('aq_n', 'abg', F.fInt); kachel('aq_d', 'soll', sollF);
  for (const [k] of LABS) { kachel('aq_' + k, k + '_quote', F.fPct); kachel('aq_' + k + '_n', k + '_abg', F.fInt); kachel('aq_' + k + '_d', k + '_soll', sollF); }
  dash.draw('leg2', (el) => { el.style.background = dash.colors[2]; });

  // Linien je Labor über die Monate
  dash.draw('ch_aq', (el) => {
    const s = dash.data('aq_verlauf');
    el.replaceChildren();
    const hinweis = (t) => { const d = document.createElement('div'); d.className = 'fail'; d.textContent = t; el.append(d); };
    if (s.status !== 'ok') { if (s.status === 'error' || s.status === 'missing') hinweis('Daten konnten nicht geladen werden'); return; }
    const rows = s.data || [];
    if (!rows.length) { hinweis('Für diese Auswahl gibt es keine Soll-Vorgabe (Soll-Aufträge sind nur für QLA, QLG und QLM hinterlegt)'); return; }
    const W = el.clientWidth || 600, H = window.LKhoehe ? window.LKhoehe(el, 260) : 260, m = { t: 10, r: 10, b: 26, l: 50 };
    const svg = d3.select(el).append('svg').attr('width', '100%').attr('height', H).attr('viewBox', `0 0 ${W} ${H}`).attr('role', 'img').attr('aria-label', 'Auftragsquote je Monat für QLA, QLG und QLM in Prozent');
    const x = d3.scalePoint().domain(rows.map((d) => d.monat)).range([m.l, W - m.r]).padding(0.3);
    const vals = rows.flatMap((d) => LABS.map(([k]) => d[k + '_quote'])).filter((v) => v != null);
    const y = d3.scaleLinear().domain([0, Math.max(100, d3.max(vals) || 0)]).nice().range([H - m.b, m.t]);
    svg.append('g').attr('class', 'grid').attr('transform', `translate(${m.l},0)`).call(d3.axisLeft(y).ticks(5).tickSize(-(W - m.l - m.r)).tickFormat('')).call((g) => g.select('.domain').remove());
    svg.append('g').attr('transform', `translate(${m.l},0)`).call(d3.axisLeft(y).ticks(5).tickFormat((v) => v + ' %')).call((g) => g.select('.domain').remove());
    const step = Math.max(1, Math.ceil(rows.length / Math.max(1, Math.floor((W - m.l) / 52))));
    svg.append('g').attr('transform', `translate(0,${H - m.b})`).call(d3.axisBottom(x).tickValues(rows.map((d) => d.monat).filter((_, i) => i % step === 0)).tickFormat(F.fMonth).tickSizeOuter(0));
    svg.append('line').attr('x1', m.l).attr('x2', W - m.r).attr('y1', y(100)).attr('y2', y(100)).attr('stroke-dasharray', '4 3').style('stroke', 'var(--cds-chart-reference)');
    LABS.forEach(([k], i) => {
      const pts = rows.filter((d) => d[k + '_quote'] != null);
      svg.append('path').datum(pts).attr('fill', 'none').attr('stroke-width', 2).style('stroke', dash.colors[i]).attr('d', d3.line().x((d) => x(d.monat)).y((d) => y(d[k + '_quote'])));
      svg.append('g').selectAll('circle').data(pts).join('circle').attr('cx', (d) => x(d.monat)).attr('cy', (d) => y(d[k + '_quote'])).attr('r', 3).style('fill', dash.colors[i]);
    });
    const tip = document.createElement('div'); tip.className = 'tip'; tip.hidden = true; el.append(tip);
    const bw = rows.length > 1 ? x.step() : W - m.l - m.r;
    svg.append('g').selectAll('rect').data(rows).join('rect').attr('x', (d) => x(d.monat) - bw / 2).attr('width', bw).attr('y', m.t).attr('height', H - m.t - m.b).style('fill', 'transparent')
      .on('pointermove', (ev, d) => {
        const lines = [F.fMonth(d.monat) + (d.anteilig ? ' (laufend, Soll anteilig)' : '')];
        for (const [k, name] of LABS) if (d[k + '_quote'] != null) lines.push(name + ': ' + F.fPct(d[k + '_quote']) + ' (' + F.fInt(d[k + '_abg']) + ' von ' + sollF(d[k + '_soll']) + ')');
        tip.replaceChildren(...lines.map((l, j) => { const e = document.createElement('div'); if (j === 0) e.style.fontWeight = '600'; e.textContent = l; return e; }));
        tip.hidden = false;
        const b = el.getBoundingClientRect();
        let tx = ev.clientX - b.left + 12; const ty = ev.clientY - b.top + 12;
        if (tx + tip.offsetWidth > b.width) tx = Math.max(0, ev.clientX - b.left - tip.offsetWidth - 12);
        tip.style.left = tx + 'px'; tip.style.top = ty + 'px';
      })
      .on('pointerleave', () => { tip.hidden = true; });
  });

  // Tabelle: neuester Monat oben
  dash.draw('tb_aq', (tb) => {
    const s = dash.data('aq_verlauf');
    tb.replaceChildren();
    if (s.status !== 'ok') return;
    const cols = [['monat', (v) => F.fMonth(v)]];
    for (const [k] of LABS) cols.push([k + '_abg', F.fInt], [k + '_soll', sollF], [k + '_quote', F.fPct]);
    cols.push(['abg', F.fInt], ['soll', sollF], ['quote', F.fPct]);
    for (const r of (s.data || []).slice().reverse()) {
      const tr = document.createElement('tr');
      tr.setAttribute('data-key', encodeURIComponent(r.monat));
      for (const [f, fmt] of cols) { const td = document.createElement('td'); td.textContent = r[f] == null ? '—' : fmt(r[f]) + (f === 'monat' && r.anteilig ? ' (laufend)' : ''); tr.append(td); }
      tb.append(tr);
    }
  });
})();
