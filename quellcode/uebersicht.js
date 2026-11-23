// Reiter „Übersicht“: alle BSC-Kennzahlen des letzten abgeschlossenen Zeitraums mit SOLL und Veränderung zum Zeitraum davor.
(() => {
  const F = window.LKfmt;
  // [Feld in der BSC-Rechnung, SOLL-Feld, 'min' oder 'max', besser wenn: 'hoch' | 'tief' | 'nah:<Zielwert-Schlüssel>', Name]
  const K = [
    ['termintreue', 'soll_termintreue', 'min', 'hoch', 'Termintreue'],
    ['budgeteinhaltung', 'soll_budgeteinhaltung', 'min', 'hoch', 'Budgeteinhaltung'],
    ['qualitaetslevel', 'soll_qualitaetslevel', 'min', 'hoch', 'Qualitätslevel'],
    ['s', 'soll_reaktion_s', 'min', 'hoch', 'Reaktionszeit S'],
    ['m', 'soll_reaktion_m', 'min', 'hoch', 'Reaktionszeit M'],
    ['l', null, null, 'hoch', 'Reaktionszeit L'],
    ['puenktlich_m', 'soll_puenktlich_m', 'min', 'hoch', 'Pünktlichkeit M'],
    ['puenktlich_l', 'soll_puenktlich_l', 'min', 'hoch', 'Pünktlichkeit L'],
    ['plankosten', null, null, 'nah:ziel_plankosten', 'Plankostenerfüllung'],
    ['vergabequote', 'max_vergabe', 'max', 'tief', 'Vergabequote'],
    ['auftragsquote', null, null, 'hoch', 'Auftragsquote'],
    ['instandhaltungsquote', null, null, 'hoch', 'Instandhaltungsquote'],
    ['dienstleistungsquote', null, null, 'hoch', 'Dienstleistungsquote'],
    ['methodeneinsatz', null, null, 'nah:ziel_methodeneinsatz', 'Methodeneinsatz'],
    ['rueckweisung', 'max_rueckweisung', 'max', 'tief', 'Rückweisung'],
  ];
  const zName = (k) => (k.length === 4 ? k : k.includes('Q') ? k.slice(5) + ' ' + k.slice(0, 4) : F.fMonth(k));
  // Bezugszeitraum wie in der BSC: letzter abgeschlossener Zeitraum der Auswahl, sonst der laufende; dazu der Zeitraum davor
  const paar = () => {
    const s = dash.data('bsc');
    const r = s.status === 'ok' ? s.data || [] : [];
    if (!r.length) return [null, null];
    const fertig = r.filter((x) => !x.laufend), b = fertig.length ? fertig[fertig.length - 1] : r[r.length - 1], j = r.indexOf(b);
    return [b, j > 0 ? r[j - 1] : null];
  };
  const sollVon = (row, key) => {
    if (!row || !key) return null;
    if (key === 'max_vergabe') return row.soll_eigenleistung == null ? null : Math.round(10 * (100 - row.soll_eigenleistung)) / 10;
    return row[key] == null ? null : row[key];
  };
  const erreicht = (row, f, sk, art) => {
    const v = row ? row[f] : null, s = sollVon(row, sk);
    return v == null || s == null ? null : art === 'max' ? v <= s : v >= s;
  };

  for (const [f, sk, art, ri] of K) {
    dash.draw('ue_v_' + f, (el) => {
      const [b] = paar(), v = b ? b[f] : null, ok = erreicht(b, f, sk, art);
      el.textContent = v == null ? '—' : F.fPct(v);
      el.classList.toggle('good', ok === true); el.classList.toggle('bad', ok === false);
    });
    if (sk) dash.draw('ue_s_' + f, (el) => { const [b] = paar(), s = sollVon(b, sk); el.textContent = s == null ? '—' : F.fPct(s); });
    dash.draw('ue_d_' + f, (el) => {
      const [b, vor] = paar(), a = b ? b[f] : null, c = vor ? vor[f] : null;
      el.classList.remove('good', 'bad', 'neutral');
      if (a == null || c == null) { el.textContent = b ? 'kein Vergleich' : '—'; el.classList.add('neutral'); return; }
      const d = Math.round(10 * (a - c)) / 10;
      let besser;
      if (ri === 'hoch') besser = d > 0;
      else if (ri === 'tief') besser = d < 0;
      else { const z = window.LKsoll(ri.slice(4)); besser = Math.abs(a - z) < Math.abs(c - z); }
      el.textContent = (d > 0 ? '▲ +' : d < 0 ? '▼ −' : '± ') + F.fDec(Math.abs(d)) + ' Pp. ggü. ' + zName(vor.zeitraum);
      el.classList.add(d === 0 ? 'neutral' : besser ? 'good' : 'bad');
    });
  }
  for (const z of ['ziel_plankosten', 'ziel_auftragsquote', 'ziel_instandhaltungsquote', 'ziel_methodeneinsatz']) {
    dash.draw('ue_z_' + z, (el) => { const v = window.LKsoll(z); el.textContent = v == null ? '—' : F.fPct(v); });
  }

  dash.draw('ue_zeitraum', (el) => { const [b] = paar(); el.textContent = b ? zName(b.zeitraum) + (b.laufend ? ' (laufend)' : '') : '—'; });
  const bewertet = () => { const [b] = paar(); return K.filter(([, sk]) => sk).map(([f, sk, art, , name]) => [name, erreicht(b, f, sk, art)]).filter((x) => x[1] != null); };
  dash.draw('ue_ok', (el) => { el.textContent = paar()[0] ? F.fInt(bewertet().filter((x) => x[1]).length) : '—'; });
  dash.draw('ue_mit', (el) => { el.textContent = paar()[0] ? F.fInt(bewertet().length) : '—'; });
  dash.draw('ue_rot', (el) => {
    if (!paar()[0]) { el.textContent = '—'; return; }
    const rot = bewertet().filter((x) => !x[1]).map((x) => x[0]);
    el.textContent = rot.length ? rot.join(', ') : 'keine';
    el.classList.toggle('bad', rot.length > 0); el.classList.toggle('good', rot.length === 0);
  });
})();
