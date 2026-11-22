(function () {
  'use strict';

  /**
   * Accessible pagination helper for list containers.
   * Progressively enhances static lists with client-side paging (WCAG 2.2 AA compliant).
   */
  function paginate(container, options) {
    if (!container) return null;
    options = options || {};

    const itemSelector = options.itemSelector || container.getAttribute('data-paginate-items') || null;
    const rawPageSize = options.pageSize || container.getAttribute('data-paginate') || 5;
    const pageSize = Math.max(1, parseInt(rawPageSize, 10) || 5);
    const label = options.label || container.getAttribute('data-paginate-label') || 'Paginación';
    const itemLabel = options.itemLabel || container.getAttribute('data-paginate-item-name') || 'elementos';
    const scrollToTop = options.scrollToTop !== false;

    // Collect target items
    let items;
    if (itemSelector) {
      items = Array.from(container.querySelectorAll(itemSelector));
    } else {
      // Direct children excluding existing pagination nav, notices, or empty states
      items = Array.from(container.children).filter(function (child) {
        return !child.classList.contains('pagination-nav') &&
               !child.classList.contains('notice') &&
               !child.classList.contains('empty-measures');
      });
    }

    const totalItems = items.length;
    const totalPages = Math.ceil(totalItems / pageSize);

    // Remove existing pagination controls if any
    let existingNav = container.nextElementSibling && container.nextElementSibling.classList.contains('pagination-nav')
      ? container.nextElementSibling
      : container.querySelector(':scope > .pagination-nav');
    if (existingNav) {
      existingNav.remove();
    }

    // If total items fit on 1 page or none, ensure all items visible and return
    if (totalItems <= pageSize) {
      items.forEach(function (item) {
        item.style.display = '';
        item.removeAttribute('aria-hidden');
      });
      return {
        currentPage: 1,
        totalPages: totalPages || 1,
        totalItems: totalItems,
        destroy: function () {
          items.forEach(function (i) { i.style.display = ''; });
        }
      };
    }

    let currentPage = Math.min(Math.max(1, parseInt(options.initialPage, 10) || 1), totalPages);

    // Create pagination nav element
    const nav = document.createElement('nav');
    nav.className = 'pagination-nav' + (options.inline ? ' pagination-nav-inline' : '');
    nav.setAttribute('aria-label', label);

    const info = document.createElement('div');
    info.className = 'pagination-info';
    info.setAttribute('aria-hidden', 'true');

    const controls = document.createElement('div');
    controls.className = 'pagination-controls';
    controls.setAttribute('role', 'group');
    controls.setAttribute('aria-label', 'Controles de ' + label.toLowerCase());

    const liveStatus = document.createElement('div');
    liveStatus.className = 'sr-only';
    liveStatus.setAttribute('role', 'status');
    liveStatus.setAttribute('aria-live', 'polite');

    nav.appendChild(info);
    nav.appendChild(controls);
    nav.appendChild(liveStatus);

    function updateView(announce) {
      const startIndex = (currentPage - 1) * pageSize;
      const endIndex = Math.min(startIndex + pageSize, totalItems);

      // Show/hide items
      items.forEach(function (item, index) {
        if (index >= startIndex && index < endIndex) {
          item.style.display = '';
          item.removeAttribute('aria-hidden');
        } else {
          item.style.display = 'none';
          item.setAttribute('aria-hidden', 'true');
        }
      });

      // Update info text
      info.textContent = 'Página ' + currentPage + ' de ' + totalPages + ' · Mostrando ' +
        (startIndex + 1) + '–' + endIndex + ' de ' + totalItems + ' ' + itemLabel;

      if (announce) {
        liveStatus.textContent = 'Página ' + currentPage + ' de ' + totalPages + '. Mostrando ' +
          (startIndex + 1) + ' a ' + endIndex + ' de ' + totalItems + ' ' + itemLabel + '.';
      }

      // Rebuild controls
      controls.innerHTML = '';

      // Previous button
      const prevBtn = document.createElement('button');
      prevBtn.type = 'button';
      prevBtn.className = 'pagination-btn pagination-btn-prev';
      prevBtn.setAttribute('aria-label', 'Página anterior');
      prevBtn.innerHTML = '<span aria-hidden="true">←</span> <span>Anterior</span>';
      if (currentPage === 1) {
        prevBtn.disabled = true;
        prevBtn.setAttribute('aria-disabled', 'true');
      } else {
        prevBtn.addEventListener('click', function () {
          goToPage(currentPage - 1);
        });
      }
      controls.appendChild(prevBtn);

      // Page numbers (smart windowing if > 7 pages)
      const pagesToShow = getPageRange(currentPage, totalPages);
      let lastP = 0;
      for (let i = 0; i < pagesToShow.length; i++) {
        const p = pagesToShow[i];
        if (lastP && p - lastP > 1) {
          const ellipsis = document.createElement('span');
          ellipsis.className = 'pagination-ellipsis';
          ellipsis.setAttribute('aria-hidden', 'true');
          ellipsis.textContent = '…';
          controls.appendChild(ellipsis);
        }
        const pageBtn = document.createElement('button');
        pageBtn.type = 'button';
        pageBtn.className = 'pagination-btn pagination-page' + (p === currentPage ? ' active' : '');
        pageBtn.setAttribute('aria-label', 'Página ' + p + (p === currentPage ? ', actual' : ''));
        pageBtn.textContent = p;
        if (p === currentPage) {
          pageBtn.setAttribute('aria-current', 'page');
        } else {
          (function (targetPage) {
            pageBtn.addEventListener('click', function () {
              goToPage(targetPage);
            });
          })(p);
        }
        controls.appendChild(pageBtn);
        lastP = p;
      }

      // Next button
      const nextBtn = document.createElement('button');
      nextBtn.type = 'button';
      nextBtn.className = 'pagination-btn pagination-btn-next';
      nextBtn.setAttribute('aria-label', 'Página siguiente');
      nextBtn.innerHTML = '<span>Siguiente</span> <span aria-hidden="true">→</span>';
      if (currentPage === totalPages) {
        nextBtn.disabled = true;
        nextBtn.setAttribute('aria-disabled', 'true');
      } else {
        nextBtn.addEventListener('click', function () {
          goToPage(currentPage + 1);
        });
      }
      controls.appendChild(nextBtn);
    }

    function goToPage(targetPage) {
      if (targetPage < 1 || targetPage > totalPages || targetPage === currentPage) return;
      currentPage = targetPage;
      updateView(true);
      if (typeof options.onPageChange === 'function') {
        options.onPageChange(currentPage, totalPages);
      }
      if (scrollToTop && container.scrollIntoView) {
        container.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    }

    function getPageRange(current, total) {
      if (total <= 7) {
        const range = [];
        for (let i = 1; i <= total; i++) range.push(i);
        return range;
      }
      const set = new Set([1, total, current]);
      if (current > 1) set.add(current - 1);
      if (current < total) set.add(current + 1);
      if (current === 1) { set.add(2); set.add(3); }
      if (current === 2) { set.add(3); }
      if (current === total) { set.add(total - 1); set.add(total - 2); }
      if (current === total - 1) { set.add(total - 2); }
      return Array.from(set).sort(function (a, b) { return a - b; });
    }

    // Insert nav after container
    if (container.parentNode) {
      container.parentNode.insertBefore(nav, container.nextSibling);
    }

    updateView(false);

    return {
      getPage: function () { return currentPage; },
      setPage: goToPage,
      totalPages: totalPages,
      totalItems: totalItems,
      destroy: function () {
        items.forEach(function (i) { i.style.display = ''; i.removeAttribute('aria-hidden'); });
        if (nav.parentNode) nav.parentNode.removeChild(nav);
      }
    };
  }

  function initAll() {
    // 1. Explicit data-paginate containers
    const explicitContainers = document.querySelectorAll('[data-paginate]');
    explicitContainers.forEach(function (container) {
      paginate(container);
    });

    // 2. Candidate containers without explicit annotation:
    // a) Topics index (temas/): .topics-grid
    const topicsGrid = document.querySelector('.topics-grid:not([data-paginate])');
    if (topicsGrid) {
      paginate(topicsGrid, {
        pageSize: 6,
        label: 'Paginación de temas',
        itemLabel: 'temas'
      });
    }

    // b) Parties index (partidos/): .parties-list
    const partiesList = document.querySelector('.parties-list:not([data-paginate])');
    if (partiesList) {
      paginate(partiesList, {
        pageSize: 6,
        label: 'Paginación de candidaturas',
        itemLabel: 'candidaturas'
      });
    }

    // c) Topic detail (temas/<tema>/):
    // Subtopics container if > 3 subtopics
    const subtopicsContainer = document.querySelector('.subtopics-container:not([data-paginate])');
    if (subtopicsContainer) {
      paginate(subtopicsContainer, {
        itemSelector: '.subtopic-section',
        pageSize: 3,
        label: 'Paginación de subtemas',
        itemLabel: 'subtemas'
      });
    } else {
      const subtopics = document.querySelectorAll('#contenido > .subtopic-section');
      if (subtopics.length > 3) {
        const parent = subtopics[0].parentNode;
        const wrapper = document.createElement('div');
        wrapper.className = 'subtopics-container';
        parent.insertBefore(wrapper, subtopics[0]);
        subtopics.forEach(function (s) { wrapper.appendChild(s); });
        paginate(wrapper, {
          itemSelector: '.subtopic-section',
          pageSize: 3,
          label: 'Paginación de subtemas',
          itemLabel: 'subtemas'
        });
      }
    }

    // Inside each subtopic section: .measure-cards with > 4 cards
    const measureCardLists = document.querySelectorAll('.subtopic-section .measure-cards:not([data-paginate])');
    measureCardLists.forEach(function (list) {
      const cards = list.querySelectorAll('.party-card');
      if (cards.length > 4) {
        paginate(list, {
          itemSelector: '.party-card',
          pageSize: 4,
          label: 'Paginación de propuestas del subtema',
          itemLabel: 'propuestas',
          inline: true,
          scrollToTop: false
        });
      }
    });

    // d) Party detail (partidos/<partido>/): proposals list
    const partyProposals = document.querySelector('.proposals-list:not([data-paginate])');
    if (partyProposals) {
      paginate(partyProposals, {
        pageSize: 5,
        label: 'Paginación de propuestas',
        itemLabel: 'propuestas'
      });
    }

    // e) Sources page (fuentes/): .coverage-cards
    const coverageCards = document.querySelectorAll('.coverage-cards:not([data-paginate])');
    coverageCards.forEach(function (cardsContainer) {
      paginate(cardsContainer, {
        pageSize: 6,
        label: 'Paginación de fuentes',
        itemLabel: 'fuentes'
      });
    });

    // f) Corrections page (correcciones/):
    const correctionsContainer = document.querySelector('.corrections-list:not([data-paginate])');
    if (correctionsContainer) {
      paginate(correctionsContainer, {
        pageSize: 5,
        label: 'Paginación de correcciones',
        itemLabel: 'correcciones'
      });
    }
  }

  window.EleccionesPagination = {
    paginate: paginate,
    initAll: initAll
  };

  if (typeof document !== 'undefined') {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', initAll);
    } else {
      initAll();
    }
  }
})();
