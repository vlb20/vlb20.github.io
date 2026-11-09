(function () {
  var root = document.documentElement;

  /* theme toggle: follows the system until the visitor picks one */
  var toggle = document.querySelector('.toggle');
  var current = function () {
    return root.dataset.theme || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
  };
  root.dataset.theme = current();
  if (toggle) toggle.addEventListener('click', function () {
    var next = current() === 'dark' ? 'light' : 'dark';
    root.dataset.theme = next;
    try { localStorage.setItem('theme', next); } catch (e) {}
  });

  /* navbar: mobile menu */
  var header = document.querySelector('.site-header');
  var menuBtn = document.querySelector('.menu-btn');
  var setMenu = function (open) {
    if (!header || !menuBtn) return;
    header.classList.toggle('is-open', open);
    document.body.classList.toggle('menu-open', open);
    menuBtn.setAttribute('aria-expanded', open ? 'true' : 'false');
    menuBtn.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
  };
  if (menuBtn) menuBtn.addEventListener('click', function () { setMenu(!header.classList.contains('is-open')); });
  document.querySelectorAll('.nav-link').forEach(function (a) { a.addEventListener('click', function () { setMenu(false); }); });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') setMenu(false); });
  window.matchMedia('(min-width: 861px)').addEventListener('change', function (e) { if (e.matches) setMenu(false); });

  /* navbar: highlight the section in view */
  var links = document.querySelectorAll('.nav-link[data-section]');
  if (links.length && 'IntersectionObserver' in window) {
    var spy = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        links.forEach(function (l) { l.classList.toggle('is-active', l.dataset.section === e.target.id); });
      });
    }, { rootMargin: '-45% 0px -50% 0px' });
    links.forEach(function (l) { var s = document.getElementById(l.dataset.section); if (s) spy.observe(s); });
    var hero = document.querySelector('.hero');
    if (hero) new IntersectionObserver(function (es) {
      if (es[0].isIntersecting) links.forEach(function (l) { l.classList.remove('is-active'); });
    }, { rootMargin: '-45% 0px -50% 0px' }).observe(hero);
  }

  /* reveal sections and start the map drawing when they scroll into view */
  var maps = document.querySelectorAll('svg.study-map[data-scroll]');
  var reveals = document.querySelectorAll('.reveal');
  if (!('IntersectionObserver' in window)) {
    maps.forEach(function (m) { m.classList.add('in-view'); });
    reveals.forEach(function (e) { e.classList.add('in'); });
  } else {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        e.target.classList.add(e.target.tagName.toLowerCase() === 'svg' ? 'in-view' : 'in');
        io.unobserve(e.target);
      });
    }, { threshold: 0.2 });
    maps.forEach(function (m) { io.observe(m); });
    reveals.forEach(function (e) { io.observe(e); });
  }

  /* link the map and the timeline */
  var path = document.querySelector('.path');
  if (!path) return;
  var stops = path.querySelectorAll('.stop');
  var focus = function (scene) {
    if (!scene) { delete path.dataset.focus; } else { path.dataset.focus = scene; }
    stops.forEach(function (s) { s.classList.toggle('is-on', !!scene && s.dataset.scene === scene); });
  };
  stops.forEach(function (s) {
    s.addEventListener('mouseenter', function () { focus(s.dataset.scene); });
    s.addEventListener('mouseleave', function () { focus(null); });
    s.addEventListener('focus', function () { focus(s.dataset.scene); });
    s.addEventListener('blur', function () { focus(null); });
  });
  /* easter egg: the stadium */
  var setEgg = function (on) { path.classList.toggle('egg-on', on); };
  path.querySelectorAll('.study-map .stadium').forEach(function (st) {
    var hit = function (ev) { ev.stopPropagation(); ev.preventDefault(); setEgg(!path.classList.contains('egg-on')); };
    st.addEventListener('click', hit);
    st.addEventListener('keydown', function (ev) { if (ev.key === 'Enter' || ev.key === ' ') hit(ev); });
  });
  var close = path.querySelector('.egg-close');
  if (close) close.addEventListener('click', function () { setEgg(false); });
  document.addEventListener('keydown', function (ev) { if (ev.key === 'Escape') setEgg(false); });

  path.querySelectorAll('.study-map .scene').forEach(function (g) {
    g.addEventListener('click', function (ev) {
      ev.stopPropagation();
      var scene = g.dataset.scene;
      focus(path.dataset.focus === scene ? null : scene);
    });
  });
  document.addEventListener('click', function (ev) {
    if (path.dataset.focus && !ev.target.closest('.stop')) focus(null);
  });
})();
