// Lokale Laufzeit: stellt den Diagramm- und Rechenskripten das Objekt "dash" bereit (Daten, Filter, Zeichnen).
window.dash = (() => {
  const daten = window.LK_DATEN || {};
  const jahre = [...new Set((daten.auftraege || []).map((r) => r.erstellt.slice(0, 4)))].sort();
  const STANDARD = { jahr: jahre.length ? jahre[jahre.length - 1] : '2026', quartal: '', monat: '', labor: '', prio: '', bsc_periode: 'quartal' };
  let params = { ...STANDARD };
  // Filter über ein Neuladen der Seite hinweg behalten (zum Beispiel nach dem Einlesen neuer Daten)
  try { const g = JSON.parse(sessionStorage.getItem('lk-filter') || 'null'); if (g) params = { ...STANDARD, ...g }; } catch (e) { /* ohne Speicher gelten die Standardfilter */ }
  if (params.jahr !== 'alle' && !jahre.includes(params.jahr)) params.jahr = STANDARD.jahr;
  const merke = () => { try { sessionStorage.setItem('lk-filter', JSON.stringify(params)); } catch (e) { /* nicht schlimm */ } };
  const calcs = {}, draws = {}, horcher = [];
  let cache = {};

  const wert = (id) => {
    if (id in daten) return daten[id];
    if (!(id in calcs)) return undefined;
    if (!(id in cache)) cache[id] = calcs[id].fn(...calcs[id].inputs.map(wert));
    return cache[id];
  };
  const zeichne = (name) => {
    document.querySelectorAll('[data-draw="' + name + '"]').forEach((el) => {
      if (el.closest('[hidden]')) return;                         // verborgene Reiter erst beim Öffnen
      try { draws[name](el); } catch (e) { console.error('Zeichnung ' + name, e); }
    });
  };
  let geplant = false;
  const alles = () => {
    if (geplant) return;
    geplant = true;
    requestAnimationFrame(() => { geplant = false; horcher.forEach((f) => f()); Object.keys(draws).forEach(zeichne); });
  };

  window.addEventListener('DOMContentLoaded', () => {
    alles();
    new MutationObserver(alles).observe(document.body, { subtree: true, attributes: true, attributeFilter: ['hidden'] });
  });
  let breite = window.innerWidth;
  window.addEventListener('resize', () => { if (window.innerWidth !== breite) { breite = window.innerWidth; alles(); } });

  return {
    jahre,
    colors: ['var(--lk-c1)', 'var(--lk-c2)', 'var(--lk-c3)', 'var(--lk-c4)', 'var(--lk-c5)', 'var(--lk-c6)'],
    data: (id) => {
      try {
        const v = wert(id);
        return v === undefined ? { status: 'missing', data: [], message: 'Quelle fehlt: ' + id } : { status: 'ok', data: v };
      } catch (e) { console.error('Berechnung ' + id, e); return { status: 'error', data: [], message: String(e) }; }
    },
    calc: (id, o) => { calcs[id] = o; },
    loader: () => {},
    draw: (name, fn) => { if (fn) draws[name] = typeof fn === 'function' ? fn : fn.update; else if (draws[name]) zeichne(name); },
    onData: (fn) => { horcher.push(fn); },
    params: () => ({ ...params }),
    setParams: (o) => { params = { ...params, ...o }; merke(); cache = {}; alles(); },
    resetParams: () => { params = { ...STANDARD }; merke(); cache = {}; alles(); },
    setLink: (id) => { try { history.replaceState(null, '', '#' + id); } catch (e) { /* file:// ohne Verlauf */ } },
    refresh: () => {},
  };
})();
