// Reiter „Termintreue“: Liste der Aufträge, die eine Vorgabe verfehlt haben (Klick auf eine Kachel wählt die Liste).
dash.calc('tt_liste', {
  inputs: ['auftraege', 'pruefgruppen', 'bsc_vorgaben'],
  title: 'Aufträge außerhalb der Vorgabe',
  description: 'Im gewählten Zeitraum abgeschlossene Aufträge, die die gewählte Vorgabe verfehlt haben: S = Babtec-Aufträge, deren schnellste Prüfgruppe mehr als 48 Stunden brauchte (ohne Sammelabschluss); M/L Frist = Abschluss mehr als 14 bzw. 70 Tage nach Bearbeitungsbeginn oder ohne Bearbeitungsbeginn; M/L Termin = Abschluss nach dem zugesagten Termin. Größte Abweichung zuerst.',
  fn: (auftraege, pruefgruppen, bsc_vorgaben) => {
    const p = dash.params();
    const jahr = p.jahr || '2026', qu = p.quartal || '', mon = p.monat || '', lab = p.labor || '', art = p.tt_liste || 'm_frist';
    const inP = (d) => d && (jahr === 'alle' || d.slice(0, 4) === jahr) && (!mon || d.slice(5, 7) === mon) && (!qu || String(Math.ceil(Number(d.slice(5, 7)) / 3)) === qu);
    const F = (v) => String(Math.round(10 * v) / 10).replace('.', ',');
    const datum = (s) => s.slice(8, 10) + '.' + s.slice(5, 7) + '.' + s.slice(0, 4);
    if (art === 's') {
      const tx = (k, d) => { const r = (bsc_vorgaben || []).find((x) => x.schluessel === k); return r && r.text ? String(r.text).slice(0, 10) : d; };
      const von = tx('sammel_von', '2026-04-04'), bis = tx('sammel_bis', '2026-04-06');
      const g = new Map();
      for (const r of pruefgruppen) {
        const tag = r.abschluss.slice(0, 10);
        if (!inP(tag) || (tag >= von && tag <= bis)) continue;
        const a = g.get(r.auftrag);
        if (!a || r.dauer_h < a.dauer_h) g.set(r.auftrag, r);          // schnellste Prüfgruppe des Auftrags
      }
      return [...g.values()].filter((r) => r.dauer_h > 48).sort((x, y) => y.dauer_h - x.dauer_h)
        .map((r) => ({ auftrag: r.auftrag, text: r.art === 'WE' ? 'Wareneingangsprüfung' : r.art === 'FP' ? 'Fertigungsprüfung' : 'Prüfgruppe',
          labore: '', abschluss: r.abschluss.slice(0, 10), vorgabe: '≤ 48 h ab Anlage', ist: F(r.dauer_h) + ' h', ueber: r.dauer_h - 48 }));
    }
    const prio = art.startsWith('m') ? 'M' : 'L', frist = prio === 'M' ? 14 : 70;
    const rows = auftraege.filter((r) => r.prio === prio && inP(r.abschluss) && (!lab || (r.labore || '').split(';').includes(lab)));
    const out = [];
    for (const r of rows) {
      const basis = { auftrag: r.auftrag, text: r.bezeichnung || '', labore: (r.labore || '').replace(/;/g, ', '), abschluss: r.abschluss };
      if (art.endsWith('frist')) {
        if (r.tage_ab_beginn == null) out.push({ ...basis, vorgabe: '≤ ' + frist + ' Tage ab Bearbeitungsbeginn', ist: 'ohne Bearbeitungsbeginn', ueber: 0 });
        else if (r.tage_ab_beginn > frist) out.push({ ...basis, vorgabe: '≤ ' + frist + ' Tage ab Bearbeitungsbeginn', ist: F(r.tage_ab_beginn) + ' Tage', ueber: r.tage_ab_beginn - frist });
      } else if (r.termin && r.abschluss > r.termin) {
        const t = Math.round((Date.parse(r.abschluss) - Date.parse(r.termin)) / 864e5);
        out.push({ ...basis, vorgabe: 'Termin ' + datum(r.termin), ist: t + (t === 1 ? ' Tag' : ' Tage') + ' später', ueber: t });
      }
    }
    return out.sort((x, y) => y.ueber - x.ueber);
  },
});

dash.calc('tt_liste_info', {
  inputs: ['tt_liste'],
  title: 'Anzahl der Aufträge außerhalb der Vorgabe',
  description: 'Zahl der Zeilen der Liste „Aufträge außerhalb der Vorgabe“; die Tabelle zeigt davon höchstens 200.',
  fn: (tt_liste) => [{ anzahl: (tt_liste || []).length }],
});

(() => {
  const F = window.LKfmt;
  dash.draw('tt_liste_n', (el) => { const s = dash.data('tt_liste_info'); el.textContent = s.status === 'ok' && s.data && s.data[0] ? F.fInt(s.data[0].anzahl) : '—'; });
  dash.draw('tb_tt_liste', (tb) => {
    const s = dash.data('tt_liste');
    tb.replaceChildren();
    if (s.status !== 'ok') return;
    for (const r of (s.data || []).slice(0, 200)) {
      const tr = document.createElement('tr');
      tr.setAttribute('data-key', encodeURIComponent(r.auftrag));
      for (const [f, cls, fmt] of [['auftrag'], ['text', 'l wrap'], ['labore', 'l'], ['abschluss', '', F.fDate], ['vorgabe', 'l'], ['ist']]) {
        const td = document.createElement('td'); if (cls) td.className = cls; td.textContent = fmt ? fmt(r[f]) : r[f]; tr.append(td);
      }
      tb.append(tr);
    }
  });

  // Klick auf eine Kachel mit data-liste wählt die Liste und springt zur Tabelle
  document.querySelectorAll('.lk [data-liste]').forEach((k) => {
    k.addEventListener('keydown', (ev) => { if (ev.key === 'Enter' || ev.key === ' ') { ev.preventDefault(); k.click(); } });
    k.addEventListener('click', () => {
      const v = k.getAttribute('data-liste');
      dash.setParams({ tt_liste: v });
      document.querySelectorAll('.lk select[data-param="tt_liste"]').forEach((sel) => { sel.value = v; });
      const ziel = document.getElementById('tt-abweichungen');
      if (ziel) ziel.scrollIntoView({ block: 'start', behavior: 'smooth' });
    });
  });
})();
