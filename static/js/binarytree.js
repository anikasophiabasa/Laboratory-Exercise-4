/* Binary tree page: draws the tree (SVG) from the Flask JSON API (/api/binarytree) and animates traversals */
(function () {
  const $ = id => document.getElementById(id);
  const svg = $('btSvg'), log = $('btLog'), out = $('btOutput');
  const valEl = $('btValue'), parEl = $('btParent');
  const NS = 'http://www.w3.org/2000/svg';
  const GAP_X = 58, GAP_Y = 78, R = 22, PAD = 34;
  let timer = null;

  function el(name, attrs) {
    const e = document.createElementNS(NS, name);
    for (const k in attrs) e.setAttribute(k, attrs[k]);
    return e;
  }

  // ---------- drawing ----------
  function layout(root) {                         // x = inorder position, y = depth
    const nodes = [], edges = [];
    let col = 0;
    (function walk(n, depth, parent) {
      if (!n) return;
      walk(n.left, depth + 1, n);
      n.x = PAD + col++ * GAP_X; n.y = PAD + depth * GAP_Y;
      nodes.push(n);
      if (parent) edges.push([parent, n]);
      walk(n.right, depth + 1, n);
    })(root, 0, null);
    return { nodes, edges, cols: col };
  }

  function draw(tree, highlight, path) {
    stop();
    svg.innerHTML = '';
    if (!tree) {
      svg.setAttribute('viewBox', '0 0 400 120'); svg.setAttribute('width', 400); svg.setAttribute('height', 120);
      const t = el('text', { x: 200, y: 60, 'text-anchor': 'middle', fill: '#9c9ab5', 'font-size': 14 });
      t.textContent = 'The tree is empty (root → NULL)'; svg.append(t); return;
    }
    const L = layout(tree);
    const maxY = Math.max(...L.nodes.map(n => n.y));
    const w = PAD * 2 + (L.cols - 1) * GAP_X, h = maxY + PAD + R;
    svg.setAttribute('viewBox', `0 0 ${w} ${h}`); svg.setAttribute('width', w); svg.setAttribute('height', h);
    L.edges.forEach(([a, b]) => svg.append(el('line', { class: 'bt-edge', x1: a.x, y1: a.y, x2: b.x, y2: b.y })));
    L.nodes.forEach(n => {
      const g = el('g', { class: 'bt-node', 'data-value': n.value });
      if (path && path.includes(n.value)) g.classList.add('visit');
      if (highlight === n.value) { g.classList.remove('visit'); g.classList.add('found', 'pop'); }
      g.append(el('circle', { cx: n.x, cy: n.y, r: R }));
      const t = el('text', { x: n.x, y: n.y }); t.textContent = n.value; g.append(t);
      g.addEventListener('click', () => {
        parEl.value = n.value;
        svg.querySelectorAll('.bt-node.sel').forEach(x => x.classList.remove('sel'));
        g.classList.add('sel'); valEl.focus();
      });
      svg.append(g);
    });
  }

  function say(msg, ok) { log.textContent = msg; log.className = 'll-log ' + (ok ? 'ok' : 'bad'); }

  function stats(d) {
    $('btSize').textContent = d.size; $('btHeight').textContent = d.height;
    $('btRoot').textContent = d.tree ? d.tree.value : '—';
  }

  // ---------- traversal animation: light up the nodes one at a time ----------
  function stop() { clearInterval(timer); timer = null; }
  function animate(order, label) {
    let i = 0;
    out.innerHTML = '<b>' + label.toUpperCase() + ':</b> ';
    const nodes = {}; svg.querySelectorAll('.bt-node').forEach(g => { nodes[g.dataset.value] = g; });
    svg.querySelectorAll('.bt-node').forEach(g => g.classList.remove('visit', 'found', 'pop'));
    timer = setInterval(() => {
      if (i >= order.length) { stop(); return; }
      const g = nodes[order[i]];
      if (g) g.classList.add('visit');
      out.append(order[i] + (i < order.length - 1 ? ' → ' : ''));
      i++;
    }, 650);
  }

  // ---------- talking to Flask ----------
  async function call(op, isTraversal) {
    try {
      const res = await fetch('/api/binarytree/' + op, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ value: valEl.value, parent: parEl.value })
      });
      const d = await res.json();
      draw(d.tree, d.highlight, isTraversal ? [] : d.path);
      stats(d); say(d.message, d.ok);
      if (isTraversal && d.ok) animate(d.order, op);
      else if (op !== 'search') out.textContent = 'Press a traversal button to see the order the nodes are visited.';
      if (d.ok && (op.startsWith('insert') || op === 'set_root')) { valEl.value = ''; valEl.focus(); }
    } catch (e) { say('Could not reach the server. Is Flask running?', false); }
  }

  document.querySelectorAll('[data-op]').forEach(b => b.addEventListener('click', () => call(b.dataset.op, false)));
  document.querySelectorAll('[data-trav]').forEach(b => b.addEventListener('click', () => call(b.dataset.trav, true)));
  valEl.addEventListener('keydown', e => { if (e.key === 'Enter') call('insert_left', false); });

  fetch('/api/binarytree').then(r => r.json()).then(d => {
    draw(d.tree); stats(d); say('Binary tree loaded. Try a traversal!', true);
  });
})();