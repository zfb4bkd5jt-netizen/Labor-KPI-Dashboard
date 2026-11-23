// Reiter „Vergabequote (HoQ 2)“: Kennzahlen der Power-BI-Seite HoQ_2_Vergabequote.

dash.calc('vq_monat', {
  inputs: ['sap_kosten', 'bsc_vorgaben'],
  title: 'Vergabequote je Buchungsmonat',
  description: 'Je Buchungsmonat: interne Leistung (Sachkonto 94311000) und externe Leistung (Sachkonten 65001000, 63012000, 65602000, 65200000) aus den SAP-Instandhaltungskosten, Vergabequote = extern / (intern + extern), dazu die im gewählten Zeitraum aufgelaufenen Werte.',
  fn: (sap_kosten, bsc_vorgaben) => {
    const p = dash.params();
    const jahr = p.jahr || '2026', qu = p.quartal || '', mon = p.monat || '';
    const konten = (k, d) => { const r = (bsc_vorgaben || []).find((x) => x.schluessel === k); const l = r && r.text ? String(r.text).split(/[;,\s]+/).filter(Boolean) : []; return l.length ? l : d; };   // Sachkonten aus dem Blatt BSC_Vorgaben
    const EXTERN = konten('sachkonten_extern', ['65001000', '63012000', '65602000', '65200000']), INTERN = konten('sachkonten_intern', ['94311000']);
    const AB = '2025-01'; // der Export enthält Aufträge mit Beginn ab 2025; frühere Buchungsmonate sind unvollständig
    const inP = (mo) => mo >= AB && (jahr === 'alle' || mo.slice(0, 4) === jahr) && (!mon || mo.slice(5) === mon) && (!qu || String(Math.ceil(Number(mo.slice(5)) / 3)) === qu);
    const map = new Map();
    for (const r of sap_kosten) {
      if (!inP(r.monat)) continue;
      let a = map.get(r.monat);
      if (!a) { a = { monat: r.monat, intern: 0, extern: 0, sonstige: 0 }; map.set(r.monat, a); }
      a[EXTERN.some((k) => r.sachkonto.includes(k)) ? 'extern' : INTERN.some((k) => r.sachkonto.includes(k)) ? 'intern' : 'sonstige'] += r.kosten;
    }
    const q = (e, i) => (e + i ? Math.round(1000 * e / (e + i)) / 10 : null);
    let ik = 0, ek = 0;
    return [...map.values()].sort((x, y) => (x.monat < y.monat ? -1 : 1)).map((a) => {
      ik += a.intern; ek += a.extern;
      return { monat: a.monat, intern: Math.round(a.intern), extern: Math.round(a.extern), sonstige: Math.round(a.sonstige), gesamt: Math.round(a.intern + a.extern),
        quote: q(a.extern, a.intern), intern_kum: Math.round(ik), extern_kum: Math.round(ek), quote_kum: q(ek, ik) };
    });
  },
});

dash.calc('vq_kpi', {
  inputs: ['vq_monat'],
  title: 'Vergabequote im gewählten Zeitraum',
  description: 'Summen der Monatswerte: interne und externe Leistung, Gesamtleistung, Vergabequote und der Betrag auf Sachkonten, die weder intern noch extern zugeordnet sind.',
  fn: (vq_monat) => {
    const rows = vq_monat || [];
    const s = (f) => rows.reduce((t, r) => t + r[f], 0);
    const intern = s('intern'), extern = s('extern');
    return [{ intern, extern, gesamt: intern + extern, sonstige: s('sonstige'), quote: intern + extern ? Math.round(1000 * extern / (intern + extern)) / 10 : null }];
  },
});

dash.calc('vq_gruppen', {
  inputs: ['sap_kosten', 'bsc_vorgaben'],
  title: 'Leistung nach Auftragsart und Sachkonto',
  description: 'Kosten des gewählten Zeitraums je Instandhaltungsauftragsart (intern, extern, Vergabequote) und je Sachkonto mit seiner Zuordnung.',
  fn: (sap_kosten, bsc_vorgaben) => {
    const p = dash.params();
    const jahr = p.jahr || '2026', qu = p.quartal || '', mon = p.monat || '';
    const konten = (k, d) => { const r = (bsc_vorgaben || []).find((x) => x.schluessel === k); const l = r && r.text ? String(r.text).split(/[;,\s]+/).filter(Boolean) : []; return l.length ? l : d; };   // Sachkonten aus dem Blatt BSC_Vorgaben
    const EXTERN = konten('sachkonten_extern', ['65001000', '63012000', '65602000', '65200000']), INTERN = konten('sachkonten_intern', ['94311000']);
    const AB = '2025-01';
    const inP = (mo) => mo >= AB && (jahr === 'alle' || mo.slice(0, 4) === jahr) && (!mon || mo.slice(5) === mon) && (!qu || String(Math.ceil(Number(mo.slice(5)) / 3)) === qu);
    const typ = (k) => (EXTERN.some((x) => k.includes(x)) ? 'extern' : INTERN.some((x) => k.includes(x)) ? 'intern' : 'nicht gewertet');
    const art = new Map(), konto = new Map();
    for (const r of sap_kosten) {
      if (!inP(r.monat)) continue;
      const t = typ(r.sachkonto);
      let a = art.get(r.auftragsart);
      if (!a) { a = { intern: 0, extern: 0 }; art.set(r.auftragsart, a); }
      if (t !== 'nicht gewertet') a[t] += r.kosten;
      let k = konto.get(r.sachkonto);
      if (!k) { k = { zuordnung: t, kosten: 0, positionen: 0 }; konto.set(r.sachkonto, k); }
      k.kosten += r.kosten; k.positionen += r.positionen;
    }
    return [
      ...[...art].sort((x, y) => (x[0] < y[0] ? -1 : 1)).map(([name, a]) => ({ schluessel: 'Auftragsart ' + name, ebene: 'Auftragsart', name, zuordnung: null,
        intern: Math.round(a.intern), extern: Math.round(a.extern), kosten: Math.round(a.intern + a.extern), positionen: null,
        quote: a.intern + a.extern ? Math.round(1000 * a.extern / (a.intern + a.extern)) / 10 : null })),
      ...[...konto].sort((x, y) => y[1].kosten - x[1].kosten).map(([name, k]) => ({ schluessel: 'Sachkonto ' + name, ebene: 'Sachkonto', name, zuordnung: k.zuordnung,
        intern: null, extern: null, kosten: Math.round(k.kosten), positionen: k.positionen, quote: null })),
    ];
  },
});

(() => {
  const F = window.LKfmt;
  const text = (v) => String(v);

  const K = () => { const k = dash.data('vq_kpi'); return k.status === 'ok' && k.data && k.data[0] ? k.data[0] : null; };
  [['vq_q', 'quote', F.fPct], ['vq_ext', 'extern', F.fEur], ['vq_int', 'intern', F.fEur], ['vq_ges', 'gesamt', F.fEur], ['vq_son', 'sonstige', F.fEur]]
    .forEach(([name, field, fmt]) => dash.draw(name, (el) => { const r = K(); el.textContent = r && r[field] != null ? fmt(r[field]) : '—'; }));

  // Gemeinsamer Rahmen für beide Monatsdiagramme
  const rahmen = (el, aria, yMax, yFmt) => {
    const s = dash.data('vq_monat');
    el.replaceChildren();
    const hinweis = (t) => { const d = document.createElement('div'); d.className = 'fail'; d.textContent = t; el.append(d); };
    if (s.status !== 'ok') { if (s.status === 'error' || s.status === 'missing') hinweis('Daten konnten nicht geladen werden'); return null; }
    const rows = s.data || [];
    if (!rows.length) { hinweis('Keine SAP-Kosten in dieser Auswahl (der Export beginnt 2025)'); return null; }
    const W = el.clientWidth || 600, H = window.LKhoehe ? window.LKhoehe(el, 240) : 240, m = { t: 10, r: 10, b: 26, l: 62 };
    const svg = d3.select(el).append('svg').attr('width', '100%').attr('height', H).attr('viewBox', `0 0 ${W} ${H}`).attr('role', 'img').attr('aria-label', aria);
    const x = d3.scaleBand().domain(rows.map((d) => d.monat)).range([m.l, W - m.r]).padding(0.25);
    const y = d3.scaleLinear().domain([0, yMax(rows) || 1]).nice().range([H - m.b, m.t]);
    svg.append('g').attr('class', 'grid').attr('transform', `translate(${m.l},0)`).call(d3.axisLeft(y).ticks(5).tickSize(-(W - m.l - m.r)).tickFormat('')).call((g) => g.select('.domain').remove());
    svg.append('g').attr('transform', `translate(${m.l},0)`).call(d3.axisLeft(y).ticks(5).tickFormat(yFmt)).call((g) => g.select('.domain').remove());
    const step = Math.max(1, Math.ceil(rows.length / Math.max(1, Math.floor((W - m.l) / 52))));
    svg.append('g').attr('transform', `translate(0,${H - m.b})`).call(d3.axisBottom(x).tickValues(rows.map((d) => d.monat).filter((_, i) => i % step === 0)).tickFormat(F.fMonth).tickSizeOuter(0));
    const tip = document.createElement('div'); tip.className = 'tip'; tip.hidden = true; el.append(tip);
    const fang = (zeilen) => svg.append('g').selectAll('rect').data(rows).join('rect').attr('x', (d) => x(d.monat) - x.step() * 0.125).attr('width', x.step()).attr('y', m.t).attr('height', H - m.t - m.b).style('fill', 'transparent')
      .on('pointermove', (ev, d) => {
        tip.replaceChildren(...[F.fMonth(d.monat), ...zeilen(d)].map((l, j) => { const e = document.createElement('div'); if (j === 0) e.style.fontWeight = '600'; e.textContent = l; return e; }));
        tip.hidden = false;
        const b = el.getBoundingClientRect();
        let tx = ev.clientX - b.left + 12; const ty = ev.clientY - b.top + 12;
        if (tx + tip.offsetWidth > b.width) tx = Math.max(0, ev.clientX - b.left - tip.offsetWidth - 12);
        tip.style.left = tx + 'px'; tip.style.top = ty + 'px';
      })
      .on('pointerleave', () => { tip.hidden = true; });
    return { svg, rows, x, y, fang };
  };

  dash.draw('ch_vq', (el) => {
    const c = rahmen(el, 'Vergabequote je Buchungsmonat und aufgelaufen im gewählten Zeitraum, in Prozent', (rows) => d3.max(rows, (d) => Math.max(d.quote || 0, d.quote_kum || 0)), (v) => v + ' %');
    if (!c) return;
    const mid = (d) => c.x(d.monat) + c.x.bandwidth() / 2;
    ['quote', 'quote_kum'].forEach((f, i) => {
      const pts = c.rows.filter((d) => d[f] != null);
      c.svg.append('path').datum(pts).attr('fill', 'none').attr('stroke-width', 2).style('stroke', dash.colors[i]).attr('d', d3.line().x(mid).y((d) => c.y(d[f])));
      c.svg.append('g').selectAll('circle').data(pts).join('circle').attr('cx', mid).attr('cy', (d) => c.y(d[f])).attr('r', 3).style('fill', dash.colors[i]);
    });
    c.fang((d) => ['Vergabequote: ' + F.fPct(d.quote), 'Aufgelaufen: ' + F.fPct(d.quote_kum), 'Extern ' + F.fEur(d.extern) + ' / intern ' + F.fEur(d.intern)]);
  });

  dash.draw('ch_vq_eur', (el) => {
    const c = rahmen(el, 'Interne und externe Leistung je Buchungsmonat in Euro, gestapelt', (rows) => d3.max(rows, (d) => d.intern + d.extern), (v) => F.fInt(v / 1000) + ' T€');
    if (!c) return;
    const g = c.svg.append('g').selectAll('g').data(c.rows).join('g').attr('transform', (d) => `translate(${c.x(d.monat)},0)`);
    g.append('rect').attr('width', c.x.bandwidth()).attr('y', (d) => c.y(Math.max(0, d.intern))).attr('height', (d) => c.y(0) - c.y(Math.max(0, d.intern))).style('fill', dash.colors[0]);
    g.append('rect').attr('width', c.x.bandwidth()).attr('y', (d) => c.y(Math.max(0, d.intern) + Math.max(0, d.extern))).attr('height', (d) => c.y(0) - c.y(Math.max(0, d.extern))).style('fill', dash.colors[1]);
    c.fang((d) => ['Intern: ' + F.fEur(d.intern), 'Extern: ' + F.fEur(d.extern), 'Gesamt: ' + F.fEur(d.gesamt)]);
  });

  const table = (name, id, key, cols, pick, rev) => dash.draw(name, (tb) => {
    const s = dash.data(id);
    tb.replaceChildren();
    if (s.status !== 'ok') return;
    let rows = (s.data || []).filter(pick || (() => true));
    if (rev) rows = rows.slice().reverse();
    for (const r of rows) {
      const tr = document.createElement('tr');
      tr.setAttribute('data-key', encodeURIComponent(String(r[key])));
      for (const [f, fmt, cls] of cols) { const td = document.createElement('td'); if (cls) td.className = cls; td.textContent = r[f] == null ? '—' : fmt(r[f]); tr.append(td); }
      tb.append(tr);
    }
  });
  table('tb_vq_monat', 'vq_monat', 'monat', [['monat', (v) => F.fMonth(v)], ['intern', F.fEur], ['extern', F.fEur], ['gesamt', F.fEur], ['quote', F.fPct], ['quote_kum', F.fPct]], null, true);
  table('tb_vq_art', 'vq_gruppen', 'schluessel', [['name', text], ['intern', F.fEur], ['extern', F.fEur], ['kosten', F.fEur], ['quote', F.fPct]], (r) => r.ebene === 'Auftragsart');
  table('tb_vq_konto', 'vq_gruppen', 'schluessel', [['name', text], ['zuordnung', text, 'l'], ['positionen', F.fInt], ['kosten', F.fEur]], (r) => r.ebene === 'Sachkonto');
})();
