// Reiter „Wartung und Kalibrierung“: Kennzahlen der Power-BI-Seiten Wartung und Kalibrierung.

dash.calc('wk_monat', {
  inputs: ['wk_abgeschlossen'],
  title: 'Abgeschlossene Wartungen und Kalibrierungen je Monat',
  description: 'Je Monat des Ist-Endtermins: abgeschlossene Wartungsaufträge (ZLB3) und Kalibrieraufträge (ZLB4, intern, extern, ohne Angabe) und der Anteil, der bis zum Eckendtermin fertig war.',
  fn: (wk_abgeschlossen) => {
    const p = dash.params();
    const jahr = p.jahr || '2026', qu = p.quartal || '', mon = p.monat || '';
    const inP = (mo) => (jahr === 'alle' || mo.slice(0, 4) === jahr) && (!mon || mo.slice(5) === mon) && (!qu || String(Math.ceil(Number(mo.slice(5)) / 3)) === qu);
    const map = new Map();
    for (const r of wk_abgeschlossen) {
      if (!inP(r.monat)) continue;
      let a = map.get(r.monat);
      if (!a) { a = { monat: r.monat, wartung: 0, w_puenktlich_n: 0, kal_intern: 0, kal_extern: 0, kal_ohne: 0, kalibrierung: 0, k_puenktlich_n: 0 }; map.set(r.monat, a); }
      if (r.art === 'Wartung') { a.wartung += r.anzahl; a.w_puenktlich_n += r.puenktlich; }
      else { a.kalibrierung += r.anzahl; a.k_puenktlich_n += r.puenktlich; a[r.ie === 'intern' ? 'kal_intern' : r.ie === 'extern' ? 'kal_extern' : 'kal_ohne'] += r.anzahl; }
    }
    const q = (n, d) => (d ? Math.round(1000 * n / d) / 10 : null);
    return [...map.values()].sort((x, y) => (x.monat < y.monat ? -1 : 1)).map((a) => ({ ...a, w_puenktlich: q(a.w_puenktlich_n, a.wartung), k_puenktlich: q(a.k_puenktlich_n, a.kalibrierung) }));
  },
});

dash.calc('wk_kpi', {
  inputs: ['wk_monat', 'wk_offen'],
  title: 'Wartung und Kalibrierung im gewählten Zeitraum',
  description: 'Summen der Monatswerte, dazu der offene Bestand zum Datenstand: Aufträge ohne Ist-Endtermin, deren Eckendtermin überschritten ist, getrennt nach freigegeben und nicht freigegeben.',
  fn: (wk_monat, wk_offen) => {
    const rows = wk_monat || [];
    const s = (f) => rows.reduce((t, r) => t + r[f], 0);
    const q = (n, d) => (d ? Math.round(1000 * n / d) / 10 : null);
    const o = { wartung: s('wartung'), w_puenktlich_n: s('w_puenktlich_n'), kalibrierung: s('kalibrierung'), k_puenktlich_n: s('k_puenktlich_n'), kal_intern: s('kal_intern'), kal_extern: s('kal_extern'), kal_ohne: s('kal_ohne') };
    o.w_puenktlich = q(o.w_puenktlich_n, o.wartung); o.k_puenktlich = q(o.k_puenktlich_n, o.kalibrierung); o.extern_anteil = q(o.kal_extern, o.kalibrierung);
    o.ueber_frei = wk_offen.filter((r) => r.freigegeben).length;
    o.ueber_frei_wartung = wk_offen.filter((r) => r.freigegeben && r.art === 'Wartung').length;
    o.ueber_frei_kalibrierung = wk_offen.filter((r) => r.freigegeben && r.art === 'Kalibrierung').length;
    o.ueber_nicht_frei = wk_offen.filter((r) => !r.freigegeben).length;
    return [o];
  },
});

dash.calc('wk_bezeichnung', {
  inputs: ['wk_abgeschlossen'],
  title: 'Abgeschlossene Aufträge nach Bezeichnung',
  description: 'Abgeschlossene Wartungs- und Kalibrieraufträge des gewählten Zeitraums je Equipment-Bezeichnung, bei Kalibrierung getrennt nach intern und extern, mit dem Anteil pünktlich abgeschlossener Aufträge.',
  fn: (wk_abgeschlossen) => {
    const p = dash.params();
    const jahr = p.jahr || '2026', qu = p.quartal || '', mon = p.monat || '';
    const inP = (mo) => (jahr === 'alle' || mo.slice(0, 4) === jahr) && (!mon || mo.slice(5) === mon) && (!qu || String(Math.ceil(Number(mo.slice(5)) / 3)) === qu);
    const map = new Map();
    for (const r of wk_abgeschlossen) {
      if (!inP(r.monat)) continue;
      const k = r.art + ' ' + r.bezeichnung;
      let a = map.get(k);
      if (!a) { a = { schluessel: k, art: r.art, bezeichnung: r.bezeichnung, anzahl: 0, intern: 0, extern: 0, ohne: 0, puenktlich_n: 0 }; map.set(k, a); }
      a.anzahl += r.anzahl; a.puenktlich_n += r.puenktlich;
      if (r.art === 'Kalibrierung') a[r.ie === 'intern' ? 'intern' : r.ie === 'extern' ? 'extern' : 'ohne'] += r.anzahl;
    }
    return [...map.values()].sort((x, y) => (x.art === y.art ? y.anzahl - x.anzahl : x.art < y.art ? -1 : 1)).map((a) => ({ ...a, puenktlich: Math.round(1000 * a.puenktlich_n / a.anzahl) / 10 }));
  },
});

dash.calc('wk_ueberfaellig', {
  inputs: ['wk_offen'],
  title: 'Freigegebene, überfällige Aufträge',
  description: 'Freigegebene Wartungs- und Kalibrieraufträge ohne Ist-Endtermin, deren Eckendtermin zum Datenstand überschritten ist, die am längsten überfälligen zuerst.',
  fn: (wk_offen) => wk_offen.filter((r) => r.freigegeben).sort((a, b) => b.tage_ueber - a.tage_ueber),
});

(() => {
  const F = window.LKfmt;
  const text = (v) => String(v);

  const K = () => { const k = dash.data('wk_kpi'); return k.status === 'ok' && k.data && k.data[0] ? k.data[0] : null; };
  [['wk_w', 'wartung', F.fInt], ['wk_wp', 'w_puenktlich', F.fPct], ['wk_k', 'kalibrierung', F.fInt], ['wk_kp', 'k_puenktlich', F.fPct],
   ['wk_ki', 'kal_intern', F.fInt], ['wk_ke', 'kal_extern', F.fInt], ['wk_ea', 'extern_anteil', F.fPct],
   ['wk_uf', 'ueber_frei', F.fInt], ['wk_ufw', 'ueber_frei_wartung', F.fInt], ['wk_ufk', 'ueber_frei_kalibrierung', F.fInt], ['wk_unf', 'ueber_nicht_frei', F.fInt]]
    .forEach(([name, field, fmt]) => dash.draw(name, (el) => { const r = K(); el.textContent = r && r[field] != null ? fmt(r[field]) : '—'; }));

  const rahmen = (el, aria, yMax, yFmt) => {
    const s = dash.data('wk_monat');
    el.replaceChildren();
    const hinweis = (t) => { const d = document.createElement('div'); d.className = 'fail'; d.textContent = t; el.append(d); };
    if (s.status !== 'ok') { if (s.status === 'error' || s.status === 'missing') hinweis('Daten konnten nicht geladen werden'); return null; }
    const rows = s.data || [];
    if (!rows.length) { hinweis('Keine abgeschlossenen Aufträge in dieser Auswahl'); return null; }
    const W = el.clientWidth || 600, H = window.LKhoehe ? window.LKhoehe(el, 240) : 240, m = { t: 10, r: 10, b: 26, l: 46 };
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

  const TEILE = [['wartung', 'Wartung'], ['kal_intern', 'Kalibrierung intern'], ['kal_extern', 'Kalibrierung extern'], ['kal_ohne', 'Kalibrierung ohne Angabe']];
  dash.draw('ch_wk', (el) => {
    const c = rahmen(el, 'Abgeschlossene Wartungen und Kalibrierungen je Monat, gestapelt', (rows) => d3.max(rows, (d) => d.wartung + d.kalibrierung), F.fInt);
    if (!c) return;
    const g = c.svg.append('g').selectAll('g').data(c.rows).join('g').attr('transform', (d) => `translate(${c.x(d.monat)},0)`);
    TEILE.forEach(([k], i) => {
      g.append('rect').attr('width', c.x.bandwidth())
        .attr('y', (d) => c.y(TEILE.slice(0, i + 1).reduce((t, [kk]) => t + d[kk], 0)))
        .attr('height', (d) => c.y(0) - c.y(d[k]))
        .style('fill', k === 'kal_ohne' ? 'var(--cds-chart-muted)' : dash.colors[i]);
    });
    c.fang((d) => TEILE.map(([k, name]) => name + ': ' + F.fInt(d[k])));
  });

  dash.draw('ch_wk_tt', (el) => {
    const c = rahmen(el, 'Anteil pünktlich abgeschlossener Wartungen und Kalibrierungen je Monat in Prozent', () => 100, (v) => v + ' %');
    if (!c) return;
    const mid = (d) => c.x(d.monat) + c.x.bandwidth() / 2;
    ['w_puenktlich', 'k_puenktlich'].forEach((f, i) => {
      const pts = c.rows.filter((d) => d[f] != null);
      c.svg.append('path').datum(pts).attr('fill', 'none').attr('stroke-width', 2).style('stroke', dash.colors[i]).attr('d', d3.line().x(mid).y((d) => c.y(d[f])));
      c.svg.append('g').selectAll('circle').data(pts).join('circle').attr('cx', mid).attr('cy', (d) => c.y(d[f])).attr('r', 3).style('fill', dash.colors[i]);
    });
    c.fang((d) => ['Wartung: ' + (d.wartung ? F.fPct(d.w_puenktlich) + ' (' + F.fInt(d.w_puenktlich_n) + ' von ' + F.fInt(d.wartung) + ')' : '—'),
      'Kalibrierung: ' + (d.kalibrierung ? F.fPct(d.k_puenktlich) + ' (' + F.fInt(d.k_puenktlich_n) + ' von ' + F.fInt(d.kalibrierung) + ')' : '—')]);
  });

  const table = (name, id, key, cols, pick, max) => dash.draw(name, (tb) => {
    const s = dash.data(id);
    tb.replaceChildren();
    if (s.status !== 'ok') return;
    for (const r of (s.data || []).filter(pick || (() => true)).slice(0, max)) {
      const tr = document.createElement('tr');
      tr.setAttribute('data-key', encodeURIComponent(String(r[key])));
      for (const [f, fmt, cls] of cols) { const td = document.createElement('td'); if (cls) td.className = cls; td.textContent = r[f] == null ? '—' : fmt(r[f]); tr.append(td); }
      tb.append(tr);
    }
  });
  table('tb_wk_kal', 'wk_bezeichnung', 'schluessel', [['bezeichnung', text], ['anzahl', F.fInt], ['intern', F.fInt], ['extern', F.fInt], ['puenktlich', F.fPct]], (r) => r.art === 'Kalibrierung', 15);
  table('tb_wk_wartung', 'wk_bezeichnung', 'schluessel', [['bezeichnung', text], ['anzahl', F.fInt], ['puenktlich', F.fPct]], (r) => r.art === 'Wartung', 15);
  table('tb_wk_ueber', 'wk_ueberfaellig', 'auftrag', [['auftrag', text], ['art', text, 'l'], ['bezeichnung', text, 'l'], ['kurztext', text, 'l wrap'], ['eckende', F.fDate], ['tage_ueber', F.fInt]], null, 25);
})();
