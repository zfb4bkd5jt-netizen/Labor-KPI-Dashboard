// Reiter „WE – Same-Day“: Kennzahlen der Power-BI-Seite WE (Wareneingangsprüfung, Abschluss am Anlagetag).

dash.calc('we_gruppen', {
  inputs: ['we_sameday'],
  title: 'Same-Day-Quote nach Zeitraum, Monat, Anlagestunde und Wochentag',
  description: 'Babtec-Aufträge nach Anlagedatum im gewählten Zeitraum: gewertete Abschlüsse, davon am Anlagetag und innerhalb von 24 Stunden technisch abgeschlossen. Eine Zeile gesamt, eine je Prüfungsart, und für die Wareneingangsprüfung je Monat, Anlagestunde und Wochentag. Quote = am Anlagetag abgeschlossen / gewertete Abschlüsse.',
  fn: (we_sameday) => {
    const p = dash.params();
    const jahr = p.jahr || '2026', qu = p.quartal || '', mon = p.monat || '';
    const inP = (mo) => (jahr === 'alle' || mo.slice(0, 4) === jahr) && (!mon || mo.slice(5) === mon) && (!qu || String(Math.ceil(Number(mo.slice(5)) / 3)) === qu);
    const TAGE = ['Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag', 'Samstag', 'Sonntag'];
    const ARTEN = { WE: 'Wareneingangsprüfung', FP: 'Fertigungsprüfung' };
    const fenster = (h) => (h >= 6 && h <= 17 ? String(h).padStart(2, '0') + ':00–' + String(h).padStart(2, '0') + ':59' : 'außerhalb 06–18 Uhr');
    const gruppen = new Map();
    const add = (ebene, name, sort, r) => {
      const k = ebene + ' ' + name;
      let a = gruppen.get(k);
      if (!a) { a = { schluessel: k, ebene, name, sort, auftraege: 0, abgeschlossen: 0, same_day: 0, in24: 0, sammel: 0 }; gruppen.set(k, a); }
      for (const f of ['auftraege', 'abgeschlossen', 'same_day', 'in24', 'sammel']) a[f] += r[f];
    };
    for (const r of we_sameday) {
      if (!inP(r.monat)) continue;
      if (ARTEN[r.art]) add('Art', ARTEN[r.art], r.art === 'WE' ? 0 : 1, r);
      if (r.art !== 'WE') continue;
      add('Zeitraum', 'gesamt', 0, r); add('Monat', r.monat, r.monat, r);
      add('Stunde', fenster(r.stunde), r.stunde >= 6 && r.stunde <= 17 ? r.stunde : 99, r); add('Wochentag', TAGE[r.wt], r.wt, r);
    }
    const rang = { Zeitraum: 0, Art: 1, Monat: 2, Stunde: 3, Wochentag: 4 };
    const q = (n, d) => (d ? Math.round(1000 * n / d) / 10 : null);
    return [...gruppen.values()]
      .sort((x, y) => rang[x.ebene] - rang[y.ebene] || (x.sort < y.sort ? -1 : x.sort > y.sort ? 1 : 0))
      .map((a) => ({ schluessel: a.schluessel, ebene: a.ebene, name: a.name, auftraege: a.auftraege, abgeschlossen: a.abgeschlossen, same_day: a.same_day, in24: a.in24, sammel: a.sammel,
        quote: q(a.same_day, a.abgeschlossen), quote24: q(a.in24, a.abgeschlossen) }));
  },
});

dash.calc('we_matrix', {
  inputs: ['we_sameday'],
  title: 'Same-Day-Quote nach Anlagestunde und Wochentag',
  description: 'Wareneingangsprüfung im gewählten Zeitraum: Same-Day-Quote in Prozent je Anlagestunde (Zeilen) und Wochentag Montag bis Freitag (Spalten), dazu die Zahl der gewerteten Abschlüsse je Zelle.',
  fn: (we_sameday) => {
    const p = dash.params();
    const jahr = p.jahr || '2026', qu = p.quartal || '', mon = p.monat || '';
    const inP = (mo) => (jahr === 'alle' || mo.slice(0, 4) === jahr) && (!mon || mo.slice(5) === mon) && (!qu || String(Math.ceil(Number(mo.slice(5)) / 3)) === qu);
    const T = ['mo', 'di', 'mi', 'do', 'fr'];
    const map = new Map();
    for (const r of we_sameday) {
      if (r.art !== 'WE' || !inP(r.monat) || r.wt > 4 || r.stunde < 6 || r.stunde > 17) continue;
      let a = map.get(r.stunde);
      if (!a) { a = { stunde: r.stunde, n: {}, s: {} }; map.set(r.stunde, a); }
      a.n[T[r.wt]] = (a.n[T[r.wt]] || 0) + r.abgeschlossen; a.s[T[r.wt]] = (a.s[T[r.wt]] || 0) + r.same_day;
    }
    return [...map.values()].sort((x, y) => x.stunde - y.stunde).map((a) => {
      const h = String(a.stunde).padStart(2, '0');
      const o = { fenster: h + ':00–' + h + ':59' };
      for (const t of T) { o[t] = a.n[t] ? Math.round(1000 * (a.s[t] || 0) / a.n[t]) / 10 : null; o[t + '_n'] = a.n[t] || 0; }
      return o;
    });
  },
});

(() => {
  const F = window.LKfmt;
  const daten = (ebene) => { const s = dash.data('we_gruppen'); return s.status === 'ok' ? (s.data || []).filter((r) => r.ebene === ebene) : null; };

  [['we_q', 'quote', F.fPct], ['we_sd', 'same_day', F.fInt], ['we_abg', 'abgeschlossen', F.fInt], ['we_q24', 'quote24', F.fPct], ['we_24', 'in24', F.fInt],
   ['we_auf', 'auftraege', F.fInt], ['we_sam', 'sammel', F.fInt]]
    .forEach(([name, field, fmt]) => dash.draw(name, (el) => { const d = daten('Zeitraum'); const r = d && d[0]; el.textContent = r && r[field] != null ? fmt(r[field]) : '—'; }));

  // Balken = am Anlagetag, Punkte mit Linie = innerhalb 24 Stunden
  const diagramm = (name, ebene, aria, label, kurz) => dash.draw(name, (el) => {
    const s = dash.data('we_gruppen');
    el.replaceChildren();
    const hinweis = (t) => { const d = document.createElement('div'); d.className = 'fail'; d.textContent = t; el.append(d); };
    if (s.status !== 'ok') { if (s.status === 'error' || s.status === 'missing') hinweis('Daten konnten nicht geladen werden'); return; }
    const rows = (s.data || []).filter((r) => r.ebene === ebene && r.abgeschlossen > 0);
    if (!rows.length) { hinweis('Keine gewerteten Abschlüsse in dieser Auswahl'); return; }
    const W = el.clientWidth || 600, H = window.LKhoehe ? window.LKhoehe(el, 240) : 240, m = { t: 10, r: 10, b: 26, l: 46 };
    const svg = d3.select(el).append('svg').attr('width', '100%').attr('height', H).attr('viewBox', `0 0 ${W} ${H}`).attr('role', 'img').attr('aria-label', aria);
    const x = d3.scaleBand().domain(rows.map((d) => d.name)).range([m.l, W - m.r]).padding(0.25);
    const y = d3.scaleLinear().domain([0, 100]).range([H - m.b, m.t]);
    svg.append('g').attr('class', 'grid').attr('transform', `translate(${m.l},0)`).call(d3.axisLeft(y).ticks(5).tickSize(-(W - m.l - m.r)).tickFormat('')).call((g) => g.select('.domain').remove());
    svg.append('g').attr('transform', `translate(${m.l},0)`).call(d3.axisLeft(y).ticks(5).tickFormat((v) => v + ' %')).call((g) => g.select('.domain').remove());
    const step = Math.max(1, Math.ceil(rows.length / Math.max(1, Math.floor((W - m.l) / 52))));
    svg.append('g').attr('transform', `translate(0,${H - m.b})`).call(d3.axisBottom(x).tickValues(rows.map((d) => d.name).filter((_, i) => i % step === 0)).tickFormat(kurz).tickSizeOuter(0));
    svg.append('g').selectAll('rect').data(rows).join('rect').attr('x', (d) => x(d.name)).attr('width', x.bandwidth()).attr('y', (d) => y(d.quote)).attr('height', (d) => y(0) - y(d.quote)).attr('rx', 1.5).style('fill', dash.colors[0]);
    const mid = (d) => x(d.name) + x.bandwidth() / 2;
    svg.append('path').datum(rows).attr('fill', 'none').attr('stroke-width', 2).style('stroke', dash.colors[1]).attr('d', d3.line().x(mid).y((d) => y(d.quote24)));
    svg.append('g').selectAll('circle').data(rows).join('circle').attr('cx', mid).attr('cy', (d) => y(d.quote24)).attr('r', 3).style('fill', dash.colors[1]);
    const tip = document.createElement('div'); tip.className = 'tip'; tip.hidden = true; el.append(tip);
    svg.append('g').selectAll('rect').data(rows).join('rect').attr('x', (d) => x(d.name) - (x.step() - x.bandwidth()) / 2).attr('width', x.step()).attr('y', m.t).attr('height', H - m.t - m.b).style('fill', 'transparent')
      .on('pointermove', (ev, d) => {
        const lines = [label(d.name), 'Am Anlagetag: ' + F.fPct(d.quote) + ' (' + F.fInt(d.same_day) + ' von ' + F.fInt(d.abgeschlossen) + ')', 'Innerhalb 24 h: ' + F.fPct(d.quote24) + ' (' + F.fInt(d.in24) + ')'];
        tip.replaceChildren(...lines.map((l, j) => { const e = document.createElement('div'); if (j === 0) e.style.fontWeight = '600'; e.textContent = l; return e; }));
        tip.hidden = false;
        const b = el.getBoundingClientRect();
        let tx = ev.clientX - b.left + 12; const ty = ev.clientY - b.top + 12;
        if (tx + tip.offsetWidth > b.width) tx = Math.max(0, ev.clientX - b.left - tip.offsetWidth - 12);
        tip.style.left = tx + 'px'; tip.style.top = ty + 'px';
      })
      .on('pointerleave', () => { tip.hidden = true; });
  });
  diagramm('ch_we_stunde', 'Stunde', 'Same-Day-Quote und Quote innerhalb 24 Stunden der Wareneingangsprüfung je Anlagestunde', (n) => 'Angelegt ' + n, (n) => (n.startsWith('auß') ? 'sonst' : n.slice(0, 2) + ' h'));
  diagramm('ch_we_monat', 'Monat', 'Same-Day-Quote und Quote innerhalb 24 Stunden der Wareneingangsprüfung je Anlagemonat', (n) => F.fMonth(n), (n) => F.fMonth(n));

  // Matrix Stunde × Wochentag, Zellen nach Quote eingefärbt
  dash.draw('tb_we_matrix', (tb) => {
    const s = dash.data('we_matrix');
    tb.replaceChildren();
    if (s.status !== 'ok') return;
    for (const r of s.data || []) {
      const tr = document.createElement('tr');
      tr.setAttribute('data-key', encodeURIComponent(r.fenster));
      const th = document.createElement('td'); th.textContent = r.fenster; tr.append(th);
      for (const t of ['mo', 'di', 'mi', 'do', 'fr']) {
        const td = document.createElement('td');
        td.textContent = r[t] == null ? '—' : F.fPct(r[t]);
        if (r[t] != null) td.style.background = 'color-mix(in srgb, var(--color-ok) ' + Math.round(r[t] * 0.45) + '%, transparent)';
        if (r[t + '_n'] < 10) td.style.color = 'var(--color-fg-muted)';
        tr.append(td);
      }
      tb.append(tr);
    }
  });

  const table = (name, ebene, cols) => dash.draw(name, (tb) => {
    tb.replaceChildren();
    const rows = daten(ebene);
    if (!rows) return;
    for (const r of rows) {
      const tr = document.createElement('tr');
      tr.setAttribute('data-key', encodeURIComponent(r.schluessel));
      for (const [f, fmt] of cols) { const td = document.createElement('td'); td.textContent = r[f] == null ? '—' : fmt(r[f]); tr.append(td); }
      tb.append(tr);
    }
  });
  const spalten = [['name', String], ['auftraege', F.fInt], ['abgeschlossen', F.fInt], ['same_day', F.fInt], ['quote', F.fPct], ['quote24', F.fPct]];
  table('tb_we_art', 'Art', spalten);
  table('tb_we_tag', 'Wochentag', spalten);
})();
