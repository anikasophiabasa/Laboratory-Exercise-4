/* Queue UI: talks to the Flask JSON API (/api/queue) */
(function () {
  const track = document.getElementById('qTrack'), log = document.getElementById('qLog');
  const valEl = document.getElementById('qValue');
  const sleep = ms => new Promise(r => setTimeout(r, ms));

  // draw the queue: FRONT on the left, REAR on the right
  function render(state, highlight, isNew) {
    document.getElementById('qSize').textContent = state.size;
    document.getElementById('qFront').textContent = state.nodes[0] ?? '—';
    document.getElementById('qRear').textContent = state.nodes[state.nodes.length - 1] ?? '—';
    document.getElementById('qEmpty').textContent = state.nodes.length ? 'No' : 'Yes';
    track.innerHTML = '';
    if (!state.nodes.length) {
      track.innerHTML = '<div class="ll-empty">The queue is empty — front → <span class="ll-null">NULL</span></div>';
      return;
    }
    const last = state.nodes.length - 1;
    state.nodes.forEach((v, i) => {
      const n = document.createElement('div');
      n.className = 'll-node' + (i === highlight ? ' hl' : '') + (isNew && i === highlight ? ' new' : '');
      if (!(isNew && i === highlight)) n.style.animation = 'none';   // only the new node slides in
      const box = document.createElement('div'); box.className = 'll-box';
      const idx = document.createElement('span'); idx.className = 'idx'; idx.textContent = i;
      const val = document.createElement('span'); val.className = 'val'; val.textContent = v; val.title = v;
      const ptr = document.createElement('span'); ptr.className = 'ptr'; ptr.textContent = '●';
      box.append(idx, val, ptr);
      let tag = '';
      if (i === 0 && i === last) tag = 'FRONT · REAR';
      else if (i === 0) tag = 'FRONT';
      else if (i === last) tag = 'REAR';
      if (tag) { const t = document.createElement('span'); t.className = 'tagh'; t.textContent = tag; box.append(t); }
      n.append(box);
      const link = document.createElement('span'); link.className = 'll-link'; n.append(link);
      track.append(n);
    });
    const end = document.createElement('span'); end.className = 'll-null'; end.textContent = 'NULL'; track.append(end);
  }

  function say(msg, ok) { log.textContent = msg; log.className = 'll-log ' + (ok ? 'ok' : 'bad'); }

  async function call(op) {
    try {
      const res = await fetch('/api/queue/' + op, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ value: valEl.value })
      });
      const data = await res.json();

      // dequeue: let the front node slide out first, then redraw
      if (data.ok && data.removed !== null && data.removed !== undefined) {
        const first = track.querySelector('.ll-node');
        if (first) { first.classList.add('leaving'); await sleep(350); }
      }
      render(data, data.highlight, data.ok && op === 'enqueue');
      say(data.message, data.ok);
      if (data.ok && op === 'enqueue') { valEl.value = ''; valEl.focus(); }
    } catch (e) { say('Could not reach the server. Is Flask running?', false); }
  }

  document.querySelectorAll('[data-op]').forEach(b => b.addEventListener('click', () => call(b.dataset.op)));
  valEl.addEventListener('keydown', e => { if (e.key === 'Enter') call('enqueue'); });

  fetch('/api/queue').then(r => r.json()).then(d => { render(d); say('Queue loaded. Try enqueueing something!', true); });
})();
