// Sidebar toggle on narrow screens, and scroll-spy on the docs page.
(function () {
  var rail = document.querySelector(".rail");
  var btn = document.querySelector(".menu-btn");

  if (btn && rail) {
    btn.addEventListener("click", function () {
      rail.classList.toggle("open");
    });

    // Tapping a link on mobile should close the rail behind you.
    rail.addEventListener("click", function (e) {
      if (e.target.tagName === "A" && window.innerWidth <= 900) {
        rail.classList.remove("open");
      }
    });
  }

  // Highlight the section currently on screen.
  var links = Array.prototype.slice.call(
    document.querySelectorAll('.rail a[href^="#"]')
  );
  if (!links.length || !("IntersectionObserver" in window)) return;

  var byId = {};
  var sections = [];

  links.forEach(function (a) {
    var el = document.getElementById(a.getAttribute("href").slice(1));
    if (el) {
      byId[el.id] = a;
      sections.push(el);
    }
  });

  var visible = {};

  var obs = new IntersectionObserver(
    function (entries) {
      entries.forEach(function (entry) {
        visible[entry.target.id] = entry.isIntersecting;
      });

      // The topmost visible section wins.
      var current = null;
      for (var i = 0; i < sections.length; i++) {
        if (visible[sections[i].id]) {
          current = sections[i].id;
          break;
        }
      }

      if (current) {
        links.forEach(function (a) {
          a.classList.toggle("active", a === byId[current]);
        });
      }
    },
    { rootMargin: "-70px 0px -65% 0px", threshold: 0 }
  );

  sections.forEach(function (s) {
    obs.observe(s);
  });
})();
