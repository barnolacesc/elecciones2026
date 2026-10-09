/**
 * Elecciones 2026 — Public Comparison & Selection Interaction
 * Pure vanilla JavaScript with zero external CDN dependencies.
 * Compliant with WCAG 2.2 AA (touch/keyboard accessible).
 * Handles:
 *  - One-topic and two-party selection validation (rejects identical parties).
 *  - URL query state synchronization and deep linking (?topic=...&partyA=...&partyB=...).
 *  - Neutral copy and native share fallback.
 *  - Strict zero visitor profiles, no data collection.
 */

(function () {
  'use strict';

  // 8 Core topics defined in taxonomy 1.0.0
  const TOPICS = {
    'housing': {
      id: 'housing',
      name: 'Vivienda',
      measureTitle: 'Medida: Parque público y alquiler asequible',
      description: 'Políticas de impulso a la oferta de vivienda en régimen de alquiler social y regulación.'
    },
    'education': {
      id: 'education',
      name: 'Educación',
      measureTitle: 'Medida: Financiación escolar y ratios de aula',
      description: 'Políticas de financiación del sistema educativo, centros concertados y plazas públicas.'
    },
    'health-social-services': {
      id: 'health-social-services',
      name: 'Sanidad y servicios sociales',
      measureTitle: 'Medida: Refuerzo de la atención primaria y reducción de listas de espera',
      description: 'Inversión en el Sistema Nacional de Salud, dotación de personal y cobertura de salud mental.'
    },
    'economy-work-tax': {
      id: 'economy-work-tax',
      name: 'Economía, trabajo y fiscalidad',
      measureTitle: 'Medida: Regulación de la jornada laboral y salario mínimo',
      description: 'Políticas laborales, incentivos fiscales y sostenibilidad del sistema de pensiones.'
    },
    'immigration': {
      id: 'immigration',
      name: 'Inmigración',
      measureTitle: 'Medida: Canales de regularización y centros de acogida',
      description: 'Gestión de flujos migratorios, procedimientos de asilo y cooperación en origen.'
    },
    'foreign-policy-eu': {
      id: 'foreign-policy-eu',
      name: 'Política exterior y UE',
      measureTitle: 'Medida: Compromisos presupuestarios y tratados de la Unión Europea',
      description: 'Cumplimiento de objetivos de gasto en defensa y acuerdos comunitarios.'
    },
    'climate-energy': {
      id: 'climate-energy',
      name: 'Clima y energía',
      measureTitle: 'Medida: Calendario de descarbonización y despliegue renovable',
      description: 'Transición energética, infraestructura de red y gestión de recursos hídricos.'
    },
    'institutions-rights': {
      id: 'institutions-rights',
      name: 'Instituciones, justicia y derechos fundamentales',
      measureTitle: 'Medida: Modelo territorial y gobernanza judicial',
      description: 'Reformas institucionales, sistema de elección del CGPJ y libertades públicas.'
    }
  };

  // Qualified candidacies and test fixtures
  const PARTIES = {
    'party-a': {
      id: 'party-a',
      name: 'Partido A',
      shortName: 'Partido A',
      pill: 'A',
      pillClass: 'party-pill-a',
      status: 'official',
      statusLabel: 'Programa de ejemplo',
      statement: 'Esta tarjeta muestra una propuesta concreta, resumida de forma neutral y revisada por el equipo editorial.',
      caveat: 'Se registrarán aquí condiciones de financiación, plazos o ámbito competencial.',
      source: 'Programa de ejemplo v1.0 · pág. 12',
      date: 'Rev. pendiente'
    },
    'party-b': {
      id: 'party-b',
      name: 'Partido B',
      shortName: 'Partido B',
      pill: 'B',
      pillClass: 'party-pill-b',
      status: 'official',
      statusLabel: 'Programa de ejemplo',
      statement: 'La segunda propuesta aparece en paralelo con idéntico espacio, rigor descriptivo y trazabilidad a la fuente original.',
      caveat: 'Toda exclusión o requisito particular quedará reflejado de manera explícita.',
      source: 'Programa de ejemplo v1.0 · pág. 24',
      date: 'Rev. pendiente'
    },
    'bng': {
      id: 'bng',
      name: 'Bloque Nacionalista Galego (BNG)',
      shortName: 'BNG',
      pill: 'BNG',
      pillClass: 'party-pill-a',
      status: 'missing',
      statusLabel: 'Programa no disponible',
      statement: 'El programa oficial para las elecciones generales de 2026 aún no ha sido publicado por la candidatura.',
      caveat: 'Ámbito territorial: Galicia. Seguimiento activo en el registro oficial de fuentes.',
      source: 'Registro oficial de fuentes (src-2026-bng-v0)',
      date: '09/10/2026'
    },
    'ehbildu': {
      id: 'ehbildu',
      name: 'EH Bildu (Euskal Herria Bildu)',
      shortName: 'EH Bildu',
      pill: 'EHB',
      pillClass: 'party-pill-b',
      status: 'missing',
      statusLabel: 'Programa no disponible',
      statement: 'El programa oficial para las elecciones generales de 2026 aún no ha sido publicado por la candidatura.',
      caveat: 'Ámbito territorial: País Vasco y Navarra. Seguimiento activo.',
      source: 'Registro oficial de fuentes (src-2026-ehbildu-v0)',
      date: '09/10/2026'
    },
    'erc': {
      id: 'erc',
      name: 'Esquerra Republicana de Catalunya (ERC)',
      shortName: 'ERC',
      pill: 'ERC',
      pillClass: 'party-pill-a',
      status: 'missing',
      statusLabel: 'Programa no disponible',
      statement: 'El programa oficial para las elecciones generales de 2026 aún no ha sido publicado por la candidatura.',
      caveat: 'Ámbito territorial: Cataluña. Seguimiento activo en el registro oficial de fuentes.',
      source: 'Registro oficial de fuentes (src-2026-erc-v0)',
      date: '09/10/2026'
    },
    'junts': {
      id: 'junts',
      name: 'Junts per Catalunya',
      shortName: 'Junts',
      pill: 'JUN',
      pillClass: 'party-pill-b',
      status: 'missing',
      statusLabel: 'Programa no disponible',
      statement: 'El programa oficial para las elecciones generales de 2026 aún no ha sido publicado por la candidatura.',
      caveat: 'Ámbito territorial: Cataluña. Seguimiento activo.',
      source: 'Registro oficial de fuentes (src-2026-junts-v0)',
      date: '09/10/2026'
    },
    'pnv': {
      id: 'pnv',
      name: 'EAJ-PNV (Partido Nacionalista Vasco)',
      shortName: 'EAJ-PNV',
      pill: 'PNV',
      pillClass: 'party-pill-a',
      status: 'missing',
      statusLabel: 'Programa no disponible',
      statement: 'El programa oficial para las elecciones generales de 2026 aún no ha sido publicado por la candidatura.',
      caveat: 'Ámbito territorial: País Vasco y Navarra. Seguimiento activo.',
      source: 'Registro oficial de fuentes (src-2026-pnv-v0)',
      date: '09/10/2026'
    },
    'pp': {
      id: 'pp',
      name: 'Partido Popular (PP)',
      shortName: 'PP',
      pill: 'PP',
      pillClass: 'party-pill-b',
      status: 'missing',
      statusLabel: 'Programa no disponible',
      statement: 'El programa oficial para las elecciones generales de 2026 aún no ha sido publicado por la candidatura.',
      caveat: 'Seguimiento activo en el registro oficial de fuentes.',
      source: 'Registro oficial de fuentes (src-2026-pp-v0)',
      date: '09/10/2026'
    },
    'psoe': {
      id: 'psoe',
      name: 'Partido Socialista Obrero Español (PSOE)',
      shortName: 'PSOE',
      pill: 'PSOE',
      pillClass: 'party-pill-a',
      status: 'missing',
      statusLabel: 'Programa no disponible',
      statement: 'El programa oficial para las elecciones generales de 2026 aún no ha sido publicado por la candidatura.',
      caveat: 'Seguimiento activo en el registro oficial de fuentes.',
      source: 'Registro oficial de fuentes (src-2026-psoe-v0)',
      date: '09/10/2026'
    },
    'sumar': {
      id: 'sumar',
      name: 'Movimiento Sumar',
      shortName: 'Sumar',
      pill: 'SUM',
      pillClass: 'party-pill-b',
      status: 'missing',
      statusLabel: 'Programa no disponible',
      statement: 'El programa oficial para las elecciones generales de 2026 aún no ha sido publicado por la candidatura.',
      caveat: 'Seguimiento activo en el registro oficial de fuentes.',
      source: 'Registro oficial de fuentes (src-2026-sumar-v0)',
      date: '09/10/2026'
    },
    'vox': {
      id: 'vox',
      name: 'VOX',
      shortName: 'VOX',
      pill: 'VOX',
      pillClass: 'party-pill-a',
      status: 'missing',
      statusLabel: 'Programa no disponible',
      statement: 'El programa oficial para las elecciones generales de 2026 aún no ha sido publicado por la candidatura.',
      caveat: 'Seguimiento activo en el registro oficial de fuentes.',
      source: 'Registro oficial de fuentes (src-2026-vox-v0)',
      date: '09/10/2026'
    }
  };

  function init() {
    const form = document.getElementById('selection-form');
    const topicSelect = document.getElementById('topic-select');
    const partyASelect = document.getElementById('party-a-select');
    const partyBSelect = document.getElementById('party-b-select');
    const errorEl = document.getElementById('selection-error');
    const shareBtn = document.getElementById('share-button');
    const shareFeedback = document.getElementById('share-feedback');

    if (!form || !topicSelect || !partyASelect || !partyBSelect || !errorEl) {
      return;
    }

    // Parse URL query parameters if present (for deep linking / restoring selection)
    const urlParams = new URLSearchParams(window.location.search);
    const initialTopic = urlParams.get('topic');
    const initialPartyA = urlParams.get('partyA');
    const initialPartyB = urlParams.get('partyB');

    if (initialTopic && TOPICS[initialTopic]) {
      topicSelect.value = initialTopic;
    }
    if (initialPartyA && PARTIES[initialPartyA]) {
      partyASelect.value = initialPartyA;
    }
    if (initialPartyB && PARTIES[initialPartyB]) {
      partyBSelect.value = initialPartyB;
    }

    function validateSelection() {
      const partyA = partyASelect.value;
      const partyB = partyBSelect.value;

      if (partyA === partyB) {
        errorEl.textContent = 'Por favor, selecciona dos candidaturas distintas para realizar la comparación.';
        errorEl.classList.remove('sr-only');
        partyASelect.setAttribute('aria-invalid', 'true');
        partyBSelect.setAttribute('aria-invalid', 'true');
        return false;
      }

      errorEl.textContent = '';
      errorEl.classList.add('sr-only');
      partyASelect.removeAttribute('aria-invalid');
      partyBSelect.removeAttribute('aria-invalid');
      return true;
    }

    function renderComparison() {
      const isValid = validateSelection();
      if (!isValid) {
        return;
      }

      const topicKey = topicSelect.value;
      const partyAKey = partyASelect.value;
      const partyBKey = partyBSelect.value;

      const topicData = TOPICS[topicKey] || TOPICS['housing'];
      const partyAData = PARTIES[partyAKey] || PARTIES['party-a'];
      const partyBData = PARTIES[partyBKey] || PARTIES['party-b'];

      // Update topic head
      const topicLabelEl = document.getElementById('measure-topic-label');
      const measureTitleEl = document.getElementById('measure-1-title');
      const measureSummaryEl = document.getElementById('measure-summary');

      if (topicLabelEl) {
        topicLabelEl.textContent = 'TEMA: ' + topicData.name.toUpperCase();
      }
      if (measureTitleEl) {
        measureTitleEl.textContent = topicData.measureTitle;
      }
      if (measureSummaryEl) {
        measureSummaryEl.textContent = topicData.description;
      }

      // Update Party A card
      const partyANameEl = document.getElementById('party-a-name');
      const partyAPillEl = document.getElementById('party-pill-a');
      const partyAStatusEl = document.getElementById('party-a-status');
      const partyAStatementEl = document.getElementById('party-a-statement');
      const partyACaveatEl = document.getElementById('party-a-caveat');
      const partyASourceEl = document.getElementById('party-a-source');
      const partyADateEl = document.getElementById('party-a-date');

      if (partyANameEl) partyANameEl.textContent = partyAData.name;
      if (partyAPillEl) partyAPillEl.textContent = partyAData.pill;
      if (partyAStatusEl) {
        partyAStatusEl.className = 'status-badge status-badge-' + partyAData.status;
        partyAStatusEl.textContent = partyAData.statusLabel;
      }
      if (partyAStatementEl) partyAStatementEl.textContent = partyAData.statement;
      if (partyACaveatEl) {
        partyACaveatEl.innerHTML = '<strong>Matiz o condición:</strong> ' + partyAData.caveat;
      }
      if (partyASourceEl) partyASourceEl.textContent = 'Fuente: ' + partyAData.source;
      if (partyADateEl) {
        partyADateEl.textContent = partyAData.date;
        partyADateEl.setAttribute('datetime', '2026-10-09');
      }

      // Update Party B card
      const partyBNameEl = document.getElementById('party-b-name');
      const partyBPillEl = document.getElementById('party-pill-b');
      const partyBStatusEl = document.getElementById('party-b-status');
      const partyBStatementEl = document.getElementById('party-b-statement');
      const partyBCaveatEl = document.getElementById('party-b-caveat');
      const partyBSourceEl = document.getElementById('party-b-source');
      const partyBDateEl = document.getElementById('party-b-date');

      if (partyBNameEl) partyBNameEl.textContent = partyBData.name;
      if (partyBPillEl) partyBPillEl.textContent = partyBData.pill;
      if (partyBStatusEl) {
        partyBStatusEl.className = 'status-badge status-badge-' + partyBData.status;
        partyBStatusEl.textContent = partyBData.statusLabel;
      }
      if (partyBStatementEl) partyBStatementEl.textContent = partyBData.statement;
      if (partyBCaveatEl) {
        partyBCaveatEl.innerHTML = '<strong>Matiz o condición:</strong> ' + partyBData.caveat;
      }
      if (partyBSourceEl) partyBSourceEl.textContent = 'Fuente: ' + partyBData.source;
      if (partyBDateEl) {
        partyBDateEl.textContent = partyBData.date;
        partyBDateEl.setAttribute('datetime', '2026-10-09');
      }

      // Update analysis callout
      const analysisTitleEl = document.getElementById('analysis-title');
      const analysisTextEl = document.getElementById('analysis-text');

      if (analysisTitleEl && analysisTextEl) {
        if (partyAData.status === 'missing' || partyBData.status === 'missing') {
          analysisTitleEl.textContent = 'Posición pendiente de publicación';
          analysisTextEl.textContent =
            'Al menos una de las candidaturas seleccionadas no ha publicado aún su programa definitivo para 2026. «No consta» no implica oposición política.';
        } else {
          analysisTitleEl.textContent = 'Coincidencias y diferencias';
          analysisTextEl.textContent =
            'Solo se publicarán relaciones revisadas entre propuestas concretas. «No consta» nunca se interpretará como oposición política.';
        }
      }

      // Update URL query parameters without reloading
      if (window.history && window.history.replaceState) {
        const newUrl = new URL(window.location.href);
        newUrl.searchParams.set('topic', topicKey);
        newUrl.searchParams.set('partyA', partyAKey);
        newUrl.searchParams.set('partyB', partyBKey);
        window.history.replaceState({}, '', newUrl.toString());
      }
    }

    // Attach form and select listeners
    topicSelect.addEventListener('change', renderComparison);
    partyASelect.addEventListener('change', renderComparison);
    partyBSelect.addEventListener('change', renderComparison);

    form.addEventListener('submit', function (evt) {
      evt.preventDefault();
      renderComparison();
    });

    // Share button handler (native Web Share or clipboard fallback)
    if (shareBtn) {
      shareBtn.addEventListener('click', function () {
        const currentUrl = window.location.href;
        const topicName = (TOPICS[topicSelect.value] || {}).name || 'Vivienda';
        const partyAName = (PARTIES[partyASelect.value] || {}).shortName || 'Partido A';
        const partyBName = (PARTIES[partyBSelect.value] || {}).shortName || 'Partido B';

        const shareData = {
          title: 'Elecciones 2026 · Comparador de programas',
          text: 'Compara las propuestas de ' + partyAName + ' y ' + partyBName + ' sobre ' + topicName + ' con fuentes directas.',
          url: currentUrl
        };

        if (navigator.share && typeof navigator.share === 'function') {
          navigator.share(shareData).catch(function () {
            // User cancelled or unsupported share target; fall back to clipboard
            copyToClipboard(currentUrl);
          });
        } else {
          copyToClipboard(currentUrl);
        }
      });
    }

    function copyToClipboard(text) {
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(showFeedback, function () {
          fallbackPrompt(text);
        });
      } else {
        fallbackPrompt(text);
      }
    }

    function showFeedback() {
      if (!shareFeedback) return;
      shareFeedback.textContent = 'Enlace copiado al portapapeles';
      shareFeedback.classList.remove('sr-only');
      setTimeout(function () {
        shareFeedback.classList.add('sr-only');
        shareFeedback.textContent = '';
      }, 3000);
    }

    function fallbackPrompt(text) {
      window.prompt('Copia este enlace para compartir la comparación:', text);
    }

    // Run initial rendering
    renderComparison();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
