# axis-3d-surveys

Pitch demo for [Axis 3D Surveys](https://axis3dsurveys.com/), a 3D laser
scanning and Scan-to-BIM practice in London. A Cloudflare Workers
static-assets site: everything served lives in `public/` and there is no build
step at deploy time.

Two tabs, wired together by the dark demo bar at the top of every page:

| Route | Page |
| --- | --- |
| `/` | The improved site – same logo, colours, typefaces, layout, photographs and words, with the defects fixed and every page rebuilt as fast static HTML (29 pages) |
| `/improvements/` | A plain-English page explaining what changed and what still needs the client's input |

The demo is deliberately hidden from search engines (`robots.txt`, `noindex`,
`X-Robots-Tag`) until it becomes the real site.

## Structure

```
public/                everything served
  index.html           home
  about-us/ contact-us/ our-services/ our-projects/
  service/<slug>/      six service pages
  project/<slug>/      fourteen project pages
  team/<slug>/         two team-member pages
  improvements/        the "what's improved" tab
  404.html             themed not-found page
  assets/css/site.css  the one stylesheet (the Kyber theme's values, hand-written)
  assets/js/site.js    mobile nav, carousels, counters, demo form
  assets/img/          WebP images converted from the site's originals, plus the logo
  fonts/               self-hosted Rajdhani and Mulish (from npm @fontsource)
  _headers  robots.txt  favicon.svg
tools/build.py         generates every page in public/ from the content in the file
tools/convert.js       converts the browser export's images (needs `sharp` and the export)
tools/img-manifest.json  sizes of the converted images, read by build.py
scripts/render_check.py  serves public/, screenshots it, checks local links
scripts/screenshots.js   full-page Playwright screenshots of every template at desktop and phone width, with an overflow check
wrangler.jsonc  package.json  package-lock.json
```

## Editing the site

All page content and templates live in `tools/build.py`. Edit it, regenerate,
and commit the generated pages with it:

```bash
python3 tools/build.py
```

Stylesheet and script are edited directly in `public/assets/`; the build stamps
a content hash onto their links so the long cache lifetime in `_headers` is safe.
The brand values (navy `#000080`, dark `#09162a`, red `#e31e24`, Rajdhani,
Mulish) sit at the top of `site.css` and nowhere else.

Images were converted once from the client's browser export ("Save as, Webpage,
Complete", one folder per page) with `tools/convert.js`: `npm i sharp` in a
scratch folder, then

```bash
NODE_PATH=<scratch>/node_modules node tools/convert.js <exportRoot> public/assets/img tools/img-manifest.json
```

Pass `-` as the export root to generate labelled placeholders for every slot
instead. New images can simply be added to `public/assets/img/` and an entry
appended to the manifest.

## Local development

```bash
npm install
npm run dev          # wrangler dev, serves public/
```

## Verification – before every push to main

```bash
python3 tools/build.py
npx wrangler deploy --dry-run
python3 scripts/render_check.py --dir public --pages index.html 404.html about-us/index.html
NODE_PATH=/opt/node22/lib/node_modules node scripts/screenshots.js
```

Then look at the screenshots in `.render-check/`: styles applied, fonts
loaded, layout intact, no overflow reported.

## Deployment

The repo connects to Cloudflare Workers Builds, so every push to `main` deploys
to production. Connect it once in the Cloudflare dashboard (Workers & Pages →
Create → Import a repository) if that has not been done yet.

## External resources

- The contact page embeds a Google Maps view of the office address and links
  to it on Google Maps.
- The footer credit links to the original designer's Instagram profile.

Everything else, fonts included, is served from this repo.

## What the export could not supply

- The About Us and Our Services pages were not in the export; both are
  assembled from copy that is (the homepage About section, the team pages and
  the six service cards).
- Daniel Tosuni's team page was not in the export; he appears on About Us with
  photo and name only.
- Three CSS background images (page banners, the "why choose us" photo, the
  contact panel) are not saved by a browser export; photographs from the
  client's own project pages stand in. The testimonials band uses the same
  file the live site does.
