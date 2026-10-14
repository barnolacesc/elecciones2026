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
      for (const party of [a.value, b.value]) {
        const position = data.positions.find(p => p.topic === topic.value && p.party === party);
        if (position) target.append(card(position));
      }
      const url = new URL(location.href);
      url.search = new URLSearchParams({topic: topic.value, partyA: a.value, partyB: b.value}).toString();
      history.replaceState({}, '', url);
    }
    for (const control of [topic, a, b]) control.addEventListener('change', render);
    render();
  }
  const quiz = document.getElementById('pilot-quiz');
  if (quiz) quiz.addEventListener('submit', event => {
    event.preventDefault();
    const results = document.getElementById('pilot-results');
    results.replaceChildren(element('h2', 'Tus medidas seleccionadas'));
    let count = 0;
    for (const topic of data.topics) {
      const chosen = quiz.querySelector('input[name="' + topic.id + '"]:checked');
      if (!chosen) continue;
      const position = data.positions.find(p => p.topic === topic.id && p.party === chosen.value);
      if (!position) continue;
      const section = element('section', '', 'result-topic');
      section.append(element('h3', topic.name));
      section.append(card(position));
      results.append(section); count++;
    }
    if (!count) results.append(element('p', 'Elige al menos una medida para ver sus fuentes.'));
    else results.append(element('p', 'Estas son tus elecciones, no un porcentaje de afinidad ni una recomendación de voto. Puedes cambiar las respuestas.'));
    results.focus();
  });
})();
