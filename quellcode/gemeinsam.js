// Gemeinsame Helfer: SOLL-Werte aus den Vorgaben, Ampelfarbe für Kacheln mit SOLL.
(() => {
  // Werte, die gelten, solange das Blatt BSC_Vorgaben keinen Eintrag hat (wie in der BSC-Rechnung)
  const STD = { soll_reaktion_s: 90, soll_reaktion_m: 50, soll_puenktlich_m: 50, soll_puenktlich_l: 90, max_rueckweisung: 5,
    soll_termintreue: 65, soll_budgeteinhaltung: 80, soll_qualitaetslevel: 80, max_vergabequote: 20,
    ziel_plankosten: 100, ziel_auftragsquote: 100, ziel_instandhaltungsquote: 65, ziel_methodeneinsatz: 25 };
  window.LKsoll = (k) => {
    const s = dash.data('bsc_vorgaben');
    const r = s.status === 'ok' ? (s.data || []).find((x) => x.schluessel === k) : null;
    return r && r.wert != null ? r.wert : (k in STD ? STD[k] : null);
  };

  // Ein SOLL-Wert als Text, z. B. in „SOLL ≥ 90,0 %“
  for (const k of Object.keys(STD)) {
    if (document.querySelector('[data-draw="lk_soll_' + k + '"]')) dash.draw('lk_soll_' + k, (el) => { const v = window.LKsoll(k); el.textContent = v == null ? '—' : window.LKfmt.fPct(v); });
  }

  // Ampel: Ein Element mit data-soll="schluessel" (und data-soll-art="max" für Höchstwerte) wird grün oder rot,
  // sobald es eine Prozentzahl zeigt.
  const zahl = (t) => { const s = String(t).replace(/\./g, '').replace(',', '.').replace(/[^0-9.\-]/g, ''); return s === '' ? NaN : Number(s); };
  const faerbe = (el) => {
    const v = zahl(el.textContent), s = window.LKsoll(el.getAttribute('data-soll'));
    const gut = el.getAttribute('data-soll-art') === 'max' ? v <= s : v >= s;
    const soll = Number.isNaN(v) || s == null ? null : gut ? 'good' : 'bad';
    for (const c of ['good', 'bad']) if (el.classList.contains(c) !== (c === soll)) el.classList.toggle(c, c === soll);
  };
  const alle = () => document.querySelectorAll('.lk [data-soll]').forEach(faerbe);
  new MutationObserver((ms) => {
    for (const m of ms) { const el = (m.target.nodeType === 1 ? m.target : m.target.parentElement); const z = el && el.closest('[data-soll]'); if (z) faerbe(z); }
  }).observe(document.body, { subtree: true, childList: true, characterData: true });

  alle();
})();
