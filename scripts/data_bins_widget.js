// Embedded in the generated U03 N01 notebook by make_exercises.py.
// No external JavaScript or network requests are needed at learner runtime.
export default {
  render({ model, el, signal }) {
    const root = el.shadowRoot || el.attachShadow({ mode: 'open' });
    const style = document.createElement('style');
    style.textContent = `
      .board { font: 14px/1.4 system-ui, sans-serif; color: #202936; }
      .hint { margin: 0 0 12px; }
      .zones { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; }
      .zone { min-height: 160px; padding: 10px; border: 2px dashed #8190a1;
              border-radius: 8px; background: #f7f9fb; }
      .zone.over { border-color: #176b8a; background: #e9f5fa; }
      .zone h3 { margin: 0 0 9px; font-size: 16px; }
      .card { margin: 0 0 8px; padding: 9px; border: 1px solid #a7b5c4;
              border-radius: 6px; background: white; cursor: grab; }
      .card:active { cursor: grabbing; }
      .card p { margin: 0 0 7px; }
      .card label { display: block; font-size: 12px; }
      .card select { width: 100%; margin-top: 3px; padding: 4px; font: inherit; }
      .count { margin-top: 10px; font-size: 12px; }
      @media (max-width: 720px) { .zones { grid-template-columns: 1fr; } }
    `;
    const board = document.createElement('div');
    board.className = 'board';
    root.replaceChildren(style, board);

    const items = Object.entries(model.get('items'));
    const move = (key, bin) => {
      const assignments = { ...model.get('assignments') };
      if (bin === 'unsorted') delete assignments[key];
      else assignments[key] = bin;
      model.set('assignments', assignments);
      model.save_changes();
      draw();
    };
    const draw = () => {
      board.replaceChildren();
      const hint = document.createElement('p');
      hint.className = 'hint';
      hint.textContent = 'Drag each card into Data or Information. You can also use its Move to menu.';
      board.appendChild(hint);
      const zones = document.createElement('div');
      zones.className = 'zones';
      board.appendChild(zones);
      const assignments = model.get('assignments');
      for (const [bin, title] of [['unsorted', 'To sort'], ['data', 'Data'], ['information', 'Information']]) {
        const zone = document.createElement('section');
        zone.className = 'zone';
        zone.dataset.zone = bin;
        zone.setAttribute('aria-label', title + ' bin');
        zone.addEventListener('dragover', event => {
          event.preventDefault();
          zone.classList.add('over');
        });
        zone.addEventListener('dragleave', () => zone.classList.remove('over'));
        zone.addEventListener('drop', event => {
          event.preventDefault();
          zone.classList.remove('over');
          const key = event.dataTransfer.getData('text/plain');
          if (Object.hasOwn(model.get('items'), key)) move(key, bin);
        });
        const heading = document.createElement('h3');
        heading.textContent = title;
        zone.appendChild(heading);
        for (const [key, text] of items) {
          if ((assignments[key] || 'unsorted') !== bin) continue;
          const card = document.createElement('div');
          card.className = 'card';
          card.dataset.item = key;
          card.draggable = true;
          card.addEventListener('dragstart', event => {
            event.dataTransfer.setData('text/plain', key);
            event.dataTransfer.effectAllowed = 'move';
          });
          const prompt = document.createElement('p');
          prompt.textContent = `${key.toUpperCase()}. ${text}`;
          card.appendChild(prompt);
          const label = document.createElement('label');
          label.textContent = `Move item ${key.toUpperCase()} to`;
          const select = document.createElement('select');
          select.setAttribute('aria-label', `Move item ${key.toUpperCase()} to`);
          for (const [value, name] of [['unsorted', 'To sort'], ['data', 'Data'], ['information', 'Information']]) {
            const option = document.createElement('option');
            option.value = value;
            option.textContent = name;
            select.appendChild(option);
          }
          select.value = bin;
          select.addEventListener('change', () => move(key, select.value));
          label.appendChild(select);
          card.appendChild(label);
          zone.appendChild(card);
        }
        zones.appendChild(zone);
      }
      const count = document.createElement('div');
      count.className = 'count';
      count.setAttribute('role', 'status');
      count.textContent = `${Object.keys(assignments).length} of ${items.length} items sorted`;
      board.appendChild(count);
    };
    model.on('change:assignments', draw);
    signal?.addEventListener('abort', () => model.off('change:assignments', draw));
    draw();
    // Running a collapsed JupyterLab cell can expand its source. Keep the
    // infrastructure input hidden once the learner-facing output is ready.
    const codeCell = el.closest('.jp-CodeCell');
    const input = codeCell?.querySelector('.jp-InputArea');
    if (input) {
      setTimeout(() => {
        if (codeCell.isConnected) input.style.setProperty('display', 'none', 'important');
      }, 0);
    }
  }
};
