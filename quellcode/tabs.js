// Reiter: Ein Knopf zeigt einen Abschnitt oder eine Gruppe von Abschnitten (data-sections) und merkt den Ort im Link.
// Elemente mit data-ziel öffnen den Reiter, zu dem der genannte Abschnitt gehört, und springen dorthin.
(() => {
  const knoepfe = () => [...document.querySelectorAll('.lk .tabs button[data-tab]')];
  const gruppe = (b) => (b.getAttribute('data-sections') || b.getAttribute('data-tab')).split(/\s+/);
  const open = (id, link) => {
    const b = knoepfe().find((k) => gruppe(k).includes(id));
    if (!b) return;
    const ids = gruppe(b);
    document.querySelectorAll('.lk section.tab').forEach((s) => { s.hidden = !ids.includes(s.id); });
    knoepfe().forEach((k) => {
      const on = k === b;
      k.setAttribute('aria-selected', on ? 'true' : 'false');
      k.tabIndex = on ? 0 : -1;
    });
    if (link) dash.setLink(id);
    const s = document.getElementById(id);
    if (s && id !== ids[0]) requestAnimationFrame(() => s.scrollIntoView({ block: 'start', behavior: 'smooth' }));
    else if (link) { const r = document.getElementById('reiter'); if (r && r.getBoundingClientRect().top < 0) r.scrollIntoView({ block: 'start' }); }
  };
  knoepfe().forEach((b) => b.addEventListener('click', () => open(b.getAttribute('data-tab'), true)));
  document.querySelectorAll('.lk [data-ziel]').forEach((e) => {
    e.addEventListener('click', () => open(e.getAttribute('data-ziel'), true));
    e.addEventListener('keydown', (ev) => { if (ev.key === 'Enter' || ev.key === ' ') { ev.preventDefault(); open(e.getAttribute('data-ziel'), true); } });
  });
  const h = (location.hash || '').replace(/^#/, '');
  if (h) open(h, false);

  // Drucken und PDF: alle Reiter und alle Erläuterungen zeigen, danach wiederherstellen
  let vorher = null;
  window.addEventListener('beforeprint', () => {
    if (vorher) return;
    vorher = [...document.querySelectorAll('.lk section.tab, .lk details')].map((e) => [e, e.hidden, e.open]);
    for (const [e] of vorher) { if (e.tagName === 'DETAILS') e.open = true; else e.hidden = false; }
  });
  window.addEventListener('afterprint', () => {
    if (!vorher) return;
    for (const [e, hid, op] of vorher) { if (e.tagName === 'DETAILS') e.open = op; else e.hidden = hid; }
    vorher = null;
  });
})();
