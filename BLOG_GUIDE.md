# Blog post guide

How to turn a raw transcript into a post for this site. Joe records his thoughts
out loud, then pastes the transcript in. The goal is a post that reads like it
was written, not spoken, and still sounds like Joe.

Reference post: `posts/2026-11-12-the-unspoken-rule-of-aaa-game-art.md`

## The job

1. Clean up the transcript using the rules below. Keep the meaning and the
   opinions exactly as given. Don't add claims, facts or credits that aren't
   in the transcript.
2. Save it as `posts/YYYY-MM-DD-some-slug.md`, dated today unless Joe gives a
   date. The slug comes from the title.
3. Run `python build.py`, commit, push. It goes live in a minute or two.
4. Tell Joe the post is up and list the main things you cut or reworded, so he
   can put any of them back.

## Front matter

```
---
title: A plain, descriptive title
date: YYYY-MM-DD
summary: The post's hook in one sentence. Shown on the blog index.
---
```

## Shape

- **Open with the hook.** The first paragraph is the single strongest idea,
  stated straight out.
- **Second paragraph sets the scene.** If Joe mentions how far into the indie
  move he is, start it with "Today is day N of my move from AAA game development
  to indie." Never start with an introduction like "I'm Joe Solo, and...".
- **Short `##` section headings** that say what each part argues.
- **Short paragraphs**, two to four sentences each.
- **A `---` rule**, then the outro.

## Cut what makes it read like a transcript

- Self-introductions: "I'm Joe Solo", "hey guys", "welcome back".
- The credits list (Firefall, Call of Duty, Sony PlayStation, etc.).
- Calls to action meant for video: "give me a follow", "like and subscribe",
  "let me know in the comments".
- "Peace" and other spoken goodbyes.
- References to things said in other videos ("for all my talk about...",
  "like I said last time").
- Filler: "literally", "basically", "you know", "like", "kind of" when it adds
  nothing, "so yeah".
- Spoken repeats and restarts: "I know how to do all of these things, I can do
  all of these things" becomes "I can do all of these things".
- Stiff words that came from talking around a point: "utilized" becomes "used".

## Keep

- Joe's voice: casual, direct and opinionated. Lines like "Believe it or not",
  "Some people will tell you that's not true. It is." and "It's fun. It's
  awesome." stay.
- His examples and specifics, such as painting an orange with one-point light.
- His opinions as he states them. Don't soften or hedge them.

## Privacy

Don't name studios or clients Joe is under contract with. Say "an unannounced
studio" or "the indie team I'm working with".

## Outro

Always end with:

```
---

More from the rest of the journey soon. Check back here for regular blog updates.

<sign-off>
```

The sign-off is one of these two, picked at random each time:

- `Work hard, don't suck.`
- `Suck is not a style.`
