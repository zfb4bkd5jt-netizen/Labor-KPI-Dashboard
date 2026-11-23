// Für alle Diagramme: Werte als Zahl an Punkten und Balken und eine Vollbild-Ansicht.
// Beides wird nach jedem Zeichnen im Diagramm selbst ergänzt, ohne die einzelnen Diagramme zu kennen.
(() => {
  const NS = 'http://www.w3.org/2000/svg';
  const voll = (card) => !!card && (card.classList.contains('lk-voll') || document.fullscreenElement === card);
  // Höhe, mit der ein Diagramm zeichnet: im Vollbild der verfügbare Platz, sonst die Standardhöhe
  window.LKhoehe = (el, std) => (voll(el.closest('.card')) ? Math.max(std, Math.floor(el.clientHeight - 30)) : std);

  const zahl = (t) => { const s = t.replace(/\./g, '').replace(',', '.').replace(/[^0-9.\-−]/g, '').replace('−', '-'); return s === '' ? NaN : Number(s); };
  const de = (v, n) => v.toLocaleString('de-DE', { minimumFractionDigits: n, maximumFractionDigits: n });

  // Werte aus der Zeichnung zurückrechnen: Die Achsenstriche geben an, welcher Wert auf welcher Höhe liegt.
  const beschrifte = (el) => {
    const svg = el.querySelector(':scope > svg');
    if (!svg || svg.querySelector('.lk-werte') || !svg.viewBox.baseVal.width) return;
    const ticks = [], versatz = window.devicePixelRatio > 1 ? 0 : 0.5;      // d3 rückt Achsenstriche auf einfachen Bildschirmen um einen halben Punkt
    svg.querySelectorAll('.tick').forEach((t) => {
      const tx = t.querySelector('text'), m = /translate\(\s*([-\d.e]+)[ ,]+([-\d.e]+)/.exec(t.getAttribute('transform') || '');
      if (!tx || !m || !tx.textContent.trim() || !(Number(tx.getAttribute('x')) < 0)) return;      // nur die linke Achse
      const v = zahl(tx.textContent);
      if (!Number.isNaN(v)) ticks.push({ y: Number(m[2]) - versatz, v, text: tx.textContent });
    });
    ticks.sort((a, b) => a.y - b.y);
    if (ticks.length < 2 || ticks[0].y === ticks[ticks.length - 1].y) return;                        // z. B. liegende Balken: dort stehen die Werte schon
    const a = ticks[0], b = ticks[ticks.length - 1], k = (b.v - a.v) / (b.y - a.y);
    const wert = (y) => a.v + (y - a.y) * k, hoehe = (h) => Math.abs(h * k);
    // Einheit wie an der Achse: der Text des höchsten Achsenstrichs ohne seine Zahl (z. B. „ T€“); Prozentwerte ohne Zeichen, das spart Platz
    const einheit = a.text.replace(/[-−\d.,\s]+/, '').trim(), prozent = einheit === '%';
    const text = (v) => {
      if (Math.abs(v) < 1e-6) v = 0;
      const s = de(v, prozent ? (Math.abs(v) >= 100 ? 0 : 1) : (Math.abs(v) >= 100 || Math.abs(v - Math.round(v)) < 0.005 ? 0 : 1));
      return prozent || !einheit ? s : s + ' ' + einheit;
    };
    const W = svg.viewBox.baseVal.width, H = svg.viewBox.baseVal.height;
    const ort = (n) => { const r = n.getBoundingClientRect(), s = svg.getBoundingClientRect(), f = W / (s.width || W); return { x: (r.left - s.left) * f, y: (r.top - s.top) * f, w: r.width * f, h: r.height * f }; };
    const g = document.createElementNS(NS, 'g'); g.setAttribute('class', 'lk-werte'); g.setAttribute('pointer-events', 'none'); svg.append(g);
    const belegt = [];
    const setze = (s, x, y, anker, farbe, innen, breite) => {
      const t = document.createElementNS(NS, 'text'); t.textContent = s; t.setAttribute('x', x); t.setAttribute('y', y); t.setAttribute('text-anchor', anker);
      if (innen) t.setAttribute('class', 'innen'); else if (farbe) t.style.fill = farbe;
      g.append(t);
      const bb = t.getBBox(), box = [bb.x - 1, bb.y, bb.x + bb.width + 1, bb.y + bb.height];
      if ((breite && bb.width > breite) || box[0] < 0 || box[2] > W || box[1] < 0 || box[3] > H || belegt.some((o) => box[0] < o[2] && box[2] > o[0] && box[1] < o[3] && box[3] > o[1])) { t.remove(); return false; }
      belegt.push(box); return true;
    };

    // Balken: gestapelte Teile innen, die Summe darüber; einzelne Balken mit dem Wert darüber
    const balken = [...svg.querySelectorAll('rect')].filter((r) => { const f = r.style.fill || r.getAttribute('fill') || ''; return f && f !== 'transparent' && f !== 'none'; })
      .map((r) => ({ r, ...ort(r) })).filter((o) => o.w > 0 && o.h > 0);
    const spalten = new Map();
    for (const o of balken) { const key = Math.round(o.x * 2) + '|' + Math.round(o.w * 2); if (!spalten.has(key)) spalten.set(key, []); spalten.get(key).push(o); }
    const sp = [...spalten.values()].sort((p, q) => p[0].x - q[0].x);
    for (const teile of sp) {
      const oben = Math.min(...teile.map((o) => o.y)), o0 = teile[0];
      const summe = teile.reduce((t, o) => t + hoehe(o.h), 0);
      setze(text(summe), o0.x + o0.w / 2, oben - 4, 'middle', teile.length > 1 ? null : (o0.r.style.fill || null), false);
    }
    for (const teile of sp) if (teile.length > 1) for (const o of teile) if (o.h >= 13) setze(text(hoehe(o.h)), o.x + o.w / 2, o.y + o.h / 2 + 4, 'middle', null, true, o.w + 4);

    // Linien: je Reihe zuerst der letzte, höchste, niedrigste und erste Punkt, dann alle weiteren, soweit Platz ist
    const reihen = new Map();
    svg.querySelectorAll('circle').forEach((c) => { const p = c.parentNode; if (!reihen.has(p)) reihen.set(p, []); const o = ort(c); reihen.get(p).push({ x: o.x + o.w / 2, y: o.y + o.h / 2, v: wert(Number(c.getAttribute('cy'))), farbe: c.style.fill || null }); });
    const folge = [];
    for (const pts of reihen.values()) for (const p of pts) belegt.push([p.x - 3, p.y - 3, p.x + 3, p.y + 3]);      // Werte nicht auf andere Punkte setzen
    for (const pts of reihen.values()) {
      if (!pts.length) continue;
      const max = pts.reduce((m, p) => (p.v > m.v ? p : m)), min = pts.reduce((m, p) => (p.v < m.v ? p : m));
      folge.push([pts[pts.length - 1], max, min, pts[0]], pts);
    }
    const fertig = new Set();
    for (let stufe = 0; stufe < 2; stufe++) for (let i = stufe; i < folge.length; i += 2) for (const p of folge[i]) {
      if (fertig.has(p)) continue;
      if (setze(text(p.v), p.x, p.y - 7, 'middle', p.farbe, false) || setze(text(p.v), p.x, p.y + 15, 'middle', p.farbe, false)) fertig.add(p);
    }
  };

  // Vollbild: Schaltfläche in jedem Diagramm; die Karte füllt dann den Bildschirm und das Diagramm zeichnet sich in voller Größe neu
  const zeichneNeu = (card) => {
    const neu = () => card.querySelectorAll('.chart[data-draw]').forEach((c) => dash.draw(c.getAttribute('data-draw')));
    requestAnimationFrame(neu); setTimeout(neu, 300);            // zweimal: der Wechsel ins Vollbild und zurück braucht einen Moment
  };
  const schalte = (card) => {
    if (!voll(card)) {
      card.classList.add('lk-voll');
      const p = card.requestFullscreen ? card.requestFullscreen() : null;
      if (p && p.then) p.then(() => zeichneNeu(card), () => zeichneNeu(card)); else zeichneNeu(card);
    } else {
      card.classList.remove('lk-voll');
      if (document.fullscreenElement && document.exitFullscreen) document.exitFullscreen().then(() => zeichneNeu(card), () => zeichneNeu(card)); else zeichneNeu(card);
    }
  };
  document.addEventListener('fullscreenchange', () => {
    if (!document.fullscreenElement) document.querySelectorAll('.lk .card.lk-voll').forEach((c) => { c.classList.remove('lk-voll'); zeichneNeu(c); });
  });
  document.addEventListener('keydown', (ev) => {
    if (ev.key === 'Escape' && !document.fullscreenElement) document.querySelectorAll('.lk .card.lk-voll').forEach((c) => { c.classList.remove('lk-voll'); zeichneNeu(c); });
  });
  const knopf = (el) => {
    const card = el.closest('.card');
    if (!card) return;
    let b = el.querySelector(':scope > .lk-voll-btn');
    if (!b) {
      b = document.createElement('button'); b.type = 'button'; b.className = 'lk-voll-btn';
      b.addEventListener('click', () => schalte(card));
      el.append(b);
    }
    const an = voll(card), s = an ? '✕ Schließen' : '⛶ Vollbild';
    if (b.textContent !== s) { b.textContent = s; b.setAttribute('aria-label', an ? 'Vollbild schließen' : 'Diagramm im Vollbild zeigen'); }
  };

  const ergaenze = (el) => { if (el.isConnected && !el.closest('[hidden]')) { try { beschrifte(el); } catch (e) { console.error('Wertbeschriftung', e); } knopf(el); } };
  let wartend = new Set(), geplant = false;
  const plane = (el) => { wartend.add(el); if (geplant) return; geplant = true; requestAnimationFrame(() => { geplant = false; const l = [...wartend]; wartend = new Set(); l.forEach(ergaenze); }); };
  const sucht = (n) => { if (n.nodeType !== 1) return; const c = n.closest('.lk .chart[data-draw]'); if (c) plane(c); else n.querySelectorAll('.lk .chart[data-draw]').forEach(plane); };
  new MutationObserver((ms) => { for (const m of ms) { if (m.type === 'attributes') sucht(m.target); else if (m.target.nodeType === 1 && m.target.matches('.lk .chart[data-draw]')) plane(m.target); } })
    .observe(document.body, { subtree: true, childList: true, attributes: true, attributeFilter: ['hidden'] });
  document.querySelectorAll('.lk .chart[data-draw]').forEach(plane);
})();
