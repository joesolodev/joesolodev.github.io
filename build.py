#!/usr/bin/env python3
"""Build the blog from Markdown.

    python build.py

Reads every posts/*.md, writes blog/<slug>.html and blog/index.html, and
copies images into assets/blog/ at a web-sensible size.

A post looks like this:

    ---
    title: Shipshape is live
    date: 2026-09-09
    summary: One line for the index page. Optional.
    ---

    Body text in Markdown.

    ![Alt text](images/whatever.png)

Only the Markdown a blog post actually needs is supported: headings,
bold, italic, inline code, links, images, lists, blockquotes, fenced
code, and horizontal rules. No dependencies beyond Pillow, and that is
only needed if a post has images.
"""

import html
import os
import re
import shutil
import sys
from datetime import date

ROOT = os.path.dirname(os.path.abspath(__file__))
POSTS = os.path.join(ROOT, "posts")
OUT = os.path.join(ROOT, "blog")
IMG_OUT = os.path.join(ROOT, "assets", "blog")

# Images wider than this are resized down. Full-size copies are kept for
# the lightbox, the same as the About page gallery.
THUMB_W = 1100
FULL_W = 2000


# --------------------------------------------------------------------------
# Markdown
# --------------------------------------------------------------------------

def inline(text):
    """Inline markup. Order matters: code first so its content is literal."""
    out = []
    for i, part in enumerate(re.split(r"(`[^`]+`)", text)):
        if i % 2:
            out.append("<code>%s</code>" % html.escape(part[1:-1]))
            continue

        part = html.escape(part)
        # Image before link - the syntax differs by one leading char.
        part = re.sub(r"!\[([^\]]*)\]\(([^)\s]+)\)", r'<img src="\2" alt="\1">', part)
        part = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", r'<a href="\2">\1</a>', part)
        part = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", part)
        part = re.sub(r"(?<![*\w])\*([^*]+)\*(?!\w)", r"<em>\1</em>", part)
        # Typographic touches, matching the rest of the site.
        part = part.replace(" -- ", " &mdash; ")
        out.append(part)
    return "".join(out)


def render(md):
    """Markdown to HTML. Block level."""
    lines = md.split("\n")
    out = []
    i = 0

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            i += 1
            continue

        # Fenced code.
        if stripped.startswith("```"):
            i += 1
            body = []
            while i < len(lines) and not lines[i].strip().startswith("```"):
                body.append(lines[i])
                i += 1
            i += 1
            out.append("<pre><code>%s</code></pre>" % html.escape("\n".join(body)))
            continue

        # Horizontal rule.
        if re.fullmatch(r"(-{3,}|\*{3,})", stripped):
            out.append("<hr>")
            i += 1
            continue

        # Heading.
        m = re.match(r"(#{1,4})\s+(.*)", stripped)
        if m:
            level = len(m.group(1)) + 1      # "# " is an h2; h1 is the title
            level = min(level, 5)
            out.append("<h%d>%s</h%d>" % (level, inline(m.group(2)), level))
            i += 1
            continue

        # An image alone on a line becomes a figure, so it can be captioned
        # and click-to-zoom like the gallery.
        m = re.fullmatch(r"!\[([^\]]*)\]\(([^)\s]+)\)", stripped)
        if m:
            alt, src = m.group(1), m.group(2)
            # "{narrow}" at the end of the alt text marks a UI capture that
            # must not be scaled up past its native width.
            narrow = alt.endswith("{narrow}")
            if narrow:
                alt = alt[:-len("{narrow}")].strip()
            base = os.path.splitext(os.path.basename(src))[0]
            full = "../assets/blog/%s.jpg" % base
            thumb = "../assets/blog/%s-thumb.jpg" % base
            fig = ['<figure class="post-fig%s">' % (" narrow" if narrow else ""),
                   '  <a href="%s" data-title="%s">' % (full, html.escape(alt)),
                   '    <img src="%s" alt="%s" loading="lazy">' % (thumb, html.escape(alt)),
                   '  </a>']
            if alt:
                fig.append("  <figcaption>%s</figcaption>" % inline(alt))
            fig.append("</figure>")
            out.append("\n".join(fig))
            i += 1
            continue

        # Blockquote.
        if stripped.startswith(">"):
            body = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                body.append(lines[i].strip().lstrip(">").strip())
                i += 1
            out.append("<blockquote><p>%s</p></blockquote>" % inline(" ".join(body)))
            continue

        # Lists.
        if re.match(r"[-*]\s+", stripped) or re.match(r"\d+\.\s+", stripped):
            ordered = bool(re.match(r"\d+\.\s+", stripped))
            tag = "ol" if ordered else "ul"
            items = []
            pattern = r"\d+\.\s+" if ordered else r"[-*]\s+"
            while i < len(lines) and re.match(pattern, lines[i].strip()):
                items.append(re.sub(pattern, "", lines[i].strip(), count=1))
                i += 1
            out.append("<%s>\n%s\n</%s>" % (
                tag,
                "\n".join("  <li>%s</li>" % inline(x) for x in items),
                tag))
            continue

        # Paragraph: gather until a blank line.
        body = []
        while i < len(lines) and lines[i].strip():
            nxt = lines[i].strip()
            if (nxt.startswith(("#", ">", "```"))
                    or re.match(r"[-*]\s+", nxt)
                    or re.match(r"\d+\.\s+", nxt)
                    or re.fullmatch(r"!\[([^\]]*)\]\(([^)\s]+)\)", nxt)):
                break
            body.append(nxt)
            i += 1
        if body:
            out.append("<p>%s</p>" % inline(" ".join(body)))

    return "\n\n".join(out)


# --------------------------------------------------------------------------
# Posts
# --------------------------------------------------------------------------

def parse(path):
    """Split front matter from body."""
    raw = open(path, encoding="utf-8").read().replace("\r\n", "\n")
    meta = {}
    body = raw

    if raw.startswith("---"):
        end = raw.find("\n---", 3)
        if end != -1:
            for line in raw[3:end].strip().split("\n"):
                if ":" in line:
                    k, v = line.split(":", 1)
                    meta[k.strip().lower()] = v.strip()
            body = raw[end + 4:].lstrip("\n")

    name = os.path.splitext(os.path.basename(path))[0]
    # A leading 2026-09-09- is a date, not part of the slug.
    m = re.match(r"(\d{4}-\d{2}-\d{2})-(.+)", name)
    if m:
        meta.setdefault("date", m.group(1))
        slug = m.group(2)
    else:
        slug = name

    meta["slug"] = meta.get("slug", slug)
    meta.setdefault("title", slug.replace("-", " ").capitalize())
    meta.setdefault("date", date.today().isoformat())
    meta["body"] = body
    return meta


def pretty_date(iso):
    try:
        y, m, d = (int(x) for x in iso.split("-"))
        months = ("January February March April May June July August "
                  "September October November December").split()
        return "%d %s %d" % (d, months[m - 1], y)
    except Exception:
        return iso


def copy_images(body):
    """Copy referenced images into assets/blog, resized. Returns count."""
    refs = re.findall(r"!\[[^\]]*\]\(([^)\s]+)\)", body)
    if not refs:
        return 0

    try:
        from PIL import Image
    except ImportError:
        print("  ! Pillow not installed - images not resized. pip install pillow")
        return 0

    os.makedirs(IMG_OUT, exist_ok=True)
    n = 0
    for ref in refs:
        if ref.startswith(("http://", "https://")):
            continue
        src = os.path.join(POSTS, ref)
        if not os.path.exists(src):
            print("  ! missing image: %s" % ref)
            continue

        base = os.path.splitext(os.path.basename(ref))[0]
        img = Image.open(src)
        for suffix, width, q in (("-thumb", THUMB_W, 84), ("", FULL_W, 86)):
            im = img.copy()
            im.thumbnail((width, width), Image.LANCZOS)
            if im.mode != "RGB":
                im = im.convert("RGB")
            im.save(os.path.join(IMG_OUT, "%s%s.jpg" % (base, suffix)),
                    "JPEG", quality=q, optimize=True, progressive=True)
        n += 1
    return n


# --------------------------------------------------------------------------
# Templates
# --------------------------------------------------------------------------

HEAD = '''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Cache-Control" content="no-cache">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 56 56'><rect x='2' y='2' width='52' height='52' rx='4' fill='%230a2540' stroke='%2378beff' stroke-width='4'/><path d='M16 29 L25 38 L41 19' stroke='%234ade80' stroke-width='6' fill='none'/></svg>">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,800&family=Outfit:wght@400;500;600&family=IBM+Plex+Mono:wght@400&display=swap">
<link rel="stylesheet" href="../assets/site.css">
</head>
<body>

<header class="topbar">
  <a class="wordmark" href="../index.html">
    <svg width="22" height="22" viewBox="0 0 56 56" fill="none" aria-hidden="true">
      <rect x="2" y="2" width="52" height="52" rx="4" stroke="#78beff" stroke-width="3"/>
      <path d="M16 29 L25 38 L41 19" stroke="#4ade80" stroke-width="6" stroke-linecap="square" stroke-linejoin="miter"/>
    </svg>
    Joe Solo
  </a>
  <span class="crumb">/ {crumb}</span>
  <button class="menu-btn" aria-label="Menu">&#9776;</button>
</header>

<nav class="rail">
  <div class="rail-title">Categories</div>
  <div class="rail-group">Blender add-ons</div>
  <a class="sub" href="../shipshape.html">Shipshape Validator</a>
  <div class="rail-group">About</div>
  <a class="sub" href="../about.html">Joe Solo</a>
  <a class="sub" href="../about.html#work">Personal work</a>
  <div class="rail-group">Blog</div>
  <a class="sub{blog_active}" href="index.html">All posts</a>
{rail_posts}</nav>

<main class="main">
'''

FOOT = '''
  <footer class="foot">
    <div class="row">
      <span>Joe Solo</span>
      <span class="spacer"></span>
      <a href="index.html">Blog</a>
      <a href="../about.html">About</a>
      <a href="mailto:joesoloart@gmail.com">joesoloart@gmail.com</a>
    </div>
  </footer>

</main>

<script src="../assets/nav.js"></script>
<script src="../assets/gallery.js"></script>
</body>
</html>
'''


def build():
    if not os.path.isdir(POSTS):
        print("no posts/ directory")
        return 1

    files = sorted(f for f in os.listdir(POSTS) if f.endswith(".md"))
    if not files:
        print("no posts found in posts/")
        return 0

    posts = [parse(os.path.join(POSTS, f)) for f in files]
    posts.sort(key=lambda p: p["date"], reverse=True)

    os.makedirs(OUT, exist_ok=True)

    # Sidebar lists the five most recent, newest first.
    rail = "".join(
        '  <a class="sub" href="%s.html">%s</a>\n' % (p["slug"], html.escape(p["title"]))
        for p in posts[:5])

    total_images = 0

    for p in posts:
        total_images += copy_images(p["body"])
        body = render(p["body"])
        head = HEAD.format(
            title=html.escape(p["title"]) + " — Joe Solo",
            desc=html.escape(p.get("summary", p["title"])),
            crumb=html.escape(p["title"]),
            blog_active="",
            rail_posts=rail)
        article = (
            '  <div class="wrap post">\n'
            '    <article>\n'
            '      <p class="post-date">%s</p>\n'
            '      <h1>%s</h1>\n'
            '%s\n'
            '      <p class="post-back"><a href="index.html">&larr; All posts</a></p>\n'
            '    </article>\n'
            '  </div>\n'
        ) % (pretty_date(p["date"]), html.escape(p["title"]),
             "\n".join("      " + ln for ln in body.split("\n")))
        with open(os.path.join(OUT, p["slug"] + ".html"), "w",
                  encoding="utf-8", newline="\n") as fh:
            fh.write(head + article + FOOT)
        print("  built blog/%s.html" % p["slug"])

    # Index.
    cards = []
    for p in posts:
        summary = p.get("summary", "")
        cards.append(
            '      <a class="post-card" href="%s.html">\n'
            '        <p class="post-date">%s</p>\n'
            '        <h2>%s</h2>\n'
            '%s'
            '      </a>' % (
                p["slug"], pretty_date(p["date"]), html.escape(p["title"]),
                "        <p>%s</p>\n" % inline(summary) if summary else ""))

    head = HEAD.format(title="Blog — Joe Solo",
                       desc="Notes on tools, character art and shipping things.",
                       crumb="Blog", blog_active=" active", rail_posts=rail)
    index = (
        '  <div class="wrap post">\n'
        '    <h1>Blog</h1>\n'
        '    <p class="lede">Notes on tools, character art, and shipping things.</p>\n'
        '    <div class="post-list">\n%s\n    </div>\n'
        '  </div>\n' % "\n".join(cards))
    with open(os.path.join(OUT, "index.html"), "w",
              encoding="utf-8", newline="\n") as fh:
        fh.write(head + index + FOOT)

    print("  built blog/index.html")
    print("\n%d post(s), %d image(s)." % (len(posts), total_images))
    return 0


if __name__ == "__main__":
    sys.exit(build())
