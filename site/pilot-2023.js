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
      const shareBtn = element('button', 'Compartir texto (Wordle)', 'button pilot-share-btn');
      shareBtn.type = 'button';
      const imageBtn = element('button', 'Descargar tarjeta (imagen)', 'button button-secondary pilot-image-btn');
      imageBtn.type = 'button';
      const retakeBtn = element('button', 'Repetir cuestionario', 'button button-secondary pilot-retake-btn');
      retakeBtn.type = 'button';
      retakeBtn.addEventListener('click', () => { window.location.reload(); });
      actionGroup.append(shareBtn, imageBtn, retakeBtn);

      const shareStatus = element('p', '', 'pilot-share-status');
      shareStatus.setAttribute('role', 'status');
      shareStatus.setAttribute('aria-live', 'polite');
      shareStatus.hidden = true;

      async function generateResultsImage(stats, totalAnswers) {
        const canvas = document.createElement('canvas');
        canvas.width = 1200;
        canvas.height = 675;
        const ctx = canvas.getContext('2d');
        if (!ctx) throw new Error('Canvas 2D unavailable');

        function roundRectPath(x, y, w, h, r) {
          if (ctx.roundRect) {
            ctx.roundRect(x, y, w, h, r);
          } else {
            ctx.moveTo(x + r, y);
            ctx.arcTo(x + w, y, x + w, y + h, r);
            ctx.arcTo(x + w, y + h, x, y + h, r);
            ctx.arcTo(x, y + h, x, y, r);
            ctx.arcTo(x, y, x + w, y, r);
            ctx.closePath();
          }
        }

        ctx.fillStyle = '#ffffff';
        ctx.fillRect(0, 0, 1200, 675);

        ctx.strokeStyle = '#e2e8f0';
        ctx.lineWidth = 2;
        ctx.beginPath();
        roundRectPath(20, 20, 1160, 635, 16);
        ctx.stroke();

        ctx.fillStyle = '#64748b';
        ctx.font = 'bold 13px system-ui, -apple-system, sans-serif';
        ctx.fillText('PILOTO HISTÓRICO · ELECCIONES 2023', 60, 65);

        ctx.fillStyle = '#0a0d12';
        ctx.font = 'bold 30px system-ui, -apple-system, sans-serif';
        ctx.fillText('Test de propuestas electorales a ciegas', 60, 105);

        ctx.fillStyle = '#475569';
        ctx.font = '500 17px system-ui, -apple-system, sans-serif';
        ctx.fillText(`Resultados tras valorar ${totalAnswers} medidas de los programas sin conocer las siglas`, 60, 135);

        ctx.strokeStyle = '#e2e8f0';
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(60, 155);
        ctx.lineTo(1140, 155);
        ctx.stroke();

        function drawBadge(text, x, y, bg, border, color) {
          ctx.font = 'bold 13px system-ui, -apple-system, sans-serif';
          const textWidth = ctx.measureText(text).width;
          const w = textWidth + 18;
          const h = 26;
          ctx.fillStyle = bg;
          ctx.strokeStyle = border;
          ctx.lineWidth = 1;
          ctx.beginPath();
          roundRectPath(x, y, w, h, 6);
          ctx.fill();
          ctx.stroke();
          ctx.fillStyle = color;
          ctx.fillText(text, x + 9, y + 17);
          return w;
        }

        let startY = 195;
        const rowGap = 85;

        for (const p of stats) {
          ctx.fillStyle = '#0a0d12';
          ctx.font = 'bold 22px system-ui, -apple-system, sans-serif';
          ctx.fillText(p.name, 60, startY);

          let badgeX = 180;
          if (p.supported > 0) {
            badgeX += drawBadge(`✓ ${p.supported} a favor`, badgeX, startY - 20, '#dcfce7', '#86efac', '#14532d') + 8;
          }
          if (p.opposed > 0) {
            badgeX += drawBadge(`✕ ${p.opposed} en contra`, badgeX, startY - 20, '#fee2e2', '#fca5a5', '#7f1d1d') + 8;
          }
          if (p.neutral > 0) {
            const neutralText = p.neutral === 1 ? '– 1 neutra' : `– ${p.neutral} neutras`;
            drawBadge(neutralText, badgeX, startY - 20, '#f1f5f9', '#cbd5e1', '#334155');
          }

          const barY = startY + 12;
          const barW = 1080;
          const barH = 14;

          ctx.fillStyle = '#e2e8f0';
          ctx.beginPath();
          roundRectPath(60, barY, barW, barH, 7);
          ctx.fill();

          if (p.total > 0) {
            const supPct = p.supported / p.total;
            const neuPct = p.neutral / p.total;
            const oppPct = p.opposed / p.total;

            ctx.save();
            ctx.beginPath();
            roundRectPath(60, barY, barW, barH, 7);
            ctx.clip();

            let curX = 60;
            if (supPct > 0) {
              const w = Math.round(barW * supPct);
              ctx.fillStyle = '#16a34a';
              ctx.fillRect(curX, barY, w, barH);
              curX += w;
            }
            if (neuPct > 0) {
              const w = Math.round(barW * neuPct);
              ctx.fillStyle = '#94a3b8';
              ctx.fillRect(curX, barY, w, barH);
              curX += w;
            }
            if (oppPct > 0) {
              const w = barW - (curX - 60);
              ctx.fillStyle = '#dc2626';
              ctx.fillRect(curX, barY, w, barH);
            }
            ctx.restore();
          }

          startY += rowGap;
        }

        ctx.strokeStyle = '#e2e8f0';
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(60, 550);
        ctx.lineTo(1140, 550);
        ctx.stroke();

        ctx.fillStyle = '#0a0d12';
        ctx.font = 'bold 15px system-ui, -apple-system, sans-serif';
        ctx.fillText('¿Coincidirías con quien crees? Haz la prueba en:', 60, 580);
        ctx.fillStyle = '#0a0d12';
        ctx.font = '500 15px system-ui, -apple-system, sans-serif';
        const displayUrl = (location.origin + location.pathname).replace(/\/$/, '') + '/';
        ctx.fillText(displayUrl, 60, 606);

        ctx.fillStyle = '#64748b';
        ctx.font = '12px system-ui, -apple-system, sans-serif';
        ctx.textAlign = 'right';
        ctx.fillText('Archivo histórico de 2023 · Datos provisionales sin revisión editorial humana.', 1140, 580);
        ctx.fillText('No calcula afinidad partidista ni recomienda el voto.', 1140, 602);
        ctx.textAlign = 'left';

        return new Promise(resolve => canvas.toBlob(resolve, 'image/png'));
      }

      const shareUrl = window.location.href.split('#')[0];
      const shareLines = partyStats.map(p => {
        const blocks = '🟩'.repeat(p.supported) + '⬜'.repeat(p.neutral) + '🟥'.repeat(p.opposed);
        const parts = [];
        if (p.supported) parts.push(`${p.supported} a favor`);
        if (p.opposed) parts.push(`${p.opposed} en contra`);
        if (p.neutral) parts.push(p.neutral === 1 ? '1 neutra' : `${p.neutral} neutras`);
        const textSummary = parts.length > 0 ? ` (${parts.join(', ')})` : '';
        return `• ${p.name}: ${blocks || '▫️'}${textSummary}`;
      });
      const shareBody = `🗳️ Test electoral a ciegas: ${answers.length} medidas valoradas sin ver las siglas\n\n${shareLines.join('\n')}\n\n(🟩 a favor · ⬜ neutra · 🟥 en contra)\n\n¿Coincidirías con quien crees? Haz la prueba aquí:`;
      const shareText = `${shareBody}\n${shareUrl}`;

      shareBtn.addEventListener('click', async () => {
        if (navigator.share) {
          try {
            await navigator.share({
              title: 'Mis resultados en el test electoral a ciegas',
              text: shareBody,
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

      imageBtn.addEventListener('click', async () => {
        imageBtn.disabled = true;
        const origText = imageBtn.textContent;
        imageBtn.textContent = 'Generando tarjeta…';
        try {
          const blob = await generateResultsImage(partyStats, answers.length);
          if (!blob) throw new Error('Image generation failed');
          const file = new File([blob], 'mis-resultados-electorales.png', { type: 'image/png' });

          if (navigator.share && navigator.canShare && navigator.canShare({ files: [file] })) {
            await navigator.share({
              title: 'Mis resultados en el test electoral a ciegas',
              text: 'He valorado propuestas electorales sin ver las siglas. ¡Haz la prueba tú también!',
              files: [file]
            });
            shareStatus.textContent = '¡Tarjeta compartida!';
            shareStatus.hidden = false;
          } else {
            const url = URL.createObjectURL(file);
            const a = document.createElement('a');
            a.href = url;
            a.download = file.name;
            document.body.append(a);
            a.click();
            a.remove();
            setTimeout(() => URL.revokeObjectURL(url), 60000);
            shareStatus.textContent = '¡Tarjeta descargada (PNG)! Ya puedes adjuntarla en Twitter, WhatsApp o tus redes.';
            shareStatus.hidden = false;
          }
        } catch (err) {
          if (err.name !== 'AbortError') {
            shareStatus.textContent = 'No se pudo generar la tarjeta de imagen. Puedes compartir el texto.';
            shareStatus.hidden = false;
          }
        } finally {
          imageBtn.disabled = false;
          imageBtn.textContent = origText;
        }
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
