/* Private historical pilot. No analytics, persistence or inferred party positions. */
(async function () {
  'use strict';
  const nested = location.pathname.includes('/cuestionario/');
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
  function card(position) {
    const article = element('article', '', 'card');
    article.append(element('span', names[position.party], 'party'));
    article.append(element('h3', position.title));
    article.append(element('p', position.summary));
    article.append(element('p', 'Matiz: ' + position.qualification, 'qualification'));
    const citation = element('p', '', 'citation');
    const link = element('a', 'Programa original, PDF pág. ' + position.page + ' ↗');
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
      if (!error.hidden) return;
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
        target.append(element('p', 'No constan propuestas específicas para las candidaturas seleccionadas en este tema.', 'empty-note'));
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
    const questions = data.positions.slice();
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
      summaryCard.append(element('p', 'Has valorado 12 propuestas a ciegas. Este es el número de medidas que has apoyado de cada candidatura:', 'pilot-summary-lead'));

      const partyList = element('div', '', 'pilot-party-results');
      for (const p of partyStats) {
        const row = element('div', '', 'pilot-party-row');
        const info = element('div', '', 'pilot-party-info');
        info.append(element('span', p.name, 'pilot-party-name'));
        info.append(element('span', `${p.supported} de ${p.total} propuestas apoyadas`, 'pilot-party-count'));
        row.append(info);

        const barContainer = element('div', '', 'pilot-bar-container');
        const bar = element('div', '', 'pilot-bar-fill');
        bar.style.width = p.total > 0 ? Math.round((p.supported / p.total) * 100) + '%' : '0%';
        barContainer.append(bar);
        row.append(barContainer);

        partyList.append(row);
      }
      summaryCard.append(partyList);

      const shareSection = element('div', '', 'pilot-share-section');
      const shareBtn = element('button', 'Compartir mis resultados', 'button pilot-share-btn');
      shareBtn.type = 'button';
      const shareStatus = element('p', '', 'pilot-share-status');
      shareStatus.setAttribute('role', 'status');
      shareStatus.setAttribute('aria-live', 'polite');
      shareStatus.hidden = true;

      const shareUrl = window.location.href.split('#')[0];
      const shareLines = partyStats.map(p => `• ${p.name}: ${p.supported} de ${p.total} propuestas apoyadas`);
      const shareText = `Resultados de mi cuestionario de propuestas electorales a ciegas:\n${shareLines.join('\n')}\n\nHaz la prueba tú también en:\n${shareUrl}`;

      shareBtn.addEventListener('click', async () => {
        if (navigator.share) {
          try {
            await navigator.share({
              title: 'Mis resultados en el cuestionario de propuestas',
              text: shareText,
              url: shareUrl
            });
            return;
          } catch (err) {
            if (err.name === 'AbortError') return;
          }
        }
        if (navigator.clipboard && navigator.clipboard.writeText) {
          try {
            await navigator.clipboard.writeText(shareText);
            shareStatus.textContent = '¡Resultados copiados al portapapeles para compartir!';
            shareStatus.hidden = false;
            const originalText = shareBtn.textContent;
            shareBtn.textContent = '¡Copiado al portapapeles!';
            setTimeout(() => { shareBtn.textContent = originalText; }, 2500);
            return;
          } catch (_) {}
        }
        shareStatus.textContent = shareText;
        shareStatus.hidden = false;
      });
      shareSection.append(shareBtn, shareStatus);
      summaryCard.append(shareSection);

      results.replaceChildren(summaryCard);
      results.append(element('h2', 'Tus respuestas y sus fuentes'));
      results.append(element('p', 'Consulta a continuación la candidatura de cada propuesta y el documento original de donde procede:', 'pilot-details-lead'));
      for (const {position, answer} of answers) {
        const section = element('section', '', 'result-topic');
        section.append(element('h3', data.topics.find(t => t.id === position.topic).name));
        section.append(element('p', 'Tu respuesta: ' + labels[answer]));
        section.append(card(position));
        results.append(section);
      }
      results.append(element('p', 'Estas respuestas no son un porcentaje de afinidad ni una recomendación de voto.'));
      results.focus();
    });
  }
})();
