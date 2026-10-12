/* E10.3: selected-topic context; official figures never depend on parties. */
(function () {
  'use strict';
  const region = document.getElementById('budget-context');
  if (!region) return;
  const topics = new Set(['housing', 'education', 'health-social-services', 'economy-work-tax',
    'immigration', 'foreign-policy-eu', 'climate-energy', 'institutions-rights']);
  const cache = new Map();
  let generation = 0;
  let pending = null;
  let pendingTopic = null;

  function element(tag, text, className) {
    const node = document.createElement(tag);
    if (text !== undefined) node.textContent = text;
    if (className) node.className = className;
    return node;
  }

  function render(data) {
    const source = new URL(data.source_url);
    if (source.protocol !== 'https:' || source.username || source.password ||
        !Array.isArray(data.rows) || !Array.isArray(data.notes) || data.rows.length > 27) {
      throw new Error('Invalid budget projection');
    }
    const content = document.createDocumentFragment();
    content.append(element('h2', data.title), element('p', data.topic_label));
    if (data.rows.length) {
      const list = element('ul', undefined, 'budget-context-rows');
      data.rows.forEach(function (row) {
        const item = element('li');
        const link = element('a', 'Tabla oficial');
        link.href = source.href;
        item.append(element('strong', row.label), element('p', row.amount + ' millones de euros · ' + row.share),
          link, document.createTextNode(' '), element('span', row.locator, 'budget-locator'));
        list.append(item);
      });
      content.append(list);
    } else {
      content.append(element('p', data.gap));
    }
    data.notes.forEach(note => content.append(element('p', note)));
    const version = element('p', 'Versión de datos: ' + data.version + '. ');
    const link = element('a', 'Ver el presupuesto completo de 2023');
    link.href = region.dataset.budgetUrl;
    version.append(link);
    content.append(version);
    region.replaceChildren(content);
    region.dataset.topic = data.topic_id;
  }

  async function update(topic) {
    if (!topics.has(topic)) { clear(); return; }
    region.hidden = false;
    if (pendingTopic === topic || (region.dataset.topic === topic && !pending)) return;
    const token = ++generation;
    if (pending) pending.abort();
    pending = null;
    pendingTopic = null;
    region.dataset.topic = '';
    region.replaceChildren(element('h2', 'Contexto presupuestario oficial · PGE 2023'),
      element('p', 'Consultando el contexto de este tema…'));
    if (cache.has(topic)) { render(cache.get(topic)); return; }
    const controller = new AbortController();
    pending = controller;
    pendingTopic = topic;
    try {
      const url = new URL(topic + '.json', new URL(region.dataset.base, window.location.href));
      if (url.origin !== window.location.origin) throw new Error('Invalid projection origin');
      const response = await fetch(url.href, { signal: controller.signal, credentials: 'omit' });
      if (!response.ok) throw new Error('Budget projection unavailable');
      // Generated projections have a strict 16 KiB build limit; enforce it again here.
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let text = '', bytes = 0;
      while (true) {
        const chunk = await reader.read();
        if (chunk.done) break;
        bytes += chunk.value.byteLength;
        if (bytes > 16384) { await reader.cancel(); throw new Error('Projection too large'); }
        text += decoder.decode(chunk.value, { stream: true });
      }
      text += decoder.decode();
      const data = JSON.parse(text);
      if (data.topic_id !== topic) throw new Error('Wrong budget topic');
      if (token !== generation) return;
      render(data);
      cache.set(topic, data);
    } catch (error) {
      if (token !== generation || error.name === 'AbortError') return;
      region.replaceChildren(element('h2', 'Contexto presupuestario oficial · PGE 2023'),
        element('p', 'El contexto presupuestario no está disponible. La comparación de propuestas sigue disponible.'));
    } finally {
      if (token === generation) { pending = null; pendingTopic = null; }
    }
  }

  function clear() {
    ++generation;
    if (pending) pending.abort();
    pending = null;
    pendingTopic = null;
    region.hidden = true;
  }
  window.BudgetContext = { update, clear };
}());
