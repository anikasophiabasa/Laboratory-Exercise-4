/* Sorting page: asks Flask (/api/sorting) for every step, then plays the steps like the lesson slides */
(function () {
  const $ = id => document.getElementById(id);
  const input = $('sValues'), boxes = $('sBoxes'), note = $('sNote'), playBtn = $('playBtn');
  let algo = 'bubble', order = 'asc', steps = [], idx = 0, timer = null;
  const DELAYS = [1500, 950, 600, 320, 150];            // speed 1 (slow) ... 5 (fast)

  // ---------- drawing ----------
  function cell(value, cls, label) {
    const c = document.createElement('div'); c.className = 'scell' + (cls.includes('dim') ? ' dim' : '');
    const b = document.createElement('div'); b.className = 'sbox ' + cls.replace('dim', '').trim(); b.textContent = value;
    const l = document.createElement('div'); l.className = 'slabel'; l.textContent = label || '';
    c.append(b, l); return c;
  }

  function drawPlain() {                                // preview of the typed numbers (before sorting)
    boxes.innerHTML = '';
    const vals = input.value.split(/[,\s]+/).filter(Boolean);
    if (vals.length < 2 || vals.length > 15 || vals.some(v => isNaN(Number(v)))) return;
    vals.forEach(v => boxes.append(cell(Number(v), '')));
  }

  function show(i) {
    const s = steps[i];
    boxes.innerHTML = '';
    s.array.forEach((v, k) => {
      let cls = '', label = '';
      if (s.sorted.includes(k)) cls = 'done';
      if (s.compare.includes(k)) { cls = 'cmp'; label = '▲'; }
      if (s.swap.includes(k)) { cls = 'swp'; label = '⇄'; }
      if (s.pivot === k) { cls = 'piv'; label = 'pivot'; }
      if (s.low === k) { cls = 'piv'; label = s.compare.includes(k) ? '▲' : 'lowest'; }
      if (s.range && (k < s.range[0] || k > s.range[1])) cls += ' dim';
      boxes.append(cell(v, cls, label));
    });
    note.textContent = s.note;
    note.className = 'll-log ' + (i === steps.length - 1 ? 'ok' : '');
    $('sCmp').textContent = s.comparisons;
    $('sSwp').textContent = s.swaps;
    $('sStep').textContent = (i + 1) + ' / ' + steps.length;
    $('sBar').style.width = ((i + 1) / steps.length * 100) + '%';
  }

  // ---------- playing ----------
  const delay = () => DELAYS[Number($('speed').value) - 1];
  function stop() { clearInterval(timer); timer = null; playBtn.textContent = '▶ Play'; }
  function play() {
    if (!steps.length) return;
    if (idx >= steps.length - 1) { idx = 0; show(0); }
    stop(); playBtn.textContent = '⏸ Pause';
    timer = setInterval(() => {
      if (idx >= steps.length - 1) { stop(); return; }
      idx++; show(idx);
      if (idx >= steps.length - 1) stop();
    }, delay());
  }
  function go(i) { if (!steps.length) return; stop(); idx = Math.max(0, Math.min(steps.length - 1, i)); show(idx); }

  function reset(msg) {                                 // forget the old steps when the choices change
    stop(); steps = []; idx = 0; drawPlain();
    $('sCmp').textContent = 0; $('sSwp').textContent = 0; $('sStep').textContent = '0 / 0'; $('sBar').style.width = '0';
    note.textContent = msg || 'Press “Sort it!” to start.'; note.className = 'll-log';
  }

  // ---------- talking to Flask ----------
  async function post(url, extra) {
    const res = await fetch(url, { method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(Object.assign({ values: input.value, order }, extra)) });
    return res.json();
  }

  async function sortIt() {
    try {
      const data = await post('/api/sorting', { algorithm: algo });
      if (!data.ok) { stop(); steps = []; note.textContent = data.message; note.className = 'll-log bad'; return; }
      steps = data.steps; idx = 0; $('sName').textContent = data.name;
      show(0); play();
    } catch (e) { note.textContent = 'Could not reach the server. Is Flask running?'; note.className = 'll-log bad'; }
  }

  async function compareAll() {
    try {
      const data = await post('/api/sorting/compare', {});
      const card = $('cmpCard');
      if (!data.ok) { note.textContent = data.message; note.className = 'll-log bad'; return; }
      const fewest = Math.min(...data.rows.map(r => r.comparisons));
      $('cmpIntro').textContent = 'Numbers: ' + data.values.join(', ') + ' (' + (order === 'asc' ? 'ascending' : 'descending') + '). The fewest comparisons are highlighted.';
      const body = $('cmpBody'); body.innerHTML = '';
      data.rows.forEach(r => {
        const tr = document.createElement('tr');
        [r.name, r.comparisons, r.swaps, r.result.join(', ')].forEach((t, i) => {
          const td = document.createElement('td'); td.textContent = t;
          if (i === 0) td.style.fontWeight = '600';
          if (i === 1 && r.comparisons === fewest) td.className = 'best';
          tr.append(td);
        });
        body.append(tr);
      });
      card.hidden = false; card.scrollIntoView({ behavior: 'smooth', block: 'center' });
    } catch (e) { note.textContent = 'Could not reach the server. Is Flask running?'; note.className = 'll-log bad'; }
  }

  // ---------- buttons ----------
  function showInfo() { document.querySelectorAll('.algo-info').forEach(p => { p.hidden = p.dataset.algo !== algo; }); }

  document.querySelectorAll('.algo-btn').forEach(b => b.addEventListener('click', () => {
    document.querySelectorAll('.algo-btn').forEach(x => x.classList.toggle('active', x === b));
    algo = b.dataset.algo; $('sName').textContent = b.textContent; showInfo(); reset();
  }));
  document.querySelectorAll('[data-order]').forEach(b => b.addEventListener('click', () => {
    document.querySelectorAll('[data-order]').forEach(x => x.classList.toggle('active', x === b));
    order = b.dataset.order; reset();
  }));
  document.querySelectorAll('[data-example]').forEach(b => b.addEventListener('click', () => { input.value = b.dataset.example; reset(); }));
  $('randomBtn').addEventListener('click', () => {
    const n = 6 + Math.floor(Math.random() * 4);
    input.value = Array.from({ length: n }, () => 1 + Math.floor(Math.random() * 99)).join(', '); reset();
  });
  input.addEventListener('input', () => reset());
  input.addEventListener('keydown', e => { if (e.key === 'Enter') sortIt(); });
  $('sortBtn').addEventListener('click', sortIt);
  $('compareBtn').addEventListener('click', compareAll);
  playBtn.addEventListener('click', () => { if (timer) stop(); else play(); });
  $('prevBtn').addEventListener('click', () => go(idx - 1));
  $('nextBtn').addEventListener('click', () => go(idx + 1));
  $('firstBtn').addEventListener('click', () => go(0));
  $('speed').addEventListener('input', () => { if (timer) play(); });

  drawPlain();
})();