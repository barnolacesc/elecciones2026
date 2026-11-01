/* Spanish quiz flow. Political state exists only in this document's memory. */
(function () {
  'use strict';
  const app = document.getElementById('quiz-app');
  const status = document.getElementById('quiz-status');
  const bundle = window.QuizBundle;
  const engine = window.QuizEngine;
  const labels = ['Totalmente en desacuerdo', 'Más bien en desacuerdo',
    'Ni de acuerdo ni en desacuerdo', 'Más bien de acuerdo', 'Totalmente de acuerdo'];
  let state;

  function node(tag, text, attributes = {}) {
    const element = document.createElement(tag);
    if (text != null) element.textContent = text;
    for (const [key, value] of Object.entries(attributes)) element.setAttribute(key, value);
    return element;
  }
  function button(text, action, attributes = {}) {
    const element = node('button', text, {type: 'button', ...attributes});
    element.addEventListener('click', action);
    return element;
  }
  function reset() {
    state = {stage: 'intro', index: 0, answers: {}, visited: new Set(), weights: {}, previous: null};
  }
  function announce(message) { status.textContent = message; }
  function heading(text) { app.append(node('h1', text, {tabindex: '-1'})); }
  function paragraph(text) { app.append(node('p', text)); }
  function navigate(stage, index = state.index) {
    if (stage !== 'result' && state.stage === 'result') {
      state.previous = Object.fromEntries(engine.calculate(bundle, state.answers, state.weights).parties
        .filter(p => p.eligible).map(p => [p.id, p.score]));
    }
    state.stage = stage; state.index = index;
    render();
  }
  function actions(...controls) {
    const group = node('div', null, {class: 'quiz-actions'});
    group.append(...controls); app.append(group);
  }
  function sources(item, parent, headingLevel = 2) {
    const details = node('details');
    details.append(node('summary', 'Ver posiciones y fuentes'));
    for (const party of bundle.parties) {
      const mapping = party.positions[bundle.items.indexOf(item)];
      const card = node('div', null, {class: 'quiz-source'});
      card.append(node(`h${headingLevel}`, party.name));
      if (mapping.value === null) card.append(node('p', mapping.reason));
      else {
        card.append(node('p', `${mapping.value === 1 ? 'A favor' : 'En contra'}${bundle.mode === 'mock' ? ' (dato ficticio)' : ''}`));
        const source = mapping.source;
        if (!source) card.append(node('p', 'Datos de prueba. No hay un documento político ni una revisión editorial.'));
        else {
          card.append(node('p', source.summary));
          for (const qualification of source.qualifications) card.append(node('p', qualification));
          card.append(node('p', `Programa ${source.programme_id}, versión ${source.version}. Página: ${source.page || '—'}. Sección: ${source.section || '—'}. Revisión: ${source.review_date}.`));
          card.append(node('p', `SHA-256: ${source.sha256}`));
          card.append(node('a', 'Abrir fuente oficial (ventana nueva)',
            {href: source.url, target: '_blank', rel: 'noopener noreferrer', referrerpolicy: 'no-referrer'}));
          card.append(node('p', 'La fuente externa tiene su propia política de privacidad.'));
        }
      }
      details.append(card);
    }
    parent.append(details);
  }
  function intro() {
    heading('Explora la coincidencia, pregunta a pregunta');
    paragraph('16 preguntas, 8 temas. Puedes omitir cualquiera y cambiar tus respuestas.');
    paragraph('Las respuestas quedan solo en la memoria de esta pestaña. Al salir o recargar se borran. No hay cuentas ni envío de respuestas.');
    paragraph('El resultado muestra coincidencia con las medidas respondidas. No recomienda a quién votar.');
    if (bundle.mode === 'mock') paragraph('Esta demostración sirve para probar el funcionamiento. Los temas son reales; las preguntas y los ejemplos son ficticios.');
    actions(button('Empezar', () => navigate('question', 0), {class: 'quiz-primary'}),
      button('Consultar método y cobertura', openMethod));
  }
  function openMethod() {
    const method = document.getElementById('quiz-method');
    method.open = true; method.querySelector('summary').focus();
  }
  function question() {
    const item = bundle.items[state.index];
    const topic = bundle.topics.find(t => t.id === item.topic_id);
    app.append(node('p', `${topic.name} · Pregunta ${state.index + 1} de 16`, {class: 'quiz-kicker'}));
    heading(item.text);
    const progress = node('progress', null, {value: state.index + 1, max: 16,
      'aria-label': `Pregunta ${state.index + 1} de 16`}); app.append(progress);
    for (const qualification of item.qualifications) paragraph(qualification);
    const fieldset = node('fieldset'); fieldset.append(node('legend', 'Elige una respuesta'));
    labels.forEach((label, index) => {
      const value = index / 2 - 1;
      const wrapper = node('label', null, {class: 'quiz-answer'});
      const input = node('input', null, {type: 'radio', name: 'quiz-answer', value,
        'aria-label': label});
      input.checked = state.answers[item.id] === value;
      input.addEventListener('change', () => { state.answers[item.id] = value; state.visited.add(item.id); });
      wrapper.append(input, node('span', label)); fieldset.append(wrapper);
    });
    app.append(fieldset);
    sources(item, app);
    const next = () => {
      state.visited.add(item.id);
      if (state.answers[item.id] === undefined) state.answers[item.id] = null;
      if (state.index === 15) finish();
      else navigate('question', state.index + 1);
    };
    actions(button('Anterior', () => navigate(state.index === 0 ? 'intro' : 'question', Math.max(0, state.index - 1))),
      button('No lo sé / Omitir', () => { state.answers[item.id] = null; next(); }),
      button(state.index === 15 ? 'Ver resultado' : 'Siguiente', next, {class: 'quiz-primary'}));
    paragraph('Las preguntas sin responder se contarán como omitidas. Puedes revisar tus respuestas si lo deseas.');
    actions(button('Revisar respuestas', () => navigate('review')),
      ...(state.index === 15 ? [] : [button('Ver resultado', finish)]));
  }
  function finish() {
    for (const item of bundle.items) if (state.answers[item.id] === undefined) state.answers[item.id] = null;
    navigate('result');
  }
  function review() {
    heading('Revisa tus respuestas');
    paragraph('Puedes cambiar cualquier respuesta. Al continuar, las preguntas sin responder se contarán como omitidas.');
    const list = node('ol', null, {class: 'quiz-review'});
    bundle.items.forEach((item, index) => {
      const value = state.answers[item.id];
      const description = value == null ? (state.visited.has(item.id) ? 'Omitida' : 'Sin responder') : labels[value * 2 + 2];
      const li = node('li');
      li.append(node('p', `${index + 1}. ${bundle.topics.find(t => t.id === item.topic_id).name}`),
        node('p', description), button(`Cambiar pregunta ${index + 1}`, () => navigate('question', index)));
      list.append(li);
    });
    app.append(list);
    actions(button('Volver a las preguntas', () => navigate('question')),
      button('Continuar y ver resultado', finish, {class: 'quiz-primary'}));
  }
  function decimal(value) { return value.toLocaleString('es-ES', {maximumFractionDigits: 1}); }
  function resultDetails(party, card) {
    const details = node('details'); details.append(node('summary', `Por qué aparece el porcentaje de ${party.name}`));
    for (const topic of party.contributions) {
      details.append(node('h3', `${topic.name} · ${topic.weight === 1 ? 'peso normal' : 'doble peso'}`));
      if (!topic.count) details.append(node('p', 'Tema sin respuestas: no cuenta en este porcentaje.'));
      else {
        details.append(node('p', `Has respondido ${topic.count} de las 2 preguntas de este tema. Su coincidencia media es ${decimal(topic.mean * 100)} %.`));
        details.append(node('p', `Con los pesos actuales, este tema representa el ${decimal(topic.normalizedWeight * 100)} % del cálculo y aporta ${decimal(topic.contribution)} puntos al porcentaje total.`));
        for (const detail of topic.details) {
          const index = bundle.items.indexOf(detail.item);
          details.append(node('h4', `Pregunta ${index + 1}`), node('p', detail.item.text));
          details.append(node('p', `Tu respuesta: ${labels[detail.answer * 2 + 2]}.`));
          details.append(node('p', `Posición de ${party.name}: ${detail.position === 1 ? 'A favor' : 'En contra'}${bundle.mode === 'mock' ? ' (dato ficticio)' : ''}.`));
          details.append(node('p', `Coincidencia en esta pregunta: ${decimal(detail.alignment * 100)} %.`));
          sources(detail.item, details, 5);
        }
      }
    }
    card.append(details);
  }
  function results() {
    heading('Coincidencia con las medidas que has respondido');
    const result = engine.calculate(bundle, state.answers, state.weights);
    paragraph(`Conjunto de preguntas: ${bundle.version}. Versión del método: ${bundle.method_version}.`);
    if (bundle.mode === 'mock') {
      paragraph('Demostración con preguntas y posiciones ficticias. Estos porcentajes no describen ningún programa político.');
    }
    paragraph(`${result.answered} de 16 respuestas · ${result.topicCount} de 8 temas respondidos.`);
    paragraph('El porcentaje resume solo las preguntas que has respondido. Una respuesta neutral sí cuenta; una pregunta omitida no cuenta en este porcentaje.');
    paragraph('Omitir no significa estar en contra. Este resultado no recomienda a quién votar.');
    if (result.status !== 'ready') {
      paragraph('No hay respuestas suficientes para calcular un porcentaje. Responde al menos 8 preguntas de 4 temas.');
      actions(button('Cambiar respuestas', () => navigate('review'), {class: 'quiz-primary'}));
      return;
    }
    const weights = node('details'); weights.append(node('summary', 'Cambiar el peso de los temas'));
    weights.append(node('p', 'Cada tema tiene el mismo peso al empezar. Si eliges doble peso, ese tema cuenta el doble que uno con peso normal. Los temas sin respuestas no cuentan en el porcentaje actual.'));
    for (const topic of bundle.topics) {
      const wrapper = node('div', null, {class: 'quiz-weight'});
      const select = node('select', null, {id: `weight-${topic.id}`});
      wrapper.append(node('label', topic.name, {for: select.id}));
      for (const value of [1, 2]) {
        const option = node('option', value === 1 ? 'Peso normal' : 'Doble peso', {value});
        option.selected = result.weights[topic.id] === value; select.append(option);
      }
      select.addEventListener('change', () => {
        state.previous = Object.fromEntries(result.parties.filter(p => p.eligible).map(p => [p.id, p.score]));
        state.weights[topic.id] = Number(select.value); render(false);
        const updated = document.getElementById(select.id);
        updated.closest('details').open = true; updated.focus(); announce('Pesos y resultados actualizados.');
      });
      wrapper.append(select); weights.append(wrapper);
    }
    weights.append(button('Restablecer pesos', () => {
      state.previous = Object.fromEntries(result.parties.filter(p => p.eligible).map(p => [p.id, p.score]));
      state.weights = {}; render(false);
      const updated = document.getElementById('quiz-reset-weights');
      updated.closest('details').open = true; updated.focus();
      announce('Todos los temas tienen peso normal.');
    }, {id: 'quiz-reset-weights'}));
    app.append(weights);
    for (const party of result.parties) {
      const card = node('article', null, {class: 'quiz-result'}); card.append(node('h2', party.name));
      if (!party.eligible) {
        card.append(node('p', 'Cobertura insuficiente. No se calcula un porcentaje.'));
        for (const gap of party.gaps) card.append(node('p', gap.reason));
      } else {
        card.append(node('p', `${party.display} %`, {class: 'quiz-score'}));
        if (state.previous?.[party.id] != null) {
          const change = party.score - state.previous[party.id];
          const explanation = change === 0 ? 'El porcentaje no ha cambiado.'
            : `Ha ${change > 0 ? 'subido' : 'bajado'} ${decimal(Math.abs(change))} puntos.`;
          card.append(node('p', `Antes: ${decimal(state.previous[party.id])} %. Ahora: ${decimal(party.score)} %. ${explanation}`));
        }
        for (const comparison of party.comparisons) {
          if (comparison.tied) card.append(node('p', `Empate exacto con ${comparison.name}.`));
          else if (comparison.smallDifference) card.append(node('p', `Diferencia pequeña con ${comparison.name} (como máximo un punto).`));
          if (!comparison.tied && comparison.sameDisplay) card.append(node('p', 'El redondeo hace que estos porcentajes se vean iguales.'));
          if (comparison.overlappingBounds && result.skipped.length) card.append(node('p', `Los escenarios posibles se solapan con ${comparison.name}. Las respuestas omitidas pueden cambiar la coincidencia relativa.`));
        }
        if (result.skipped.length) {
          card.append(node('p', `Si completas las ${result.skipped.length} preguntas omitidas: entre ${decimal(party.lower)} % y ${decimal(party.upper)} %.`));
          card.append(node('p', 'Estos límites usan las 16 preguntas, incluidos los temas que aún no has respondido. El porcentaje actual usa solo los temas respondidos. Muestran resultados posibles, no una probabilidad.'));
        } else {
          card.append(node('p', `Has respondido las 16 preguntas. Los límites del cálculo completo coinciden con tu porcentaje: ${decimal(party.lower)} %.`));
        }
        if (party.sensitivity) card.append(node('p', `Al retirar una respuesta: entre ${decimal(party.sensitivity.min)} % y ${decimal(party.sensitivity.max)} % (${party.sensitivity.count} pruebas válidas). La pregunta ${bundle.items.findIndex(i => i.id === party.sensitivity.largestChange.itemId) + 1} produce el mayor cambio.`));
        else card.append(node('p', 'No hay respuestas suficientes para comprobar cómo cambia el resultado al retirar una.'));
        resultDetails(party, card);
      }
      app.append(card);
    }
    actions(button('Cambiar respuestas', () => navigate('review')),
      button('Compartir el cuestionario', share));
  }
  async function share() {
    const url = document.querySelector('link[rel="canonical"]').href;
    function offerManualLink(isCancel = false) {
      let input = app.querySelector('#quiz-share-link');
      if (!input) {
        const wrapper = node('div', null, {class: 'quiz-share-fallback'});
        wrapper.append(node('label', 'Enlace al cuestionario', {for: 'quiz-share-link'}));
        input = node('input', null, {id: 'quiz-share-link', type: 'url', readonly: ''});
        wrapper.append(input);
        app.append(wrapper);
      }
      input.value = url;
      input.focus();
      input.select();
      announce(isCancel
        ? 'No se ha compartido. Selecciona y copia el enlace al cuestionario.'
        : 'Selecciona y copia el enlace al cuestionario.');
    }
    try {
      if (navigator.share) await navigator.share({title: 'Cuestionario de coincidencia', url});
      else if (navigator.clipboard) { await navigator.clipboard.writeText(url); announce('Enlace al cuestionario copiado.'); }
      else offerManualLink(false);
    } catch (error) {
      // A dismissed native sheet needs a new gesture before clipboard access.
      offerManualLink(error?.name === 'AbortError');
    }
  }
  function render(focus = true) {
    app.replaceChildren();
    ({intro, question, review, result: results}[state.stage])();
    if (state.stage !== 'intro') actions(button('Borrar respuestas', () => { reset(); render(); announce('Respuestas borradas.'); }));
    if (focus) {
      app.querySelector('h1').focus({preventScroll: true});
      app.scrollIntoView({block: 'start', behavior: 'instant'});
    }
  }
  try {
    engine.validate(bundle);
    reset(); render(false);
    window.addEventListener('pagehide', () => { reset(); render(false); });
    window.addEventListener('pageshow', event => { if (event.persisted) { reset(); render(false); } });
  } catch (_) {
    reset(); app.replaceChildren(); heading('No se puede abrir este cuestionario');
    paragraph('Los datos no son válidos. No se ha calculado ningún resultado. Puedes consultar el método y volver a cargar la página.');
  }
})();
