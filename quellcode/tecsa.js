// Reiter „TecSa“: Kennzahlen der Power-BI-Seite TecSa (Technische Sauberkeit, Standardprüfungen).

dash.calc('ts_woche', {
  inputs: ['tecsa'],
  title: 'Filter je Kalenderwoche',
  description: 'Je ISO-Kalenderwoche des gewählten Zeitraums: Anzahl ausgewerteter Filter (laufende Nummern), getrennt nach Fertigungsprüfung (FP), Wareneingang (WE) und ohne Angabe, dazu die Zahl der Tage mit Filtern.',
  fn: (tecsa) => {
    const p = dash.params();
    const jahr = p.jahr || '2026', qu = p.quartal || '', mon = p.monat || '';
    const inP = (d) => (jahr === 'alle' || d.slice(0, 4) === jahr) && (!mon || d.slice(5, 7) === mon) && (!qu || String(Math.ceil(Number(d.slice(5, 7)) / 3)) === qu);
    const isoKW = (s) => {
      const d = new Date(s + 'T00:00:00Z');
      d.setUTCDate(d.getUTCDate() - ((d.getUTCDay() + 6) % 7) + 3); // Donnerstag der Woche
      const y = d.getUTCFullYear();
      return y + '-KW' + String(1 + Math.floor((d - Date.UTC(y, 0, 1)) / 6048e5)).padStart(2, '0');
    };
    const map = new Map();
    for (const r of tecsa) {
      if (!inP(r.datum)) continue;
      const kw = isoKW(r.datum);
      let a = map.get(kw);
      if (!a) { a = { kw, fp: 0, we: 0, ohne: 0, filter: 0, blindwert: 0, t: new Set() }; map.set(kw, a); }
      a[r.art === 'FP' ? 'fp' : r.art === 'WE' ? 'we' : 'ohne'] += r.filter; a.filter += r.filter; a.t.add(r.datum);
      if (r.blindwert) a.blindwert += r.filter;
    }
    return [...map.values()].sort((x, y) => (x.kw < y.kw ? -1 : 1)).map((a) => ({ kw: a.kw, fp: a.fp, we: a.we, ohne: a.ohne, filter: a.filter, blindwert: a.blindwert, tage: a.t.size }));
  },
});

dash.calc('ts_gruppen', {
  inputs: ['tecsa'],
  title: 'Filter nach Zeitraum, Produkt, Wochentag und Auswertung',
  description: 'Anzahl Filter des gewählten Zeitraums: eine Zeile gesamt, eine je Produkt, je Wochentag und je Auswertungsart, jeweils mit FP und WE, dem Anteil an allen Filtern und dem Durchschnitt je Tag mit Filtern.',
  fn: (tecsa) => {
    const p = dash.params();
    const jahr = p.jahr || '2026', qu = p.quartal || '', mon = p.monat || '';
    const inP = (d) => (jahr === 'alle' || d.slice(0, 4) === jahr) && (!mon || d.slice(5, 7) === mon) && (!qu || String(Math.ceil(Number(d.slice(5, 7)) / 3)) === qu);
    const TAGE = ['Sonntag', 'Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag', 'Samstag'];
    const rows = tecsa.filter((r) => inP(r.datum));
    const gesamt = rows.reduce((t, r) => t + r.filter, 0);
    const gruppen = new Map();
    const add = (ebene, name, sort, r) => {
      const k = ebene + ' ' + name;
      let a = gruppen.get(k);
      if (!a) { a = { schluessel: k, ebene, name, sort, filter: 0, fp: 0, we: 0, ohne: 0, blindwert: 0, t: new Set() }; gruppen.set(k, a); }
      a.filter += r.filter; a[r.art === 'FP' ? 'fp' : r.art === 'WE' ? 'we' : 'ohne'] += r.filter; a.t.add(r.datum);
      if (r.blindwert) a.blindwert += r.filter;
    };
    for (const r of rows) {
      const wt = new Date(r.datum + 'T00:00:00Z').getUTCDay();
      add('Zeitraum', 'gesamt', 0, r); add('Produkt', r.produkt, 0, r); add('Wochentag', TAGE[wt], (wt + 6) % 7, r); add('Auswertung', r.auswertung, 0, r);
    }
    const rang = { Zeitraum: 0, Produkt: 1, Wochentag: 2, Auswertung: 3 };
    return [...gruppen.values()]
      .sort((x, y) => rang[x.ebene] - rang[y.ebene] || (x.ebene === 'Wochentag' ? x.sort - y.sort : y.filter - x.filter))
      .map((a) => ({ schluessel: a.schluessel, ebene: a.ebene, name: a.name, filter: a.filter, fp: a.fp, we: a.we, ohne: a.ohne, blindwert: a.blindwert, tage: a.t.size,
        anteil: gesamt ? Math.round(1000 * a.filter / gesamt) / 10 : null,
        fp_anteil: a.filter ? Math.round(1000 * a.fp / a.filter) / 10 : null, we_anteil: a.filter ? Math.round(1000 * a.we / a.filter) / 10 : null,
        je_tag: a.t.size ? Math.round(10 * a.filter / a.t.size) / 10 : null }));
  },
});

(() => {
  const F = window.LKfmt;
  const daten = (ebene) => { const s = dash.data('ts_gruppen'); return s.status === 'ok' ? (s.data || []).filter((r) => r.ebene === ebene) : null; };

  [['ts_n', 'filter', F.fInt], ['ts_tage', 'tage', F.fInt], ['ts_jt', 'je_tag', F.fDec], ['ts_fp', 'fp', F.fInt], ['ts_fpa', 'fp_anteil', F.fPct],
   ['ts_we', 'we', F.fInt], ['ts_wea', 'we_anteil', F.fPct], ['ts_bw', 'blindwert', F.fInt]]
    .forEach(([name, field, fmt]) => dash.draw(name, (el) => { const d = daten('Zeitraum'); const r = d && d[0]; el.textContent = r && r[field] != null ? fmt(r[field]) : '—'; }));

  const TEILE = [['fp', 'Fertigungsprüfung (FP)'], ['we', 'Wareneingang (WE)'], ['ohne', 'ohne Angabe']];
  dash.draw('ch_ts', (el) => {
    const s = dash.data('ts_woche');
    el.replaceChildren();
    const hinweis = (t) => { const d = document.createElement('div'); d.className = 'fail'; d.textContent = t; el.append(d); };
    if (s.status !== 'ok') { if (s.status === 'error' || s.status === 'missing') hinweis('Daten konnten nicht geladen werden'); return; }
    const rows = s.data || [];
    if (!rows.length) { hinweis('Keine Filter in dieser Auswahl (die Daten beginnen im März 2024)'); return; }
    const multi = new Set(rows.map((d) => d.kw.slice(0, 4))).size > 1;
    const label = (k) => (multi ? k.slice(7) + '/' + k.slice(2, 4) : 'KW ' + k.slice(7));
    const W = el.clientWidth || 600, H = window.LKhoehe ? window.LKhoehe(el, 260) : 260, m = { t: 10, r: 10, b: 26, l: 40 };
    const svg = d3.select(el).append('svg').attr('width', '100%').attr('height', H).attr('viewBox', `0 0 ${W} ${H}`).attr('role', 'img').attr('aria-label', 'Anzahl Filter je Kalenderwoche, gestapelt nach Fertigungsprüfung und Wareneingang');
    const x = d3.scaleBand().domain(rows.map((d) => d.kw)).range([m.l, W - m.r]).padding(rows.length > 60 ? 0.1 : 0.25);
    const y = d3.scaleLinear().domain([0, d3.max(rows, (d) => d.filter) || 1]).nice().range([H - m.b, m.t]);
    svg.append('g').attr('class', 'grid').attr('transform', `translate(${m.l},0)`).call(d3.axisLeft(y).ticks(5).tickSize(-(W - m.l - m.r)).tickFormat('')).call((g) => g.select('.domain').remove());
    svg.append('g').attr('transform', `translate(${m.l},0)`).call(d3.axisLeft(y).ticks(5).tickFormat(F.fInt)).call((g) => g.select('.domain').remove());
    const step = Math.max(1, Math.ceil(rows.length / Math.max(1, Math.floor((W - m.l) / 58))));
    svg.append('g').attr('transform', `translate(0,${H - m.b})`).call(d3.axisBottom(x).tickValues(rows.map((d) => d.kw).filter((_, i) => i % step === 0)).tickFormat(label).tickSizeOuter(0));
    const g = svg.append('g').selectAll('g').data(rows).join('g').attr('transform', (d) => `translate(${x(d.kw)},0)`);
    TEILE.forEach(([k], i) => {
      g.append('rect').attr('width', x.bandwidth())
        .attr('y', (d) => y(TEILE.slice(0, i + 1).reduce((t, [kk]) => t + d[kk], 0)))
        .attr('height', (d) => y(0) - y(d[k]))
        .style('fill', k === 'ohne' ? 'var(--cds-chart-muted)' : dash.colors[i]);
    });
    const tip = document.createElement('div'); tip.className = 'tip'; tip.hidden = true; el.append(tip);
    svg.append('g').selectAll('rect').data(rows).join('rect').attr('x', (d) => x(d.kw) - (x.step() - x.bandwidth()) / 2).attr('width', x.step()).attr('y', m.t).attr('height', H - m.t - m.b).style('fill', 'transparent')
      .on('pointermove', (ev, d) => {
        const lines = ['KW ' + d.kw.slice(7) + ' / ' + d.kw.slice(0, 4), 'Filter: ' + F.fInt(d.filter), ...TEILE.filter(([k]) => d[k]).map(([k, name]) => name + ': ' + F.fInt(d[k])), 'an ' + F.fInt(d.tage) + ' Tagen'];
        tip.replaceChildren(...lines.map((l, j) => { const e = document.createElement('div'); if (j === 0) e.style.fontWeight = '600'; e.textContent = l; return e; }));
        tip.hidden = false;
        const b = el.getBoundingClientRect();
        let tx = ev.clientX - b.left + 12; const ty = ev.clientY - b.top + 12;
        if (tx + tip.offsetWidth > b.width) tx = Math.max(0, ev.clientX - b.left - tip.offsetWidth - 12);
        tip.style.left = tx + 'px'; tip.style.top = ty + 'px';
      })
      .on('pointerleave', () => { tip.hidden = true; });
  });

  const table = (name, ebene, cols, max) => dash.draw(name, (tb) => {
    tb.replaceChildren();
    const rows = daten(ebene);
    if (!rows) return;
    for (const r of rows.slice(0, max)) {
      const tr = document.createElement('tr');
      tr.setAttribute('data-key', encodeURIComponent(r.schluessel));
      for (const [f, fmt] of cols) { const td = document.createElement('td'); td.textContent = r[f] == null ? '—' : fmt(r[f]); tr.append(td); }
      tb.append(tr);
    }
  });
  table('tb_ts_produkt', 'Produkt', [['name', String], ['filter', F.fInt], ['anteil', F.fPct], ['fp', F.fInt], ['we', F.fInt]], 20);
  table('tb_ts_tag', 'Wochentag', [['name', String], ['filter', F.fInt], ['tage', F.fInt], ['je_tag', F.fDec]]);
  table('tb_ts_ausw', 'Auswertung', [['name', String], ['filter', F.fInt], ['anteil', F.fPct]]);
})();
