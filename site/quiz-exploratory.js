(function() {
  'use strict';
  const bundle = window.QuizExploratoryBundle;
  if (!bundle || !Array.isArray(bundle.topics)) return;
  const topics = bundle.topics;

  const panel = document.getElementById('topics');
  const results = document.getElementById('results');
  const finish = document.getElementById('finish');
  const status = document.getElementById('status');
  const form = document.getElementById('exploratory-form');
  const drawBtn = document.getElementById('draw');
  const redrawResultsBtn = document.getElementById('redraw-results');
  const editBtn = document.getElementById('edit');

  function selection(bank, randomIndex) {
    return bank.map(topic => {
      const first = randomIndex(topic.items.length);
      const other = randomIndex(topic.items.length - 1);
      const second = other >= first ? other + 1 : other;
      return { id: topic.id, name: topic.name, items: [topic.items[first], topic.items[second]] };
    });
  }

  function randomIndex(size) {
    const array = new Uint32Array(1);
    const limit = 2 ** 32 - (2 ** 32 % size);
    do crypto.getRandomValues(array); while (array[0] >= limit);
    return array[0] % size;
  }

  function element(tag, text) {
    const node = document.createElement(tag);
    if (text !== undefined && text !== null) node.textContent = text;
    return node;
  }

  const choices = [
    'Totalmente a favor', 'Más bien a favor', 'Ni a favor ni en contra',
    'Más bien en contra', 'Totalmente en contra', 'Omitir'
  ];

  const answers = new Map();
  let last = '';
  let batch = [];

  function draw({ focusAnswers = false } = {}) {
    let key;
    let attempts = 0;
    do {
      batch = selection(topics, randomIndex);
      key = batch.map(t => t.items.map(i => i.id).sort().join(',')).join('/');
      attempts++;
    } while (key === last && attempts < 10);
    last = key;
    answers.clear();
    render();
    if (focusAnswers) panel?.querySelector('input')?.focus();
  }

  function render() {
    if (results) results.hidden = true;
    const resultItems = document.getElementById('result-items');
    if (resultItems) resultItems.replaceChildren();
    if (panel) {
      panel.hidden = false;
      panel.replaceChildren(...batch.map(topic => {
        const section = element('section', '');
        section.className = 'exploratory-topic-section';
        section.append(element('h2', topic.name));
        for (const item of topic.items) {
          const fieldset = element('fieldset', '');
          fieldset.className = 'exploratory-item';
          fieldset.dataset.item = item.id;
          const legend = element('legend', item.statement);
          fieldset.append(legend);

          if (item.context && item.context.text) {
            const subtitle = element('p', item.context.text);
            subtitle.className = 'exploratory-context';
            subtitle.id = item.id + '-context';
            fieldset.setAttribute('aria-describedby', subtitle.id);
            fieldset.append(subtitle);
          }

          if (item.qualifications && item.qualifications.length > 0) {
            for (const condition of item.qualifications) {
              const note = element('p', condition);
              note.className = 'condition';
              fieldset.append(note);
            }
          }

          const optionsGrid = element('div', '');
          optionsGrid.className = 'exploratory-options-grid';
          for (const option of choices) {
            const label = element('label', '');
            label.className = 'quiz-answer exploratory-answer';
            const input = element('input', '');
            input.type = 'radio';
            input.name = item.id;
            input.autocomplete = 'off';
            input.value = option;
            input.checked = answers.get(item.id) === option;
            input.addEventListener('change', () => answers.set(item.id, option));
            const span = element('span', option);
            label.append(input, span);
            optionsGrid.append(label);
          }
          fieldset.append(optionsGrid);

          if (item.context && item.context.references && item.context.references.length > 0) {
            const references = element('details', '');
            references.className = 'exploratory-references';
            references.append(element('summary', 'Fuente de la situación actual'));
            if (item.context.period) references.append(element('p', 'Periodo: ' + item.context.period));
            if (item.context.reference_date) {
              references.append(element('p', 'Verificado el ' + item.context.reference_date.split('-').reverse().join('/')));
            }
            const list = element('ul', '');
            for (const reference of item.context.references) {
              const li = element('li', '');
              const link = element('a', reference.label);
              link.href = reference.url;
              link.target = '_blank';
              link.rel = 'noopener noreferrer';
              li.append(link);
              list.append(li);
            }
            references.append(list);
            fieldset.append(references);
          }
          section.append(fieldset);
        }
        return section;
      }));
    }
    if (form) form.hidden = false;
    if (finish) finish.hidden = false;
    if (status) status.textContent = '24 enunciados en 12 temas';
  }

  function showResults() {
    if (panel) panel.hidden = true;
    if (finish) finish.hidden = true;
    if (form) form.hidden = true;
    if (status) status.textContent = 'Respuestas completadas · Fuentes consultables';
    const resultItems = document.getElementById('result-items');
    if (!resultItems) return;
    resultItems.replaceChildren(...batch.map(topic => {
      const section = element('section', '');
      section.className = 'result-topic-group';
      section.append(element('h3', topic.name));
      for (const item of topic.items) {
        const article = element('article', '');
        article.className = 'result-item-card';
        article.dataset.item = item.id;
        article.append(element('h4', item.statement));
        if (item.qualifications && item.qualifications.length > 0) {
          for (const condition of item.qualifications) {
            const note = element('p', condition);
            note.className = 'condition';
            article.append(note);
          }
        }
        const choice = answers.get(item.id);
        const choiceText = choice === 'Omitir' ? 'Omitida' : (choice || 'Sin responder');
        const answerP = element('p', '');
        answerP.className = 'result-user-answer';
        answerP.append(element('span', 'Tu respuesta: '));
        const strongChoice = element('strong', choiceText);
        answerP.append(strongChoice);
        article.append(answerP);

        const sourceBlock = element('div', '');
        sourceBlock.className = 'result-source-block';
        const sourceLabel = element('p', 'Propuesta incluida en el programa de:');
        sourceLabel.className = 'result-source-label';
        sourceBlock.append(sourceLabel);

        const link = element('a', item.source.publisher + ' · página ' + item.source.page + ' ↗');
        link.className = 'programme-link';
        link.href = item.source.url;
        link.target = '_blank';
        link.rel = 'noopener noreferrer';
        sourceBlock.append(link);

        if (item.source.verified_external_copy) {
          const copy = element('a', 'Copia verificada del PDF · página ' + item.source.page + ' ↗');
          copy.className = 'programme-copy-link';
          copy.href = item.source.verified_external_copy;
          copy.target = '_blank';
          copy.rel = 'noopener noreferrer';
          const copyP = element('p', '');
          copyP.append(copy);
          sourceBlock.append(copyP);
        }
        article.append(sourceBlock);
        section.append(article);
      }
      return section;
    }));
    if (results) {
      results.hidden = false;
      const heading = document.getElementById('results-heading');
      if (heading) heading.focus();
    }
    window.scrollTo({top: 0, behavior: 'smooth'});
  }

  if (drawBtn) drawBtn.addEventListener('click', () => draw());
  if (redrawResultsBtn) {
    redrawResultsBtn.addEventListener('click', () => draw({ focusAnswers: true }));
  }
  if (finish) finish.addEventListener('click', showResults);
  if (editBtn) {
    editBtn.addEventListener('click', () => {
      render();
      if (panel) {
        const firstInput = panel.querySelector('fieldset input');
        if (firstInput) firstInput.focus();
      }
    });
  }

  window.addEventListener('pageshow', event => {
    if (event.persisted) draw();
  });

  draw();
})();
