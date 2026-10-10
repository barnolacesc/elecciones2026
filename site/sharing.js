/* Stable public routes and sharing. No visitor state is persisted. */
(function () {
  'use strict';

  function readSelection(href, topics, parties) {
    const params = new URL(href).searchParams;
    const own = (object, key) => Object.prototype.hasOwnProperty.call(object, key);
    const single = key => params.getAll(key).length === 1 ? params.get(key) : null;
    const topic = single('topic');
    const partyA = single('partyA');
    const partyB = single('partyB');
    const rawElection = single('election');
    const election = rawElection === '2023' ? 'es-gen-2023' : rawElection;
    const pilot = election === 'es-gen-2023';
    const validElection = params.getAll('election').length <= 1 &&
      (!election || election === 'es-gen-2026' || pilot);
    const validTopic = own(topics, topic);
    const validPair = validElection && validTopic && own(parties, partyA) &&
      own(parties, partyB) && partyA !== partyB &&
      (!pilot || [partyA, partyB].every(id => id === 'pp' || id === 'erc'));
    return { topic: validTopic ? topic : null, partyA: validPair ? partyA : null,
      partyB: validPair ? partyB : null, pilot: validElection && pilot };
  }

  function stableUrl(href, state) {
    const url = new URL(href);
    url.search = '';
    url.hash = '';
    url.pathname = url.pathname.replace(/index\.html$/, '');
    if (state && state.partyA && state.partyB) {
      url.searchParams.set('topic', state.topic);
      url.searchParams.set('partyA', state.partyA);
      url.searchParams.set('partyB', state.partyB);
    }
    if (state && state.pilot) url.searchParams.set('election', 'es-gen-2023');
    return url.toString();
  }

  function init() {
    const button = document.getElementById('share-button');
    const feedback = document.getElementById('share-feedback');
    const fallback = document.getElementById('share-fallback');
    const input = document.getElementById('share-link');
    const copy = document.getElementById('copy-link-button');
    if (!button || !feedback || !fallback || !input || !copy) return;
    let pending = false;
    function message(text) {
      feedback.textContent = text;
      feedback.classList.remove('sr-only');
    }
    function offerCopy(url) {
      input.value = url;
      fallback.hidden = false;
      message('Puedes copiar el enlace o seleccionarlo para compartirlo.');
    }
    async function copyLink(url) {
      try {
        if (!navigator.clipboard || !navigator.clipboard.writeText) throw new Error('Clipboard unavailable');
        await navigator.clipboard.writeText(url);
        message('Enlace copiado al portapapeles.');
      } catch (_) {
        offerCopy(url);
        input.focus();
        input.select();
        message('Selecciona y copia el enlace para compartirlo.');
      }
    }
    copy.addEventListener('click', () => copyLink(input.value));
    button.addEventListener('click', async function () {
      if (pending) return;
      const state = window.NeutralSharing.getState ? window.NeutralSharing.getState() : null;
      const url = stableUrl(window.location.href, state);
      const pilot = state && state.pilot || document.body.dataset.election === 'es-gen-2023';
      const data = {
        title: pilot ? 'Generales 2023 · Ensayo piloto privado' : 'Elecciones 2026 · Comparador de programas',
        text: pilot ? 'Ensayo técnico privado de programas de 2023. Consulta las fuentes originales.' :
          'Compara propuestas y consulta los programas originales.',
        url: url
      };
      pending = true;
      try {
        if (window.isSecureContext && typeof navigator.share === 'function' &&
            (!navigator.canShare || navigator.canShare(data))) {
          try {
            await navigator.share(data);
            message('Enlace compartido.');
          } catch (_) {
            // A fresh gesture is needed for clipboard access after closing a share sheet.
            offerCopy(url);
          }
        } else {
          await copyLink(url);
        }
      } catch (_) {
        offerCopy(url);
      } finally {
        pending = false;
      }
    });
  }
  window.NeutralSharing = { readSelection: readSelection, stableUrl: stableUrl };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
