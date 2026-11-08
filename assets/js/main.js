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
