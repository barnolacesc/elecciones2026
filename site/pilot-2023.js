/* Private historical pilot. No analytics, persistence or inferred party positions. */
(async function () {
  'use strict';
  const nested = ['/cuestionario/', '/fuentes/', '/presupuestos/', '/simulador/', '/compromisos/'].some(p => location.pathname.includes(p));
  const response = await fetch((nested ? '../' : './') + 'pilot-2023-data.json', {cache: 'no-store'});
  if (!response.ok) return;
  const data = await response.json();
  if (data.election_id !== 'es-gen-2023' || data.status !== 'historical-provisional-private') return;
  const names = {pp: 'PP', erc: 'ERC', pnv: 'PNV', sumar: 'Sumar'};
  function element(tag, text, className) {
    const node = document.createElement(tag);
    node.textContent = text;
    if (className) node.className = className;
    return node;
  }
  function card(position, extraClass) {
    const className = extraClass ? `card ${extraClass}` : 'card';
    const article = element('article', '', className);
    article.append(element('span', names[position.party], 'party'));
    article.append(element('h3', position.title));
    article.append(element('p', position.summary));
    article.append(element('p', 'Matiz: ' + position.qualification, 'qualification'));
    const citation = element('p', '', 'citation');
    const link = element('a', 'Programa original, PDF pág. ' + position.page + ' (se abre en otra pestaña) ↗');
    link.href = position.url;
    link.target = '_blank'; link.rel = 'noopener noreferrer'; link.referrerPolicy = 'no-referrer';
    citation.append(link, element('span', position.locator, 'locator'));
    article.append(citation);
    return article;
  }
  function emptyCard(party) {
    const article = element('article', '', 'card card-empty');
    article.append(element('span', names[party], 'party'));
    article.append(element('h3', 'Sin propuesta registrada', 'empty-title'));
    article.append(element('p', 'No consta propuesta específica sobre esta medida en el extracto analizado del programa de 2023.', 'empty-note'));
    article.append(element('p', 'Matiz: Una medida ausente o no seleccionada no implica oposición.', 'qualification'));
    return article;
  }
  const topic = document.getElementById('pilot-topic');
  if (topic) {
    const a = document.getElementById('pilot-a');
    const b = document.getElementById('pilot-b');
    const target = document.getElementById('pilot-comparison');
    const error = document.getElementById('pilot-error');
    b.value = 'erc';
    const params = new URLSearchParams(location.search);
    if (data.topics.some(t => t.id === params.get('topic'))) topic.value = params.get('topic');
    if (names[params.get('partyA')]) a.value = params.get('partyA');
    if (names[params.get('partyB')]) b.value = params.get('partyB');
    function render() {
      target.replaceChildren();
      error.hidden = a.value !== b.value;
      for (const control of [a, b]) {
        if (error.hidden) {
          control.removeAttribute('aria-invalid');
          control.removeAttribute('aria-describedby');
        } else {
          control.setAttribute('aria-invalid', 'true');
          control.setAttribute('aria-describedby', 'pilot-error');
        }
      }
      if (!error.hidden) {
        // A copied address must never restore the previous valid comparison.
        const url = new URL(location.href);
        url.search = '';
        url.hash = '';
        history.replaceState({}, '', url);
        return;
      }
      const topicMeasures = [];
      for (const p of data.positions) {
        if (p.topic === topic.value && !topicMeasures.some(m => m.id === p.measure_id)) {
          topicMeasures.push({ id: p.measure_id, title: p.measure_title });
        }
      }
      const relevantMeasures = topicMeasures.filter(m =>
        data.positions.some(p => p.measure_id === m.id && (p.party === a.value || p.party === b.value))
      );
      if (relevantMeasures.length === 0) {
        target.append(element('p', 'Este piloto no incluye medidas para estas candidaturas en este tema. La ausencia no indica apoyo ni oposición.', 'empty-note'));
        const sources = element('a', 'Consultar fuentes y límites del piloto', 'button');
        sources.href = './fuentes/';
        target.append(sources);
      } else {
        for (const m of relevantMeasures) {
          const group = element('div', '', 'measure-group');
          group.append(element('h3', m.title, 'measure-title'));
          const cards = element('div', '', 'cards');
          for (const party of [a.value, b.value]) {
            const pos = data.positions.find(p => p.measure_id === m.id && p.party === party);
            if (pos) {
              cards.append(card(pos));
            } else {
              cards.append(emptyCard(party));
            }
          }
          group.append(cards);
          target.append(group);
        }
      }
      const url = new URL(location.href);
      url.search = new URLSearchParams({topic: topic.value, partyA: a.value, partyB: b.value}).toString();
      history.replaceState({}, '', url);
    }
    for (const control of [topic, a, b]) control.addEventListener('change', render);
    render();
  }
  const quiz = document.getElementById('pilot-quiz');
  if (quiz) {
    function shuffle(arr) {
      const copy = arr.slice();
      for (let i = copy.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [copy[i], copy[j]] = [copy[j], copy[i]];
      }
      return copy;
    }
    function selectQuestions(positions, targetPerParty = 3) {
      const selected = [];
      for (const partyKey of Object.keys(names)) {
        const partyPositions = positions.filter(p => p.party === partyKey);
        const shuffledParty = shuffle(partyPositions);
        selected.push(...shuffledParty.slice(0, Math.min(targetPerParty, partyPositions.length)));
      }
      return shuffle(selected);
    }
    const questions = selectQuestions(data.positions, 3);
    const answers = [];
    const results = document.getElementById('pilot-results');
    let index = 0;
    function showQuestion() {
      const position = questions[index];
      document.getElementById('pilot-progress').textContent = 'Propuesta ' + (index + 1) + ' de ' + questions.length;
      document.getElementById('pilot-question').textContent = data.topics.find(t => t.id === position.topic).name;
      document.getElementById('pilot-statement').textContent = position.summary;
      document.getElementById('pilot-next').textContent = index === questions.length - 1 ? 'Ver respuestas y fuentes' : 'Siguiente propuesta';
      quiz.reset();
      document.getElementById('pilot-answer-error').hidden = true;
    }
    showQuestion();
    function clearPoliticalState() {
      answers.length = 0;
      index = 0;
      quiz.hidden = false;
      results.replaceChildren();
      showQuestion();
    }
    window.addEventListener('pagehide', clearPoliticalState);
    window.addEventListener('pageshow', event => {
      if (event.persisted) clearPoliticalState();
    });
    quiz.addEventListener('submit', event => {
      event.preventDefault();
      const chosen = quiz.querySelector('input[name="answer"]:checked');
      if (!chosen) {
        document.getElementById('pilot-answer-error').hidden = false;
        return;
      }
      answers.push({position: questions[index], answer: chosen.value});
      index++;
      if (index < questions.length) { showQuestion(); return; }
      quiz.hidden = true;
      const labels = {
        'strongly-agree': 'Totalmente de acuerdo',
        'agree': 'Más bien de acuerdo',
        'somewhat-agree': 'Más bien de acuerdo',
        'neutral': 'Indiferente',
        'disagree': 'Más bien en desacuerdo',
        'somewhat-disagree': 'Más bien en desacuerdo',
        'strongly-disagree': 'Totalmente en desacuerdo'
      };

      const partyStats = Object.keys(names).map(partyKey => {
        const partyAnswers = answers.filter(a => a.position.party === partyKey);
        const supported = partyAnswers.filter(a => a.answer === 'strongly-agree' || a.answer === 'agree' || a.answer === 'somewhat-agree').length;
        const neutral = partyAnswers.filter(a => a.answer === 'neutral').length;
        const opposed = partyAnswers.filter(a => a.answer === 'strongly-disagree' || a.answer === 'disagree' || a.answer === 'somewhat-disagree').length;
        return {
          party: partyKey,
          name: names[partyKey],
          supported,
          neutral,
          opposed,
          total: partyAnswers.length
        };
      });

      partyStats.sort((a, b) => b.supported - a.supported || b.neutral - a.neutral || a.name.localeCompare(b.name, 'es'));

      const summaryCard = element('section', '', 'pilot-summary-card');
      summaryCard.append(element('h2', 'Resumen de resultados'));
      summaryCard.append(element('p', `Has valorado ${answers.length} propuestas a ciegas. Este es el número de medidas que has apoyado de cada candidatura:`, 'pilot-summary-lead'));

      const partyList = element('div', '', 'pilot-party-results');
      for (const p of partyStats) {
        const row = element('div', '', 'pilot-party-row');
        const info = element('div', '', 'pilot-party-info');
        info.append(element('span', p.name, 'pilot-party-name'));

        const badgeGroup = element('div', '', 'pilot-badge-group');
        if (p.supported > 0) {
          badgeGroup.append(element('span', `✓ ${p.supported} a favor`, 'pilot-badge pilot-badge-green'));
        }
        if (p.opposed > 0) {
          badgeGroup.append(element('span', `✕ ${p.opposed} en contra`, 'pilot-badge pilot-badge-red'));
        }
        if (p.neutral > 0) {
          badgeGroup.append(element('span', `– ${p.neutral} neutras`, 'pilot-badge pilot-badge-neutral'));
        }
        info.append(badgeGroup);
        row.append(info);

        const barContainer = element('div', '', 'pilot-bar-container');
        if (p.total > 0) {
          const supPct = Math.round((p.supported / p.total) * 100);
          const neuPct = Math.round((p.neutral / p.total) * 100);
          const oppPct = 100 - supPct - neuPct;
          if (supPct > 0) {
            const seg = element('div', '', 'pilot-bar-segment pilot-bar-green');
            seg.style.width = supPct + '%';
            seg.title = `${p.supported} a favor (${supPct}%)`;
            barContainer.append(seg);
          }
          if (neuPct > 0) {
            const seg = element('div', '', 'pilot-bar-segment pilot-bar-neutral');
            seg.style.width = neuPct + '%';
            seg.title = `${p.neutral} neutras (${neuPct}%)`;
            barContainer.append(seg);
          }
          if (oppPct > 0) {
            const seg = element('div', '', 'pilot-bar-segment pilot-bar-red');
            seg.style.width = oppPct + '%';
            seg.title = `${p.opposed} en contra (${oppPct}%)`;
            barContainer.append(seg);
          }
        }
        row.append(barContainer);

        partyList.append(row);
      }
      summaryCard.append(partyList);

      const shareSection = element('div', '', 'pilot-share-section');
      const actionGroup = element('div', '', 'pilot-actions-group');
      const shareBtn = element('button', 'Compartir el cuestionario', 'button pilot-share-btn');
      shareBtn.type = 'button';
      const retakeBtn = element('button', 'Repetir cuestionario', 'button button-secondary pilot-retake-btn');
      retakeBtn.type = 'button';
      retakeBtn.addEventListener('click', () => { window.location.reload(); });
      actionGroup.append(shareBtn, retakeBtn);

      const shareStatus = element('p', '', 'pilot-share-status');
      shareStatus.setAttribute('role', 'status');
      shareStatus.setAttribute('aria-live', 'polite');
      shareStatus.hidden = true;
      const shareUrl = new URL(location.href);
      shareUrl.search = '';
      shareUrl.hash = '';
      shareUrl.pathname = shareUrl.pathname.replace(/index\.html$/, '');
      const neutralUrl = shareUrl.toString();
      shareBtn.addEventListener('click', async () => {
        const payload = {
          title: 'Cuestionario exploratorio · Generales 2023',
          text: 'Consulta el cuestionario histórico privado y sus fuentes provisionales.',
          url: neutralUrl
        };
        if (navigator.share) {
          try {
            await navigator.share(payload);
            shareStatus.textContent = 'Enlace compartido.';
            shareStatus.hidden = false;
            return;
          } catch (err) {
            if (err.name === 'AbortError') return;
          }
        }
        if (navigator.clipboard && navigator.clipboard.writeText) {
          try {
            await navigator.clipboard.writeText(neutralUrl);
            shareStatus.textContent = 'Enlace copiado al portapapeles.';
            shareStatus.hidden = false;
            return;
          } catch (_) {}
        }
        shareStatus.textContent = 'Copia este enlace: ' + neutralUrl;
        shareStatus.hidden = false;
      });
      shareSection.append(actionGroup, shareStatus);
      summaryCard.append(shareSection);

      results.replaceChildren(summaryCard);
      results.append(element('h2', 'Tus respuestas y sus fuentes'));
      results.append(element('p', 'Consulta a continuación la candidatura de cada propuesta y el documento original de donde procede:', 'pilot-details-lead'));
      for (const {position, answer} of answers) {
        const isAgreed = answer === 'strongly-agree' || answer === 'agree' || answer === 'somewhat-agree';
        const isOpposed = answer === 'strongly-disagree' || answer === 'disagree' || answer === 'somewhat-disagree';
        const cardClass = isAgreed ? 'card-agreed' : isOpposed ? 'card-opposed' : 'card-neutral';
        const pillClass = isAgreed ? 'status-agreed' : isOpposed ? 'status-opposed' : 'status-neutral';
        const pillLabel = isAgreed ? '✓ A favor' : isOpposed ? '✕ En contra' : '– Indiferente';

        const section = element('section', '', 'result-topic');
        section.append(element('h3', data.topics.find(t => t.id === position.topic).name));

        const answerP = element('p', '', 'pilot-user-answer');
        const pill = element('span', pillLabel, `pilot-answer-pill ${pillClass}`);
        answerP.append(pill, document.createTextNode(' Tu respuesta: ' + labels[answer]));
        section.append(answerP);

        section.append(card(position, cardClass));
        results.append(section);
      }
      results.append(element('p', 'Estas respuestas no son un porcentaje de afinidad ni una recomendación de voto.'));
      results.focus();
    });
  }

  const topicFilter = document.getElementById('commitment-topic-filter');
  if (topicFilter) {
    const partyFilter = document.getElementById('commitment-party-filter');
    const statusFilter = document.getElementById('commitment-status-filter');
    const commitmentsGrid = document.getElementById('commitments-results');
    const commitmentsEmpty = document.getElementById('commitments-empty');

    if (commitmentsGrid && partyFilter && statusFilter) {
      function filterCommitments() {
        const selectedTopic = topicFilter.value;
        const selectedParty = partyFilter.value;
        const selectedStatus = statusFilter.value;
        let visibleCount = 0;

        const cards = commitmentsGrid.querySelectorAll('.commitment-card');
        for (const card of cards) {
          const matchTopic = selectedTopic === 'all' || card.dataset.topic === selectedTopic;
          const matchParty = selectedParty === 'all' || card.dataset.party === selectedParty;
          const matchStatus = selectedStatus === 'all' || card.dataset.status === selectedStatus;

          if (matchTopic && matchParty && matchStatus) {
            card.style.display = '';
            visibleCount++;
          } else {
            card.style.display = 'none';
          }
        }

        if (commitmentsEmpty) {
          commitmentsEmpty.style.display = visibleCount === 0 ? 'block' : 'none';
        }

        const params = new URLSearchParams(location.search);
        if (selectedTopic !== 'all') params.set('topic', selectedTopic); else params.delete('topic');
        if (selectedParty !== 'all') params.set('party', selectedParty); else params.delete('party');
        if (selectedStatus !== 'all') params.set('status', selectedStatus); else params.delete('status');
        const newQuery = params.toString();
        const newUrl = location.pathname + (newQuery ? '?' + newQuery : '');
        history.replaceState({}, '', newUrl);
      }

      const urlParams = new URLSearchParams(location.search);
      if (urlParams.get('topic') && Array.from(topicFilter.options).some(o => o.value === urlParams.get('topic'))) {
        topicFilter.value = urlParams.get('topic');
      }
      if (urlParams.get('party') && Array.from(partyFilter.options).some(o => o.value === urlParams.get('party'))) {
        partyFilter.value = urlParams.get('party');
      }
      if (urlParams.get('status') && Array.from(statusFilter.options).some(o => o.value === urlParams.get('status'))) {
        statusFilter.value = urlParams.get('status');
      }

      topicFilter.addEventListener('change', filterCommitments);
      partyFilter.addEventListener('change', filterCommitments);
      statusFilter.addEventListener('change', filterCommitments);
      filterCommitments();
    }
  }
})();
