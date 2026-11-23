// Reiter „Plankostenerfüllung (HoQ 2)“: Kennzahlen der Power-BI-Seite HoQ_2_Plankostenerfüllung.

dash.calc('pk_auftraege', {
  inputs: ['auftraege', 'stunden_auftrag', 'bsc_vorgaben'],
  title: 'Plankostenerfüllung je Auftrag',
  description: 'Abgeschlossene M- und L-Aufträge der Auswahl (nach Abschlussdatum) mit Planwert und gebuchten Stunden: IST-Kosten = gebuchte Stunden × 75 €, PLAN-Kosten = Auftragswert, Quote = IST / PLAN.',
  fn: (auftraege, stunden_auftrag, bsc_vorgaben) => {
    const p = dash.params();
    const jahr = p.jahr || '2026', qu = p.quartal || '', mon = p.monat || '', lab = p.labor || '', prio = p.prio || '';
    const vs = (bsc_vorgaben || []).find((x) => x.schluessel === 'stundensatz');
    const SATZ = vs && vs.wert > 0 ? vs.wert : 75; // € je gebuchter Stunde, aus dem Blatt BSC_Vorgaben
    const std = new Map();
    for (const s of stunden_auftrag) std.set(s.auftrag, (std.get(s.auftrag) || 0) + s.stunden);
    const inP = (d) => (jahr === 'alle' || d.slice(0, 4) === jahr) && (!mon || d.slice(5, 7) === mon) && (!qu || String(Math.ceil(Number(d.slice(5, 7)) / 3)) === qu);
    return auftraege
      .filter((r) => r.abschluss && (r.prio === 'M' || r.prio === 'L') && inP(r.abschluss) && r.wert > 0 && std.has(r.auftrag)   // Kosten werden nur für M und L geplant
        && (!lab || (r.labore || '').split(';').includes(lab)) && (!prio || r.prio === prio))
      .map((r) => {
        const h = Math.round(100 * std.get(r.auftrag)) / 100, ist = Math.round(100 * h * SATZ) / 100;
        return { auftrag: r.auftrag, bezeichnung: r.bezeichnung, labore: (r.labore || '').replace(/;/g, ', '), prio: r.prio, abschluss: r.abschluss,
          plan: r.wert, stunden: h, ist, abweichung: Math.round(100 * (ist - r.wert)) / 100, quote: Math.round(1000 * ist / r.wert) / 10 };
      })
      .sort((a, b) => b.abweichung - a.abweichung);
  },
});

dash.calc('pk_kpi', {
  inputs: ['pk_auftraege', 'auftraege', 'stunden_auftrag'],
  title: 'Plankostenerfüllung im gewählten Zeitraum',
  description: 'Summen über die gewerteten Aufträge: Gesamtquote (Summe IST / Summe PLAN), Mittelwert und Median der Auftragsquoten, Anteil der Aufträge bis 100 %, dazu die Zahl der abgeschlossenen Aufträge ohne Planwert oder ohne gebuchte Stunden.',
  fn: (pk_auftraege, auftraege, stunden_auftrag) => {
    const p = dash.params();
    const jahr = p.jahr || '2026', qu = p.quartal || '', mon = p.monat || '', lab = p.labor || '', prio = p.prio || '';
    const inP = (d) => (jahr === 'alle' || d.slice(0, 4) === jahr) && (!mon || d.slice(5, 7) === mon) && (!qu || String(Math.ceil(Number(d.slice(5, 7)) / 3)) === qu);
    const gebucht = new Set(stunden_auftrag.map((s) => s.auftrag));
    const abg = auftraege.filter((r) => r.abschluss && (r.prio === 'M' || r.prio === 'L') && inP(r.abschluss) && (!lab || (r.labore || '').split(';').includes(lab)) && (!prio || r.prio === prio));
    const rows = pk_auftraege || [];
    const plan = rows.reduce((t, r) => t + r.plan, 0), ist = rows.reduce((t, r) => t + r.ist, 0);
    const q = rows.map((r) => r.quote).sort((a, b) => a - b), m = q.length >> 1;
    const imPlan = rows.filter((r) => r.quote <= 100).length;
    return [{
      n: rows.length, plan: Math.round(plan), ist: Math.round(ist), abweichung: Math.round(ist - plan),
      quote_gesamt: plan ? Math.round(1000 * ist / plan) / 10 : null,
      quote_mittel: q.length ? Math.round(10 * q.reduce((t, v) => t + v, 0) / q.length) / 10 : null,
      quote_median: q.length ? Math.round(10 * (q.length % 2 ? q[m] : (q[m - 1] + q[m]) / 2)) / 10 : null,
      n_im_plan: imPlan, anteil_im_plan: rows.length ? Math.round(1000 * imPlan / rows.length) / 10 : null,
      n_abgeschlossen: abg.length,
      n_ohne_plan: abg.filter((r) => !(r.wert > 0)).length,
      n_ohne_stunden: abg.filter((r) => r.wert > 0 && !gebucht.has(r.auftrag)).length,
    }];
  },
});

dash.calc('pk_woche', {
  inputs: ['pk_auftraege'],
  title: 'Plankostenerfüllung je Kalenderwoche',
  description: 'Je ISO-Kalenderwoche des technischen Abschlusses: Gesamtquote (Summe IST / Summe PLAN) und Mittelwert der Auftragsquoten.',
  fn: (pk_auftraege) => {
    const isoKW = (s) => {
      const d = new Date(s.slice(0, 10) + 'T00:00:00Z');
      d.setUTCDate(d.getUTCDate() - ((d.getUTCDay() + 6) % 7) + 3); // Donnerstag der Woche
      const y = d.getUTCFullYear();
      return y + '-KW' + String(1 + Math.floor((d - Date.UTC(y, 0, 1)) / 6048e5)).padStart(2, '0');
    };
    const map = new Map();
    for (const r of pk_auftraege || []) {
      const kw = isoKW(r.abschluss);
      let a = map.get(kw);
      if (!a) { a = { kw, n: 0, plan: 0, ist: 0, sq: 0 }; map.set(kw, a); }
      a.n++; a.plan += r.plan; a.ist += r.ist; a.sq += r.quote;
    }
    return [...map.values()].sort((x, y) => (x.kw < y.kw ? -1 : 1)).map((a) => ({
      kw: a.kw, n: a.n, plan: Math.round(a.plan), ist: Math.round(a.ist),
      quote_gesamt: Math.round(1000 * a.ist / a.plan) / 10, quote_mittel: Math.round(10 * a.sq / a.n) / 10,
    }));
  },
});

dash.calc('pk_gruppen', {
  inputs: ['pk_auftraege'],
  title: 'Plankostenerfüllung nach Priorität und Labor',
  description: 'Gewertete Aufträge je Priorität und je Labor: PLAN, IST, Gesamtquote, Mittelwert der Auftragsquoten und Anteil bis 100 %. Ein Auftrag mit mehreren Laboren zählt bei jedem.',
  fn: (pk_auftraege) => {
    const rows = pk_auftraege || [];
    const zeile = (art, gruppe, g) => {
      const plan = g.reduce((t, r) => t + r.plan, 0), ist = g.reduce((t, r) => t + r.ist, 0);
      return { schluessel: art + ' ' + gruppe, art, gruppe, n: g.length, plan: Math.round(plan), ist: Math.round(ist), abweichung: Math.round(ist - plan),
        quote_gesamt: plan ? Math.round(1000 * ist / plan) / 10 : null,
        quote_mittel: g.length ? Math.round(10 * g.reduce((t, r) => t + r.quote, 0) / g.length) / 10 : null,
        anteil_im_plan: g.length ? Math.round(1000 * g.filter((r) => r.quote <= 100).length / g.length) / 10 : null };
    };
    const namen = { S: 'S (48 h)', M: 'M (14 d)', L: 'L (70 d)', '0': '0 (ohne Reaktionszeit)' };
    return [
      ...['M', 'L'].map((k) => zeile('Priorität', namen[k], rows.filter((r) => r.prio === k))),
      ...['QLA', 'QLC', 'QLG', 'QLM'].map((l) => zeile('Labor', l, rows.filter((r) => r.labore.split(', ').includes(l)))),
    ];
  },
});

dash.calc('pk_top', {
  inputs: ['pk_auftraege'],
  title: 'Größte Abweichungen vom Plan',
  description: 'Die 20 gewerteten Aufträge mit der größten Abweichung zwischen IST- und PLAN-Kosten in Euro, nach oben wie nach unten.',
  fn: (pk_auftraege) => (pk_auftraege || []).slice().sort((a, b) => Math.abs(b.abweichung) - Math.abs(a.abweichung)).slice(0, 20),
});

(() => {
  const F = window.LKfmt;
  const eurS = (v) => (v > 0 ? '+' : v < 0 ? '−' : '') + F.fEur(Math.abs(v));
  const stdF = (v) => F.fDec(v) + ' h';
  const text = (v) => String(v);

  const K = () => { const k = dash.data('pk_kpi'); return k.status === 'ok' && k.data && k.data[0] ? k.data[0] : null; };
  [['pk_q', 'quote_gesamt', F.fPct], ['pk_ist', 'ist', F.fEur], ['pk_plan', 'plan', F.fEur],
   ['pk_abw', 'abweichung', eurS], ['pk_imp', 'anteil_im_plan', F.fPct], ['pk_imp_n', 'n_im_plan', F.fInt], ['pk_imp_d', 'n', F.fInt],
   ['pk_qm', 'quote_mittel', F.fPct], ['pk_med', 'quote_median', F.fPct],
   ['pk_n', 'n', F.fInt], ['pk_oh', 'n_ohne_stunden', F.fInt], ['pk_op', 'n_ohne_plan', F.fInt],
  ].forEach(([name, field, fmt]) => dash.draw(name, (el) => {
    const r = K();
    el.textContent = r && r[field] != null ? fmt(r[field]) : '—';
    if (name === 'pk_abw') { el.classList.remove('good', 'bad'); if (r && r.abweichung) el.classList.add(r.abweichung > 0 ? 'bad' : 'good'); }
  }));

  window.LKline('ch_pk', 'pk_woche', [{ field: 'quote_gesamt' }, { field: 'quote_mittel' }], {
    pct: false, prozent: true, ref: 100,
    aria: 'Plankostenerfüllung je Kalenderwoche: Gesamtquote und Mittelwert der Auftragsquoten in Prozent',
    tip: (r) => ['Gesamtquote: ' + F.fPct(r.quote_gesamt), 'Ø Auftragsquoten: ' + F.fPct(r.quote_mittel), 'IST ' + F.fEur(r.ist) + ' / PLAN ' + F.fEur(r.plan), F.fInt(r.n) + ' Aufträge'],
  });

  const table = (name, id, key, cols, pick) => dash.draw(name, (tb) => {
    const s = dash.data(id);
    tb.replaceChildren();
    if (s.status !== 'ok') return;
    for (const r of (s.data || []).filter(pick || (() => true))) {
      const tr = document.createElement('tr');
      tr.setAttribute('data-key', encodeURIComponent(String(r[key])));
      for (const [f, fmt, cls] of cols) { const td = document.createElement('td'); if (cls) td.className = cls; td.textContent = r[f] == null ? '—' : fmt(r[f]); tr.append(td); }
      tb.append(tr);
    }
  });
  const gruppenSpalten = [['gruppe', text], ['n', F.fInt], ['plan', F.fEur], ['ist', F.fEur], ['abweichung', eurS], ['quote_gesamt', F.fPct], ['quote_mittel', F.fPct], ['anteil_im_plan', F.fPct]];
  table('tb_pk_prio', 'pk_gruppen', 'schluessel', gruppenSpalten, (r) => r.art === 'Priorität');
  table('tb_pk_labor', 'pk_gruppen', 'schluessel', gruppenSpalten, (r) => r.art === 'Labor');
  table('tb_pk_top', 'pk_top', 'auftrag', [['auftrag', text], ['bezeichnung', text, 'l wrap'], ['labore', text, 'l'], ['prio', text, 'l'], ['abschluss', F.fDate], ['stunden', stdF], ['plan', F.fEur], ['ist', F.fEur], ['abweichung', eurS], ['quote', F.fPct]]);
})();
