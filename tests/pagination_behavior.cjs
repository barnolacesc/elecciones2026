const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const { test } = require('node:test');

function createMockElement(tagName, className = '', id = '') {
  const children = [];
  const attributes = new Map();
  const eventListeners = {};
  const style = {};

  return {
    tagName: tagName.toUpperCase(),
    className,
    id,
    children,
    style,
    parentNode: null,
    nextSibling: null,
    nextElementSibling: null,
    getAttribute(name) { return attributes.get(name) || null; },
    setAttribute(name, val) { attributes.set(name, String(val)); },
    removeAttribute(name) { attributes.delete(name); },
    hasAttribute(name) { return attributes.has(name); },
    classList: {
      add(cls) {
        const parts = new Set((className || '').split(' ').filter(Boolean));
        parts.add(cls);
        className = Array.from(parts).join(' ');
      },
      remove(cls) {
        const parts = new Set((className || '').split(' ').filter(Boolean));
        parts.delete(cls);
        className = Array.from(parts).join(' ');
      },
      contains(cls) {
        return (className || '').split(' ').includes(cls);
      }
    },
    appendChild(child) {
      child.parentNode = this;
      children.push(child);
      return child;
    },
    removeChild(child) {
      const idx = children.indexOf(child);
      if (idx !== -1) {
        children.splice(idx, 1);
        child.parentNode = null;
      }
      return child;
    },
    insertBefore(newChild, refChild) {
      newChild.parentNode = this;
      const idx = refChild ? children.indexOf(refChild) : -1;
      if (idx === -1) {
        children.push(newChild);
      } else {
        children.splice(idx, 0, newChild);
      }
      return newChild;
    },
    remove() {
      if (this.parentNode) {
        this.parentNode.removeChild(this);
      }
    },
    addEventListener(type, handler) {
      if (!eventListeners[type]) eventListeners[type] = [];
      eventListeners[type].push(handler);
    },
    click() {
      if (this.disabled || attributes.get('aria-disabled') === 'true') return;
      const handlers = eventListeners['click'] || [];
      for (const h of handlers) h({ target: this });
    },
    scrollIntoView() { this.scrolled = true; },
    querySelectorAll(selector) {
      const results = [];
      function traverse(node) {
        for (const c of node.children) {
          if (matches(c, selector)) results.push(c);
          traverse(c);
        }
      }
      traverse(this);
      return results;
    },
    querySelector(selector) {
      return this.querySelectorAll(selector)[0] || null;
    }
  };
}

function matches(el, selector) {
  if (selector.startsWith('.')) {
    const cls = selector.slice(1);
    return el.classList.contains(cls);
  }
  if (selector.startsWith('#')) {
    return el.id === selector.slice(1);
  }
  return el.tagName === selector.toUpperCase();
}

function setupMockDOM() {
  const elements = [];
  const doc = {
    readyState: 'complete',
    createElement(tag) {
      const el = createMockElement(tag);
      elements.push(el);
      return el;
    },
    querySelectorAll(selector) {
      const results = [];
      for (const el of elements) {
        if (matches(el, selector)) results.push(el);
      }
      return results;
    },
    querySelector(selector) {
      return this.querySelectorAll(selector)[0] || null;
    },
    addEventListener() {}
  };

  const context = vm.createContext({
    document: doc,
    window: {},
    Array,
    Math,
    parseInt,
    Set
  });
  context.window = context;

  const code = fs.readFileSync('site/pagination.js', 'utf8');
  vm.runInContext(code, context);

  return { context, doc, createElement: doc.createElement.bind(doc) };
}

test('EleccionesPagination.paginate chunks items and provides navigation', () => {
  const { context, createElement } = setupMockDOM();
  const Pagination = context.window.EleccionesPagination;
  assert.ok(Pagination, 'EleccionesPagination must be defined');

  // Create parent and container with 12 items
  const parent = createElement('main');
  const container = createElement('div', 'test-list');
  parent.appendChild(container);

  for (let i = 1; i <= 12; i++) {
    const item = createElement('article', 'item');
    item.textContent = `Item ${i}`;
    container.appendChild(item);
  }

  const controller = Pagination.paginate(container, {
    pageSize: 5,
    label: 'Paginación de prueba',
    itemLabel: 'elementos',
    scrollToTop: false
  });

  assert.ok(controller, 'paginate must return controller object');
  assert.equal(controller.totalPages, 3);
  assert.equal(controller.getPage(), 1);

  // Page 1: items 0-4 visible, items 5-11 hidden
  for (let i = 0; i < 12; i++) {
    if (i < 5) {
      assert.equal(container.children[i].style.display, '');
    } else {
      assert.equal(container.children[i].style.display, 'none');
    }
  }

  // Go to page 2
  controller.setPage(2);
  assert.equal(controller.getPage(), 2);

  // Page 2: items 5-9 visible, items 0-4 and 10-11 hidden
  for (let i = 0; i < 12; i++) {
    if (i >= 5 && i < 10) {
      assert.equal(container.children[i].style.display, '');
    } else {
      assert.equal(container.children[i].style.display, 'none');
    }
  }

  // Go to page 3
  controller.setPage(3);
  assert.equal(controller.getPage(), 3);

  // Page 3: items 10-11 visible
  for (let i = 0; i < 12; i++) {
    if (i >= 10) {
      assert.equal(container.children[i].style.display, '');
    } else {
      assert.equal(container.children[i].style.display, 'none');
    }
  }
});

test('EleccionesPagination does not add controls when total items <= pageSize', () => {
  const { context, createElement } = setupMockDOM();
  const Pagination = context.window.EleccionesPagination;

  const parent = createElement('main');
  const container = createElement('div', 'short-list');
  parent.appendChild(container);

  for (let i = 1; i <= 3; i++) {
    const item = createElement('article', 'item');
    container.appendChild(item);
  }

  const controller = Pagination.paginate(container, {
    pageSize: 5
  });

  assert.equal(controller.totalPages, 1);
  for (const item of container.children) {
    assert.equal(item.style.display, '');
  }
});
