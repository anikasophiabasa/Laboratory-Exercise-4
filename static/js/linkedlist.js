/* Linked list UI — talks to the Flask JSON API (/api/linkedlist) */
(function () {
  const track = document.getElementById('llTrack'), log = document.getElementById('llLog');
  const valEl = document.getElementById('llValue'), idxEl = document.getElementById('llIndex');

  function render(state, highlight) {
    document.getElementById('llSize').textContent = state.size;
    document.getElementById('llHead').textContent = state.nodes[0] ?? '—';
    document.getElementById('llTail').textContent = state.nodes[state.nodes.length - 1] ?? '—';
    track.innerHTML = '';
    if (!state.nodes.length) { track.innerHTML = '<div class="ll-empty">The list is empty — head → <span class="ll-null">NULL</span></div>'; return; }
    state.nodes.forEach((v, i) => {
      const n = document.createElement('div');
      n.className = 'll-node' + (i === highlight ? ' hl' : '');
      n.style.animationDelay = (i * 0.05) + 's';
      const box = document.createElement('div'); box.className = 'll-box';
      const idx = document.createElement('span'); idx.className = 'idx'; idx.textContent = i;
      const val = document.createElement('span'); val.className = 'val'; val.textContent = v; val.title = v;
      const ptr = document.createElement('span'); ptr.className = 'ptr'; ptr.textContent = '●';
      box.append(idx, val, ptr);
      if (i === 0) { const h = document.createElement('span'); h.className = 'tagh'; h.textContent = 'HEAD'; box.append(h); }
      if (i === state.nodes.length - 1 && i !== 0) { const t = document.createElement('span'); t.className = 'tagh'; t.textContent = 'TAIL'; box.append(t); }
      n.append(box);
      const link = document.createElement('span'); link.className = 'll-link'; n.append(link);
      track.append(n);
    });
    const end = document.createElement('span'); end.className = 'll-null'; end.textContent = 'NULL'; track.append(end);
  }

  function say(msg, ok) { log.textContent = msg; log.className = 'll-log ' + (ok ? 'ok' : 'bad'); }

  async function call(op) {
    try {
      const res = await fetch('/api/linkedlist/' + op, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ value: valEl.value, index: idxEl.value })
      });
      const data = await res.json();
      render(data, data.highlight);
      say(data.message, data.ok);
      if (data.ok && op.startsWith('insert')) { valEl.value = ''; valEl.focus(); }
    } catch (e) { say('Could not reach the server. Is Flask running?', false); }
  }

  document.querySelectorAll('[data-op]').forEach(b => b.addEventListener('click', () => call(b.dataset.op)));
  valEl.addEventListener('keydown', e => { if (e.key === 'Enter') call('insert_tail'); });

  fetch('/api/linkedlist').then(r => r.json()).then(d => { render(d); say('Linked list loaded — try inserting something!', true); });
})();
