# CLAUDE.md

Standing policy for this repository. Read it before making any change here.

## What this repo is

A Cloudflare Workers static-assets site holding the pitch demo for Axis 3D
Surveys. Everything served lives in `public/` and there is no build step at
deploy time - the files in that directory are the site. The repo is connected
to Cloudflare Workers Builds, so **every push to `main` deploys to production**.

```
public/            everything served (home, about, contact, services, projects,
                   team, improvements, 404, assets, fonts, _headers, robots)
tools/build.py     generates the pages in public/ from the content it contains
tools/convert.js   one-off image conversion from the client's browser export
tools/social.js    renders the share thumbnail public/assets/img/social.jpg
scripts/render_check.py  render check used before every push
scripts/screenshots.js   full-page screenshots of every template, desktop and phone
wrangler.jsonc     assets-only config, no Worker script
package.json       wrangler devDependency + build/dev/deploy/check scripts
```

The pages are generated: edit `tools/build.py` (content and templates) or the
files in `public/assets/`, run `python3 tools/build.py`, and commit the
regenerated pages together with the change. Never hand-edit a generated page.

## Local development

```bash
npm install
npm run dev          # wrangler dev
```

## Verification - before every push to main

1. `python3 tools/build.py` (the generated pages must be current)
2. `npx wrangler deploy --dry-run`
3. `python3 scripts/render_check.py --dir public --pages index.html 404.html`
   and `NODE_PATH=/opt/node22/lib/node_modules node scripts/screenshots.js`,
   then inspect the screenshots: styles applied, fonts loaded, layout intact,
   no overflow reported.

Never leave pushed work unverified or half-finished. Work in small, complete
batches: implement, verify, commit, push.

## Git and release workflow

- Before committing: `git config user.name "Fid" && git config user.email "fid_kk@proton.me"`
- Develop on the working branch and push there first. Release verified work by
  fast-forwarding `main` onto it and pushing `main`.
- Every push to `main` is a release. Versions are an ascending `vMAJOR.MINOR`
  sequence starting at `v1.0`; every push bumps the minor regardless of size. A
  major bump is reserved for a ground-up overhaul.
- With every push to `main`, provide release-tag text in the reply, in exactly
  this shape. The owner creates the GitHub release manually - **never push tags**:

  ```
  Tag: v<next>  —  Title: <five to nine words, plain and evocative>
  Description: <one to three sentences of editorial prose describing what changed
  from the owner's point of view — outcomes, not implementation. No bullet lists,
  no jargon, no file names.>
  ```

- Append the release line to the ledger below as part of the same push.
- Commit messages: descriptive imperative first line (what the change does, not
  "update X"), then a short prose body; dash bullets are fine there. One commit
  per coherent piece of work; several may share a push, but each push gets
  exactly one version entry.
- Never include model names, AI attribution trailers, session links, or other
  tooling identifiers in commit messages, titles, or code.

## The site itself

The improved site keeps the client's brand exactly: the logo, the customiser's
navy `#000080`, the theme's dark `#09162a`, the hero's red `#e31e24`, Rajdhani
headings and Mulish body copy, their photographs and their words. The
`/improvements/` page lists every deliberate change; anything not on that list
should not be "improved" quietly. The demo bar is demo chrome and is removed
when the site goes live. The demo stays `noindex` until then. No pricing
appears anywhere in this repo.

## Release ledger

| Version | Title | Description |
| --- | --- | --- |
| v1.0 | Axis 3D Surveys demo: same brand, fixed and faster | A rebuilt Axis 3D Surveys site in the company's own logo, colours and typefaces, with the dead links, stray template text, borrowed theme images and footer address fixed, and every page loading at a fraction of the weight. A second tab explains each improvement in plain terms and lists what still needs the client's input. |
| v1.1 | A picture for every shared link | Sharing any page of the demo on WhatsApp, LinkedIn or Facebook now shows a proper preview card in the company's colours, with the logo, the headline and the phone number, instead of a blank box or a cropped photo. |
