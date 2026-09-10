# joesolodev.github.io

Tools by Joe Solo.

## Pages

- `index.html` — landing page, tool index
- `shipshape.html` — Shipshape Validator documentation
- `about.html` — bio, work galleries, resume
- `blog/` — **generated**, do not edit by hand
- `assets/site.css` — styles (Blueprint direction; palette from the brand kit)
- `assets/nav.js` — sidebar toggle and scroll-spy
- `assets/gallery.js` — lightbox for galleries and post images

Plain static HTML. Edit and push; GitHub Pages serves it.

## Writing a blog post

1. Create `posts/YYYY-MM-DD-some-slug.md`:

   ```
   ---
   title: What the post is called
   date: 2026-09-09
   summary: One line shown on the blog index. Optional.
   ---

   Body text in Markdown.

   ![A caption for the image](images/whatever.png)
   ```

2. Put any images in `posts/images/`.

3. Run the build:

   ```
   python build.py
   ```

   It writes `blog/<slug>.html` and `blog/index.html`, and copies images into
   `assets/blog/` at two sizes — a page-width version and a full-size one for
   the lightbox. Originals in `posts/images/` are left alone.

4. Commit and push. The post is live in a minute or so.

### Notes

- The filename date sets the post date and orders the index. Newest first.
- Markdown supported: headings, bold, italic, inline code, links, images,
  lists, blockquotes, fenced code, horizontal rules. That is deliberate — it
  covers what a post needs without a dependency.
- An image alone on its own line becomes a captioned figure that opens in a
  lightbox. The alt text is the caption.
- End the alt text with `{narrow}` for a screenshot of narrow UI, so it renders
  near its real width instead of being blown up across the column:
  `![The panel {narrow}](images/panel.png)`
- Pillow is needed only if a post has images: `pip install pillow`

## Cache busting

Asset links carry `?v=<commit>`. After changing CSS or JS, restamp them so
browsers pick the change up:

```
V=$(git rev-parse --short HEAD)
sed -i -E "s/\?v=[a-f0-9]+/?v=$V/g" index.html shipshape.html about.html
```
