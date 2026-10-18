/* Spanish manual seat simulator UI.
   Handles interactive hemicycle, responsive data table, and privacy-safe URL sharing.
*/
(function (root) {
  'use strict';

  const engine = root.SimulatorEngine;
  if (!engine) {
    console.warn('SimulatorEngine not loaded.');
    return;
  }

  // Accessible, high-contrast palette for up to 30 groups
  const PALETTE = [
    '#2563eb', '#dc2626', '#16a34a', '#9333ea', '#ea580c',
    '#0891b2', '#ca8a04', '#db2777', '#4f46e5', '#059669',
    '#b91c1c', '#475569', '#0284c7', '#7c3aed', '#d97706',
    '#10b981', '#f43f5e', '#6366f1', '#14b8a6', '#84cc16',
    '#e11d48', '#8b5cf6', '#06b6d4', '#f59e0b', '#22c55e',
    '#ec4899', '#3b82f6', '#64748b', '#a855f7', '#0d9488'
  ];

  // Hemicycle 350-seat arc configuration (6 rows: 38 + 46 + 54 + 62 + 72 + 78 = 350)
  const HEMICYCLE_ROWS = [
    { radius: 72, count: 38 },
    { radius: 94, count: 46 },
    { radius: 116, count: 54 },
    { radius: 138, count: 62 },
    { radius: 160, count: 72 },
    { radius: 182, count: 78 }
  ];

  function computeSeatPositions() {
    const cx = 200;
    const cy = 200;
    const positions = [];
    for (const row of HEMICYCLE_ROWS) {
      const { radius, count } = row;
      for (let i = 0; i < count; i++) {
        // Distribute angle evenly from PI (180deg - left) to 0 (0deg - right)
        const angle = Math.PI - (i / (count - 1)) * Math.PI;
        const x = cx + radius * Math.cos(angle);
        const y = cy - radius * Math.sin(angle);
        positions.push({ x: Number(x.toFixed(2)), y: Number(y.toFixed(2)), angle });
      }
    }
    // Sort positions ray-by-ray (by angle descending from left to right, then by radius)
    positions.sort((a, b) => {
      const angleDiff = b.angle - a.angle;
      if (Math.abs(angleDiff) > 0.0001) return angleDiff;
      return a.radius - b.radius;
    });
    return positions;
  }

  const SEAT_POSITIONS = computeSeatPositions();

  // Initial starter scenario
  function defaultGroups() {
    return [
      { id: 'g-1', label: 'Grupo A', seats: '135' },
      { id: 'g-2', label: 'Grupo B', seats: '120' },
      { id: 'g-3', label: 'Grupo C', seats: '35' },
      { id: 'g-4', label: 'Grupo D', seats: '30' },
      { id: 'g-5', label: 'Grupo E', seats: '20' },
      { id: 'g-6', label: 'Grupo F', seats: '10' }
    ];
  }

  function emptyGroups() {
    return [
      { id: 'g-1', label: 'Grupo A', seats: '0' }
    ];
  }

  let state = {
    groups: [],
    selectedIds: [],
    idCounter: 10
  };

  function getUniqueId() {
    state.idCounter += 1;
    return 'g-' + state.idCounter + '-' + Math.random().toString(36).slice(2, 6);
  }

  function initFromUrlOrDefaults() {
    const fromUrl = engine.deserializeScenario(window.location.href);
    if (fromUrl && fromUrl.groups && fromUrl.groups.length) {
      state.groups = fromUrl.groups;
      state.selectedIds = fromUrl.selectedIds || [];
      return;
    }
    const profile = window.SimulatorProfile;
    if (profile && Array.isArray(profile.sample_groups) && profile.sample_groups.length) {
      state.groups = profile.sample_groups.map((g, idx) => ({
        id: g.id || ('g-' + (idx + 1)),
        label: g.label || ('Grupo ' + (idx + 1)),
        seats: String(g.seats || '0')
      }));
    } else {
      state.groups = defaultGroups();
    }
    state.selectedIds = [];
  }

  function announce(message) {
    const el = document.getElementById('simulator-status');
    if (el) el.textContent = message;
  }

  function renderHemicycle(calculation) {
    const container = document.getElementById('simulator-hemicycle-chart');
    if (!container) return;

    const totalSeats = engine.limits.totalSeats;
    const isValid = calculation && calculation.status !== 'invalid';
    const groups = isValid ? calculation.groups : [];
    const selectedSet = new Set(calculation && calculation.coalition ? state.selectedIds : []);

    // Build assignment array for each of the 350 seats
    const seatAssignments = [];
    if (isValid) {
      groups.forEach((group, gIdx) => {
        const color = PALETTE[gIdx % PALETTE.length];
        const inCoalition = selectedSet.has(group.id);
        const count = group.seats || 0;
        for (let s = 0; s < count; s++) {
          seatAssignments.push({
            group,
            color,
            inCoalition,
            unassigned: false
          });
        }
      });
    }

    // Fill remaining seats as unassigned
    while (seatAssignments.length < totalSeats) {
      seatAssignments.push({
        group: null,
        color: '#cbd5e1',
        inCoalition: false,
        unassigned: true
      });
    }

    // Build SVG elements
    const hasSelection = selectedSet.size > 0;
    const dotsSvg = seatAssignments.slice(0, totalSeats).map((seat, idx) => {
      const pos = SEAT_POSITIONS[idx] || { x: 200, y: 200 };
      const opacity = seat.unassigned
        ? '0.4'
        : (hasSelection && !seat.inCoalition ? '0.3' : '1.0');
      const r = seat.inCoalition ? '4.8' : '3.8';
      const stroke = seat.inCoalition ? '#1e293b' : (seat.unassigned ? '#94a3b8' : 'none');
      const strokeWidth = seat.inCoalition ? '1.5' : (seat.unassigned ? '0.75' : '0');

      return `<circle class="simulator-hemicycle-dot"
        cx="${pos.x}" cy="${pos.y}" r="${r}"
        fill="${seat.color}"
        stroke="${stroke}"
        stroke-width="${strokeWidth}"
        opacity="${opacity}" />`;
    }).join('\n');

    // Threshold indicator line & center text
    const coalitionSeats = calculation && calculation.coalition ? calculation.coalition.seats : 0;
    const reaches = calculation && calculation.coalition && calculation.coalition.reachesThreshold;
    const assignedSeats = isValid ? calculation.assigned : 0;

    const centerNumber = hasSelection ? coalitionSeats : assignedSeats;
    const centerSub = hasSelection
      ? (reaches ? 'Mayoría absoluta (≥ 176)' : 'Coalición (faltan ' + (176 - coalitionSeats) + ')')
      : assignedSeats + ' / 350 escaños';

    const svgHtml = `
      <svg class="simulator-hemicycle-svg" viewBox="0 15 400 205" role="img"
        aria-label="Hemiciclo de 350 escaños. ${assignedSeats} asignados, ${350 - assignedSeats} sin asignar. ${coalitionSeats} en coalición.">
        <!-- Majority line mark at center base -->
        <line x1="200" y1="20" x2="200" y2="60" stroke="#94a3b8" stroke-width="1.5" stroke-dasharray="3,3" />
        <g id="hemicycle-dots">
          ${dotsSvg}
        </g>
        <g class="hemicycle-center-readout">
          <text x="200" y="172" text-anchor="middle" font-size="28" font-weight="700" fill="currentColor">${centerNumber}</text>
          <text x="200" y="192" text-anchor="middle" font-size="11" fill="var(--color-text-secondary, #64748b)">${centerSub}</text>
        </g>
      </svg>
    `;

    container.innerHTML = svgHtml;

    // Legend
    const legendEl = document.getElementById('simulator-hemicycle-legend');
    if (legendEl) {
      if (!isValid || groups.length === 0) {
        legendEl.innerHTML = '';
      } else {
        const legendItems = groups.map((g, idx) => {
          const color = PALETTE[idx % PALETTE.length];
          const isSelected = selectedSet.has(g.id);
          const weight = isSelected ? 'font-weight: 700;' : '';
          return `
            <span class="simulator-legend-item" style="${weight}">
              <span class="simulator-legend-dot" style="background: ${color};"></span>
              <span>${escapeHtml(g.label || 'Grupo')} (${g.seats || 0})</span>
            </span>
          `;
        });
        legendItems.push(`
          <span class="simulator-legend-item">
            <span class="simulator-legend-dot" style="background: #cbd5e1; border: 1px solid #94a3b8;"></span>
            <span>Sin asignar (${calculation.unassigned})</span>
          </span>
        `);
        legendEl.innerHTML = legendItems.join('');
      }
    }
  }

  function renderSummary(calculation) {
    const isValid = calculation && calculation.status !== 'invalid';
    const assignedEl = document.getElementById('stat-assigned');
    const unassignedEl = document.getElementById('stat-unassigned');
    const coalitionEl = document.getElementById('stat-coalition');
    const thresholdEl = document.getElementById('stat-threshold');
    const bannerEl = document.getElementById('simulator-threshold-banner');

    if (!assignedEl || !unassignedEl || !coalitionEl || !thresholdEl || !bannerEl) return;

    if (!isValid) {
      assignedEl.textContent = '—';
      unassignedEl.textContent = '—';
      coalitionEl.textContent = '—';
      thresholdEl.textContent = '—';

      bannerEl.className = 'simulator-threshold-banner chamber-overflow';
      bannerEl.innerHTML = `
        <div class="simulator-threshold-title">Escenario no válido</div>
        <p class="simulator-threshold-desc">Corrige los errores indicados en la tabla para ver los cálculos.</p>
      `;
      return;
    }

    assignedEl.textContent = String(calculation.assigned);
    unassignedEl.textContent = String(calculation.unassigned);

    const coalition = calculation.coalition;
    if (!coalition) {
      coalitionEl.textContent = '0';
      thresholdEl.textContent = '—';

      bannerEl.className = 'simulator-threshold-banner';
      bannerEl.innerHTML = `
        <div class="simulator-threshold-title">Selecciona grupos para sumar sus escaños</div>
        <p class="simulator-threshold-desc">Marca las casillas de la columna «Coalición» para comprobar si alcanzan la mayoría absoluta de 176 escaños.</p>
      `;
    } else {
      coalitionEl.textContent = String(coalition.seats);

      if (coalition.reachesThreshold) {
        thresholdEl.textContent = '+' + coalition.surplus;
        bannerEl.className = 'simulator-threshold-banner majority-reached';
        bannerEl.innerHTML = `
          <div class="simulator-threshold-title">Alcanza la mayoría absoluta en primera votación</div>
          <p class="simulator-threshold-desc">
            La suma de los grupos seleccionados es de <strong>${coalition.seats} escaños</strong>.
            ${coalition.surplus > 0 ? `Supera los 176 escaños requeridos por <strong>${coalition.surplus} escaño(s)</strong>.` : 'Alcanza exactamente el umbral de 176 escaños.'}
          </p>
        `;
      } else {
        thresholdEl.textContent = '-' + coalition.deficit;
        bannerEl.className = 'simulator-threshold-banner majority-short';
        bannerEl.innerHTML = `
          <div class="simulator-threshold-title">No alcanza la mayoría absoluta en primera votación</div>
          <p class="simulator-threshold-desc">
            La suma de los grupos seleccionados es de <strong>${coalition.seats} escaños</strong>.
            Faltan <strong>${coalition.deficit} escaño(s)</strong> para alcanzar la mayoría absoluta de 176.
          </p>
        `;
      }
    }
  }

  function renderTable(calculation) {
    const tbody = document.getElementById('simulator-groups-tbody');
    const errorSummary = document.getElementById('simulator-errors-container');
    if (!tbody) return;

    const errors = (calculation && calculation.errors) || [];
    const errorMap = new Map();
    const scenarioErrors = [];

    for (const err of errors) {
      if (err.index !== null && err.index !== undefined) {
        if (!errorMap.has(err.index)) errorMap.set(err.index, []);
        errorMap.get(err.index).push(err);
      } else {
        scenarioErrors.push(err);
      }
    }

    if (errorSummary) {
      if (scenarioErrors.length) {
        const items = scenarioErrors.map(e => {
          if (e.code === 'total-exceeds-chamber') {
            return '<li>La suma total de escaños supera el aforo del Congreso (máximo 350 escaños).</li>';
          }
          if (e.code === 'group-count') {
            return '<li>El número de grupos debe estar entre 1 y 30.</li>';
          }
          return '<li>' + escapeHtml(e.code) + '</li>';
        }).join('');
        errorSummary.innerHTML = `
          <div class="simulator-error-summary" role="alert">
            <strong>Atención:</strong>
            <ul>${items}</ul>
          </div>
        `;
        errorSummary.hidden = false;
      } else {
        errorSummary.innerHTML = '';
        errorSummary.hidden = true;
      }
    }

    const selectedSet = new Set(state.selectedIds);
    const rowsHtml = state.groups.map((group, idx) => {
      const color = PALETTE[idx % PALETTE.length];
      const rowErrors = errorMap.get(idx) || [];
      const hasLabelError = rowErrors.some(e => e.field === 'label');
      const hasSeatsError = rowErrors.some(e => e.field === 'seats');

      const labelErrMsg = rowErrors.find(e => e.field === 'label');
      const seatsErrMsg = rowErrors.find(e => e.field === 'seats');

      let labelText = '';
      if (labelErrMsg) {
        labelText = labelErrMsg.code === 'duplicate-label'
          ? 'Nombre repetido'
          : 'Nombre obligatorio (máx. 60 caracteres)';
      }

      let seatsText = '';
      if (seatsErrMsg) {
        seatsText = seatsErrMsg.code === 'count-range'
          ? 'De 0 a 350'
          : 'Número de escaños obligatorio';
      }

      const seatsNum = Number(group.seats || 0);
      const pct = (seatsNum / 350 * 100).toFixed(1);
      const isSelected = selectedSet.has(group.id);

      return `
        <tr data-id="${group.id}">
          <td>
            <div class="group-name-cell">
              <span class="group-swatch" style="background: ${color};" aria-hidden="true"></span>
              <div style="flex: 1;">
                <input type="text" class="group-label-input"
                  data-idx="${idx}"
                  value="${escapeHtml(group.label)}"
                  maxlength="60"
                  aria-label="Nombre del grupo ${idx + 1}"
                  aria-invalid="${hasLabelError ? 'true' : 'false'}"
                  ${hasLabelError ? `aria-describedby="err-label-${idx}"` : ''} />
                ${hasLabelError ? `<div id="err-label-${idx}" class="field-error">${labelText}</div>` : ''}
              </div>
            </div>
          </td>
          <td class="num-cell" style="min-width: 90px;">
            <input type="number" class="group-seats-input"
              data-idx="${idx}"
              value="${escapeHtml(group.rawSeats !== undefined ? group.rawSeats : group.seats)}"
              min="0" max="350"
              aria-label="Escaños para ${escapeHtml(group.label || 'Grupo ' + (idx + 1))}"
              aria-invalid="${hasSeatsError ? 'true' : 'false'}"
              ${hasSeatsError ? `aria-describedby="err-seats-${idx}"` : ''} />
            ${hasSeatsError ? `<div id="err-seats-${idx}" class="field-error">${seatsText}</div>` : ''}
          </td>
          <td class="num-cell" style="color: var(--color-text-secondary);">${pct}%</td>
          <td style="text-align: center;">
            <label class="simulator-checkbox-label">
              <input type="checkbox" class="group-select-checkbox"
                data-id="${group.id}"
                ${isSelected ? 'checked' : ''}
                aria-label="Sumar ${escapeHtml(group.label || 'Grupo')} a la coalición" />
            </label>
          </td>
          <td style="text-align: right;">
            <button type="button" class="simulator-danger group-remove-btn"
              data-idx="${idx}"
              aria-label="Eliminar ${escapeHtml(group.label || 'Grupo')}"
              ${state.groups.length <= 1 ? 'disabled title="Se requiere al menos un grupo"' : ''}>
              ✕
            </button>
          </td>
        </tr>
      `;
    }).join('\n');

    tbody.innerHTML = rowsHtml;
  }

  function update() {
    const calculation = engine.calculate(state.groups, state.selectedIds);
    renderHemicycle(calculation);
    renderSummary(calculation);
    renderTable(calculation);

    // Disable/enable Add button
    const addBtn = document.getElementById('simulator-add-group');
    if (addBtn) {
      addBtn.disabled = state.groups.length >= engine.limits.maxGroups;
    }
  }

  function escapeHtml(text) {
    if (text == null) return '';
    return String(text)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  function bindEvents() {
    const app = document.getElementById('simulator-app');
    if (!app) return;

    // Delegated input changes for table
    app.addEventListener('input', function (e) {
      const target = e.target;
      if (target.classList.contains('group-label-input')) {
        const idx = Number(target.dataset.idx);
        if (state.groups[idx]) {
          state.groups[idx].label = target.value;
          update();
        }
      } else if (target.classList.contains('group-seats-input')) {
        const idx = Number(target.dataset.idx);
        if (state.groups[idx]) {
          state.groups[idx].rawSeats = target.value;
          state.groups[idx].seats = target.value;
          update();
        }
      }
    });

    app.addEventListener('change', function (e) {
      const target = e.target;
      if (target.classList.contains('group-select-checkbox')) {
        const id = target.dataset.id;
        if (target.checked) {
          if (!state.selectedIds.includes(id)) state.selectedIds.push(id);
        } else {
          state.selectedIds = state.selectedIds.filter(x => x !== id);
        }
        update();
      }
    });

    app.addEventListener('click', function (e) {
      const target = e.target.closest('button');
      if (!target) return;

      if (target.classList.contains('group-remove-btn')) {
        const idx = Number(target.dataset.idx);
        if (state.groups.length > 1 && idx >= 0 && idx < state.groups.length) {
          const removed = state.groups.splice(idx, 1)[0];
          state.selectedIds = state.selectedIds.filter(id => id !== removed.id);
          announce('Grupo eliminado.');
          update();
        }
      }
    });

    // Add group button
    const addBtn = document.getElementById('simulator-add-group');
    if (addBtn) {
      addBtn.addEventListener('click', function () {
        if (state.groups.length >= engine.limits.maxGroups) return;
        const newGroup = {
          id: getUniqueId(),
          label: 'Grupo ' + (state.groups.length + 1),
          seats: '0',
          rawSeats: '0'
        };
        state.groups.push(newGroup);
        announce('Nuevo grupo añadido.');
        update();
        // Focus new row label
        setTimeout(() => {
          const inputs = document.querySelectorAll('.group-label-input');
          if (inputs.length) inputs[inputs.length - 1].focus();
        }, 50);
      });
    }

    // Reset button
    const resetBtn = document.getElementById('simulator-reset');
    if (resetBtn) {
      resetBtn.addEventListener('click', function () {
        state.groups = emptyGroups();
        state.selectedIds = [];
        announce('Escenario restablecido.');
        update();
      });
    }

    // Load sample button
    const sampleBtn = document.getElementById('simulator-sample');
    if (sampleBtn) {
      sampleBtn.addEventListener('click', function () {
        const profile = window.SimulatorProfile;
        if (profile && Array.isArray(profile.sample_groups) && profile.sample_groups.length) {
          state.groups = profile.sample_groups.map((g, idx) => ({
            id: g.id || ('g-' + (idx + 1)),
            label: g.label || ('Grupo ' + (idx + 1)),
            seats: String(g.seats || '0')
          }));
        } else {
          state.groups = defaultGroups();
        }
        state.selectedIds = [];
        announce('Ejemplo cargado.');
        update();
      });
    }

    // Share scenario button & copy link
    const shareBtn = document.getElementById('simulator-share-btn');
    const copyBtn = document.getElementById('simulator-copy-btn');
    const shareInput = document.getElementById('simulator-share-input');
    const shareFeedback = document.getElementById('simulator-share-feedback');

    async function copyToClipboard(url) {
      try {
        if (navigator.clipboard && navigator.clipboard.writeText) {
          await navigator.clipboard.writeText(url);
          if (shareFeedback) shareFeedback.textContent = 'Enlace copiado al portapapeles.';
        } else {
          throw new Error('Clipboard API no disponible');
        }
      } catch (_) {
        if (shareInput) {
          shareInput.value = url;
          shareInput.focus();
          shareInput.select();
        }
        if (shareFeedback) shareFeedback.textContent = 'Copia el enlace seleccionado arriba.';
      }
    }

    if (shareBtn) {
      shareBtn.addEventListener('click', async function () {
        const url = engine.stableSimulatorUrl(window.location.href, state.groups, state.selectedIds);
        if (shareInput) shareInput.value = url;

        if (window.isSecureContext && typeof navigator.share === 'function') {
          try {
            await navigator.share({
              title: 'Simulador de escaños y mayorías · Elecciones 2026',
              text: 'Simula combinaciones de escaños y mayorías de investidura en el Congreso.',
              url: url
            });
            if (shareFeedback) shareFeedback.textContent = 'Escenario compartido.';
            return;
          } catch (err) {
            // If user closed share sheet or failed, fall back to copy
            if (err.name !== 'AbortError') {
              await copyToClipboard(url);
            }
          }
        } else {
          await copyToClipboard(url);
        }
      });
    }

    if (copyBtn) {
      copyBtn.addEventListener('click', async function () {
        const url = engine.stableSimulatorUrl(window.location.href, state.groups, state.selectedIds);
        if (shareInput) shareInput.value = url;
        await copyToClipboard(url);
      });
    }
  }

  function init() {
    initFromUrlOrDefaults();
    bindEvents();
    update();
  }

  const api = Object.freeze({
    init,
    update,
    getState: () => state,
    setState: (newState) => { state = newState; update(); }
  });

  if (typeof module !== 'undefined' && module.exports) {
    module.exports = api;
  } else {
    root.SimulatorUI = api;
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', init);
    } else {
      init();
    }
  }
})(typeof globalThis !== 'undefined' ? globalThis : this);
