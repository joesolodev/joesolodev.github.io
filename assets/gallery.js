// Lightbox for the work gallery. Click a thumbnail to open the full-size
// render; arrows and Escape work; clicking the backdrop closes it.
(function () {
  var links = Array.prototype.slice.call(document.querySelectorAll(".gallery a"));
  if (!links.length) return;

  var box = document.createElement("div");
  box.className = "lightbox";
  box.hidden = true;
  box.innerHTML =
    '<button class="lb-close" aria-label="Close">&times;</button>' +
    '<button class="lb-prev" aria-label="Previous">&#8249;</button>' +
    '<img alt="">' +
    '<button class="lb-next" aria-label="Next">&#8250;</button>' +
    '<div class="lb-cap"></div>';
  document.body.appendChild(box);

  var img = box.querySelector("img");
  var cap = box.querySelector(".lb-cap");
  var current = 0;

  function show(i) {
    current = (i + links.length) % links.length;
    var a = links[current];
    img.src = a.getAttribute("href");
    img.alt = a.querySelector("img").alt;
    cap.textContent = a.getAttribute("data-title") || "";
    box.hidden = false;
    document.body.style.overflow = "hidden";
  }

  function hide() {
    box.hidden = true;
    img.src = "";
    document.body.style.overflow = "";
  }

  links.forEach(function (a, i) {
    a.addEventListener("click", function (e) {
      e.preventDefault();
      show(i);
    });
  });

  box.querySelector(".lb-close").addEventListener("click", hide);
  box.querySelector(".lb-prev").addEventListener("click", function (e) { e.stopPropagation(); show(current - 1); });
  box.querySelector(".lb-next").addEventListener("click", function (e) { e.stopPropagation(); show(current + 1); });
  img.addEventListener("click", function (e) { e.stopPropagation(); });
  box.addEventListener("click", hide);

  document.addEventListener("keydown", function (e) {
    if (box.hidden) return;
    if (e.key === "Escape") hide();
    else if (e.key === "ArrowLeft") show(current - 1);
    else if (e.key === "ArrowRight") show(current + 1);
  });
})();
