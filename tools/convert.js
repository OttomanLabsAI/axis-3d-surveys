// Convert the client's exported originals into right-sized WebP assets.
//
//   node tools/convert.js <exportRoot> public/assets/img tools/img-manifest.json
//
// <exportRoot> is the folder holding the browser export ("Save as, Webpage,
// Complete") with one "<Page title>_files" folder per page. Pass "-" to build
// labelled placeholders for every slot instead (used before the export
// arrived); a job whose source file is missing also falls back to a
// placeholder and is reported. Needs `sharp` (npm i sharp in a scratch folder,
// then run with NODE_PATH pointing at it).
const fs = require('fs'), path = require('path'); const sharp = require('sharp');
const [ROOT, OUT, MANIFEST] = process.argv.slice(2);
if (!OUT || !MANIFEST) { console.error('usage: node convert.js <exportRoot|-> <outDir> <manifestOut>'); process.exit(1); }

// Export folders (one per page).
const H = 'Axis 3D Surveys_files';
const PR = 'Our Projects – Axis 3D Surveys_files';
const S = {
  bim: 'Scan-to-BIM – Axis 3D Surveys_files',
  fourd: '4D BIM Planning – Axis 3D Surveys_files',
  asb: 'As-Built Verification – Axis 3D Surveys_files',
  mon: 'Building Movement Monitoring – Axis 3D Surveys_files',
  her: 'Heritage & Restoration Surveys – Axis 3D Surveys_files',
  twin: 'Digital Twin Creation – Axis 3D Surveys_files',
};
const P = {
  '4d-planning-contractor-slough': '4D Planning – Contractor, Slough – Axis 3D Surveys_files',
  'point-cloud-architect-reading': 'Point Cloud – Architect, Reading – Axis 3D Surveys_files',
  'point-cloud-contractor-chesham': 'Point Cloud – Contractor, Chesham – Axis 3D Surveys_files',
  'scan-to-bim-property-developer-soho': 'Scan-to-BIM – Property Developer, Soho – Axis 3D Surveys_files',
  'scan-to-bim-property-developer-south-london': 'Scan-to-BIM – Property Developer, South London – Axis 3D Surveys_files',
  'victorian-terrace-renovation-islington-london': 'Victorian Terrace Renovation – Islington, London – Axis 3D Surveys_files',
  '3d-walkthrough-for-flat-sale-manchester-city-centre': 'Setting out, 3 Storey Commercial Unit – Bedfont Lakes, London – Axis 3D Surveys_files',
  'as-built-deviation-flat-london': 'As Built Plans – Apartment, London – Axis 3D Surveys_files',
  'house-planning': 'Movement Monitoring – Grade II Building, Cambridge – Axis 3D Surveys_files',
  'heritage-scan-grade-ii-building-bath': 'Heritage Scan – Grade II Building, Bath – Axis 3D Surveys_files',
  'measured-survey-commercial-headquarters-london': 'Measured Survey – Commercial Headquarters, London – Axis 3D Surveys_files',
  'cottage-extension-cotswolds': 'Cottage Extension – London – Axis 3D Surveys_files',
  'rear-side-loft-extension-potters-bar-london': 'Rear_Side_Loft Extension – Potters Bar, London – Axis 3D Surveys_files',
  'rear-extension-watford-london': 'Rear Extension – Watford, London – Axis 3D Surveys_files',
};
const T = {
  endrit: 'Endrit Badallaj – Axis 3D Surveys_files',
  florjan: 'Florjan Mata – Axis 3D Surveys_files',
  daniel: 'Daniel Tosuni – Axis 3D Surveys_files',
};
const HQ = P['measured-survey-commercial-headquarters-london'];

// name: { src: [dir, file], w, h, cover: [w, h], q, enlarge, label, pos }
//   w/h = fit inside (never enlarged unless `enlarge`);  cover = exact crop;  label/pos = placeholder caption
const jobs = {
  // Home
  'hero':        { src: [H, 'Hero-NEW-1.png'], w: 792, label: 'Homepage hero photograph' },
  'hero-sm':     { src: [H, 'Hero-NEW-1.png'], w: 520, label: 'Homepage hero photograph' },
  'svc-scan-to-bim':   { src: [H, 'Scan-to-Bim-600x340.png'], cover: [600, 340], label: 'Scan-to-BIM' },
  'svc-4d':            { src: [H, '4D-Synchro-600x340.jpg'], cover: [600, 340], label: '4D BIM Planning' },
  'svc-as-built':      { src: [H, 'AS-BUILT-600x340.png'], cover: [600, 340], label: 'As-Built Verification' },
  'svc-monitoring':    { src: [H, 'Building-Movement-monitoring-530x340.png'], cover: [600, 340], enlarge: true, label: 'Building Movement Monitoring' },
  'svc-heritage':      { src: [H, 'Heritage-Restoration-Surveys-489x340.png'], cover: [600, 340], enlarge: true, label: 'Heritage & Restoration Surveys' },
  'svc-digital-twin':  { src: [H, 'Digital-Twin-600x340.png'], cover: [600, 340], label: 'Digital Twin Creation' },
  'about-home':  { src: [H, 'HOME.02-e1760360009839.jpg'], w: 800, label: 'About us photograph' },
  // The live site loads these three as CSS backgrounds, which a browser export cannot save.
  // The testimonials band is the site's own file (same name in the HQ project); the other two are stand-ins from the client's project photos.
  'testimonials-bg': { src: [HQ, 'WhatsApp-Image-2025-12-02-at-16.36.43.jpeg'], w: 1600, q: 62, label: 'Testimonials background' },
  'why-photo':   { src: [HQ, 'WhatsApp-Image-2025-12-02-at-20.50.23.jpeg'], w: 900, q: 76, pos: 'center', label: 'Why choose us photograph' },
  'contact-bg':  { src: [P['scan-to-bim-property-developer-soho'], 'aa1.jpg'], w: 1000, q: 68, pos: 'center', label: 'Contact panel background' },
  // Page banner: the live site hot-links the theme vendor's demo image; a client photo stands in.
  'band-bg':     { src: [HQ, 'WhatsApp-Image-2025-12-02-at-16.36.43-5.jpeg'], cover: [1600, 720], q: 66, enlarge: true, pos: 'top', label: 'Page banner background' },
  'band-bg-sm':  { src: [HQ, 'WhatsApp-Image-2025-12-02-at-16.36.43-5.jpeg'], cover: [800, 360], q: 66, pos: 'top', label: 'Page banner background' },
  // Service pages: main image + secondary image
  'svc-scan-to-bim-1':  { src: [S.bim, 'Scan-to-Bim.png'], w: 1000, label: 'Scan-to-BIM' },
  'svc-scan-to-bim-2':  { src: [S.bim, 'WhatsApp-Image-2025-12-06-at-17.50.36-1024x460.jpeg'], w: 1024, label: 'Scan-to-BIM' },
  'svc-4d-1':           { src: [S.fourd, '4D-Synchro.jpg'], w: 1200, label: '4D BIM Planning' },
  'svc-4d-2':           { src: [S.fourd, 'DATA-CENTRE-1024x576.jpg'], w: 1024, label: '4D BIM Planning' },
  'svc-as-built-1':     { src: [S.asb, 'AS-BUILT.png'], w: 872, label: 'As-Built Verification' },
  'svc-as-built-2':     { src: [S.asb, 'As-Built-Verification-1024x499.png'], w: 1024, label: 'As-Built Verification' },
  'svc-monitoring-1':   { src: [S.mon, 'Building-Movement-monitoring.png'], w: 530, label: 'Building Movement Monitoring' },
  'svc-heritage-1':     { src: [S.her, 'Heritage-Restoration-Surveys.png'], w: 489, label: 'Heritage & Restoration Surveys' },
  'svc-heritage-2':     { src: [S.her, 'Heritage-Restoration-Surveys-1-1024x367.png'], w: 1024, label: 'Heritage & Restoration Surveys' },
  'svc-digital-twin-1': { src: [S.twin, 'Digital-Twin.png'], w: 650, label: 'Digital Twin Creation' },
  'svc-digital-twin-2': { src: [S.twin, 'Digital-Twin-1024x576.jpg'], w: 1024, label: 'Digital Twin Creation' },
  // Team
  'team-endrit':  { src: [T.endrit, 'Endrit-B.-Copy.jpg'], cover: [600, 700], label: 'Endrit Badallaj' },
  'team-florjan': { src: [T.florjan, 'Untitled-design-2.jpg'], cover: [600, 700], enlarge: true, label: 'Florjan Mata' },
  'team-daniel':  { src: [T.daniel, 'Danjel-Tosuni.jpg'], cover: [600, 700], label: 'Daniel Tosuni' },
};
// Project grid thumbnails (the 600x700 crops WordPress made for the projects page)
const thumbs = {
  '4d-planning-contractor-slough': [PR, 'Data-centre-slough-1-600x700.png'],
  'point-cloud-architect-reading': [PR, 'N1-600x700.png'],
  'point-cloud-contractor-chesham': [PR, '5-600x700.png'],
  'scan-to-bim-property-developer-soho': [PR, 'Project-4-Scan-600x700.png'],
  'scan-to-bim-property-developer-south-london': [PR, 'Scan-to-BIM-Property-Developer-South-London-600x695.jpg'],
  'victorian-terrace-renovation-islington-london': [PR, '3-8-600x700.png'],
  '3d-walkthrough-for-flat-sale-manchester-city-centre': [PR, 'as-600x700.jpg'],
  'as-built-deviation-flat-london': [PR, '1-2-600x700.jpg'],
  'house-planning': [PR, '2-1.png'],
  'heritage-scan-grade-ii-building-bath': [PR, '1-6-600x700.png'],
  'measured-survey-commercial-headquarters-london': [HQ, 'WhatsApp-Image-2025-12-02-at-16.36.43-5.jpeg'],  // the grid used a 1405x464 panorama that cannot fill a portrait card; a photo from the same project stands in
  'cottage-extension-cotswolds': [PR, '1-4-600x700.png'],
  'rear-side-loft-extension-potters-bar-london': [PR, '3-4-600x662.png'],
  'rear-extension-watford-london': [PR, '1-5-600x700.png'],
};
for (const [slug, src] of Object.entries(thumbs)) jobs['proj-' + slug] = { src, cover: [600, 700], enlarge: true, label: slug };
// Project pages: hero (the post thumbnail) + gallery (the slider images, each once)
const pages = {
  '4d-planning-contractor-slough': ['Data-centre-slough-1.png', ['Data-centre-slough-1.png', 'Data-centre-slough-Synchro.png']],
  'point-cloud-architect-reading': ['N1.png', ['N3.png', 'N1.png', 'N2.png']],
  'point-cloud-contractor-chesham': ['5.png', ['2-scaled.png', 'Project-3.2.png', '3-1.png', '1-scaled.png']],
  'scan-to-bim-property-developer-soho': ['Project-4-Scan.png', ['Soho_Revit-Model_LOD300.png', 'Project-4-Scan.png', 'Project-4-LOD200-Revit-Model.png', 'aa1.jpg', '3.png']],
  'scan-to-bim-property-developer-south-london': ['Scan-to-BIM-Property-Developer-South-London.jpg', ['Scan-to-BIM-Property-Developer-South-London-1.jpg', 'Scan-to-BIM-Property-Developer-South-London.jpg', 'Scan-to-BIM-Property-Developer-South-London1.jpg', 'Scan-to-BIM-Property-Developer-South-Londonn.jpg', 'Scan-to-BIM-Property-Developer-South-Londonnn.jpg', 'Scan-to-BIM-Property-Developer-South-Londonmn.jpg', 'Scan-to-BIM-Property-Developer-South-Londonnnn.jpg']],
  'victorian-terrace-renovation-islington-london': ['3-8.png', ['3-8.png', '1-8.png', 'Islington-Flat-1.png']],
  '3d-walkthrough-for-flat-sale-manchester-city-centre': ['as.jpg', ['DWG-577x1024.jpg', 'CS20-Scanner-577x1024.jpg', 'Staking-out-577x1024.jpg', 'as-577x1024.jpg']],
  'as-built-deviation-flat-london': ['1-2.jpg', ['3-2.jpg', '1-2.jpg', '2-3.jpg']],
  'house-planning': ['2-1.png', ['3-2.png', '1-1.png', '2-1.png']],
  'heritage-scan-grade-ii-building-bath': ['1-6.png', ['3-6.png', '1-6.png', '2-5.png']],
  'measured-survey-commercial-headquarters-london': ['WhatsApp-Image-2025-12-02-at-16.36.43-3.jpeg', ['WhatsApp-Image-2025-12-02-at-20.50.23.jpeg', 'WhatsApp-Image-2025-12-02-at-16.36.42.jpeg', 'WhatsApp-Image-2025-12-02-at-16.36.43.jpeg', 'WhatsApp-Image-2025-12-02-at-16.36.43-1.jpeg', 'WhatsApp-Image-2025-12-02-at-16.36.43-2.jpeg', 'WhatsApp-Image-2025-12-02-at-16.36.43-3.jpeg', 'WhatsApp-Image-2025-12-02-at-16.36.43-4.jpeg', 'WhatsApp-Image-2025-12-02-at-16.36.43-5.jpeg', 'WhatsApp-Image-2025-12-02-at-20.50.23-1.jpeg']],
  'cottage-extension-cotswolds': ['1-4.png', ['3-3.png', '1-4.png', '2-2.png']],
  'rear-side-loft-extension-potters-bar-london': ['3-4.png', ['3-4.png', '1-1.jpg', '2-3.png']],
  'rear-extension-watford-london': ['1-5.png', ['4.jpg', '1-5.png', '3-5.png', '1-1.jpg']],
};
for (const [slug, [hero, gallery]] of Object.entries(pages)) {
  jobs[`pp-${slug}-hero`] = { src: [P[slug], hero], w: 1200, h: 1200, label: slug };
  gallery.forEach((f, i) => { jobs[`pp-${slug}-${String(i + 1).padStart(2, '0')}`] = { src: [P[slug], f], w: 1200, h: 1000, q: 78, label: slug }; });
}

function placeholderSvg(w, h, label, seed, pos) {
  let s = seed >>> 0;
  const rnd = () => { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; };
  const dots = [];
  const blocks = [[0.08, 0.30, 0.34, 0.50], [0.42, 0.24, 0.28, 0.62], [0.72, 0.36, 0.22, 0.44]];
  const push = (x, y, big) => {
    const blue = rnd() < 0.18;
    dots.push(`<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="${(big ? 2.2 : 1.3) * Math.max(0.6, w / 900)}" fill="${blue ? '#6ea8ff' : '#fff'}" fill-opacity="${blue ? 0.9 : (0.25 + rnd() * 0.5).toFixed(2)}"/>`);
  };
  for (const [bx, by, bw, bh] of blocks) {
    const x0 = bx * w, x1 = (bx + bw) * w, y1 = h - by * h, y0 = y1 - bh * h;
    const per = Math.round((x1 - x0 + y1 - y0) / 6);
    for (let i = 0; i < per; i++) {
      const t = rnd(), edge = rnd(), j = () => (rnd() - 0.5) * 6;
      if (edge < 0.3) push(x0 + t * (x1 - x0) + j(), y0 + j(), true);
      else if (edge < 0.5) push(x0 + t * (x1 - x0) + j(), y1 + j(), false);
      else if (edge < 0.75) push(x0 + j(), y0 + t * (y1 - y0) + j(), true);
      else push(x1 + j(), y0 + t * (y1 - y0) + j(), true);
    }
    const fill = Math.round(((x1 - x0) * (y1 - y0)) / 2600);
    for (let i = 0; i < fill; i++) push(x0 + rnd() * (x1 - x0), y0 + rnd() * (y1 - y0), false);
  }
  const fs_ = Math.max(11, Math.round(Math.min(w, h) / 34));
  const text = `Placeholder – ${label.replace(/&/g, '&amp;')} (your photo goes here)`;
  const capY = pos === 'top' ? 0 : pos === 'center' ? Math.round(h / 2 - fs_ * 1.3) : h - fs_ * 2.6;
  const anchor = pos === 'center' ? ` text-anchor="middle" x="${w / 2}"` : ` x="${fs_}"`;
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}" viewBox="0 0 ${w} ${h}">
<defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#16263c"/><stop offset="1" stop-color="#09162a"/></linearGradient>
<pattern id="p" width="40" height="40" patternUnits="userSpaceOnUse"><path d="M40 0H0V40" fill="none" stroke="#fff" stroke-opacity=".07"/></pattern></defs>
<rect width="${w}" height="${h}" fill="url(#g)"/><rect width="${w}" height="${h}" fill="url(#p)"/>
${dots.join('')}
<rect x="0" y="${capY}" width="${w}" height="${fs_ * 2.6}" fill="#000" fill-opacity=".35"/>
<text${anchor} y="${capY + fs_ * 1.6}" font-family="Arial, Helvetica, sans-serif" font-size="${fs_}" fill="#fff" fill-opacity=".8">${text}</text>
</svg>`;
}

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const manifest = {}; let total = 0, fromExport = 0, placeholders = 0, seed = 7;
  for (const [name, o] of Object.entries(jobs)) {
    let img = null, source = null;
    if (ROOT !== '-' && o.src) {
      const src = path.join(ROOT, o.src[0], o.src[1]);
      if (fs.existsSync(src)) { img = sharp(src, { animated: false, limitInputPixels: false }).rotate(); source = src; }
      else console.log('MISSING', name, '->', src);
    }
    if (!img) {
      if (ROOT !== '-' && name.startsWith('pp-') && !/-hero$/.test(name)) continue;  // a missing gallery image is simply left out
      const [w, h] = o.cover || [o.w, o.h || o.w];
      img = sharp(Buffer.from(placeholderSvg(w, h, o.label || name, seed += 101, o.pos)));
      placeholders++;
    } else fromExport++;
    if (o.cover) img = img.resize(o.cover[0], o.cover[1], { fit: 'cover', position: 'attention', withoutEnlargement: !o.enlarge });
    else img = img.resize({ width: o.w, height: o.h, fit: 'inside', withoutEnlargement: !o.enlarge });
    const out = path.join(OUT, name + '.webp');
    const info = await img.webp({ quality: o.q || 80, effort: 5 }).toFile(out);
    manifest[name] = { file: name + '.webp', width: info.width, height: info.height, bytes: info.size, placeholder: !source };
    total += info.size;
  }
  // Logo: trim the whitespace around the wordmark, then a light variant (dark pixels -> white) for the footer
  const logoSrc = ROOT !== '-' ? path.join(ROOT, H, 'Untitled-design.png') : null;
  if (logoSrc && fs.existsSync(logoSrc)) {
    const trimmed = await sharp(logoSrc).trim({ threshold: 20 }).resize({ width: 560, withoutEnlargement: true }).png().toBuffer();
    const l1 = await sharp(trimmed).png({ compressionLevel: 9, palette: true }).toFile(path.join(OUT, 'logo.png'));
    const { data, info } = await sharp(trimmed).ensureAlpha().raw().toBuffer({ resolveWithObject: true });
    const light = Buffer.from(data);
    for (let i = 0; i < light.length; i += 4) {
      const r = light[i], g = light[i + 1], b = light[i + 2], a = light[i + 3];
      if (a > 0 && Math.max(r, g, b) < 90) { light[i] = 255; light[i + 1] = 255; light[i + 2] = 255; }
    }
    const l2 = await sharp(light, { raw: { width: info.width, height: info.height, channels: 4 } }).png({ compressionLevel: 9 }).toFile(path.join(OUT, 'logo-light.png'));
    manifest['logo'] = { file: 'logo.png', width: l1.width, height: l1.height, bytes: l1.size, placeholder: false };
    manifest['logo-light'] = { file: 'logo-light.png', width: l2.width, height: l2.height, bytes: l2.size, placeholder: false };
    total += l1.size + l2.size;
  }
  fs.writeFileSync(MANIFEST, JSON.stringify(manifest, null, 1));
  console.log(`wrote ${Object.keys(manifest).length} files, ${(total / 1024).toFixed(0)} KB total (${fromExport} from the export, ${placeholders} placeholders)`);
  const big = Object.entries(manifest).sort((a, b) => b[1].bytes - a[1].bytes).slice(0, 8);
  for (const [n, m] of big) console.log(`  ${String(m.bytes).padStart(7)} ${m.width}x${m.height} ${n}`);
})().catch(e => { console.error(e); process.exit(1); });
