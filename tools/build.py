#!/usr/bin/env python3
"""Generate public/ for the Axis 3D Surveys demo.

Content lives in this file; templates are plain Python strings. Run it after
editing and commit the generated pages alongside it:

    python3 tools/build.py

Nothing here runs at deploy time: Cloudflare serves public/ as-is.

Every sentence below comes from the browser export of axis3dsurveys.com
(25 pages). The About Us and Our Services pages were not in the export and
are assembled from copy that is; the improvements page says so.
"""
import hashlib
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PUBLIC = ROOT / "public"
IMG = PUBLIC / "assets" / "img"

BASE_URL = ""  # set to the live origin (https://axis3dsurveys.com) at go-live for canonical/OG URLs
YEAR = 2026

SITE = {
    "name": "Axis 3D Surveys",
    "legal": "Axis 3D Surveys",
    "phone": "07460 844015",
    "tel": "+447460844015",
    "email": "info@axis3dsurveys.com",
    "address": ["18 Ongar House, Baxter Road", "London N1 3ND"],
    "live": "https://axis3dsurveys.com/",
    "tagline": "Precise 3D laser scanning, BIM modelling and as-built verification for architects, engineers and contractors across the UK.",
}

# ---------------------------------------------------------------- icons
ICONS = {
    "phone": '<path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.13.96.37 1.9.72 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.91.35 1.85.59 2.81.72A2 2 0 0 1 22 16.92z"/>',
    "mail": '<path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/>',
    "pin": '<path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/>',
    "menu": '<line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/>',
    "x": '<line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>',
    "left": '<polyline points="15 18 9 12 15 6"/>',
    "right": '<polyline points="9 18 15 12 9 6"/>',
    "check": '<polyline points="20 6 9 17 4 12"/>',
    "bim": '<path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/>',
    "plan": '<rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/>',
    "verify": '<polyline points="9 11 12 14 22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/>',
    "twin": '<polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/>',
    "monitor": '<polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>',
    "heritage": '<line x1="3" y1="22" x2="21" y2="22"/><line x1="6" y1="18" x2="6" y2="11"/><line x1="10" y1="18" x2="10" y2="11"/><line x1="14" y1="18" x2="14" y2="11"/><line x1="18" y1="18" x2="18" y2="11"/><polygon points="12 2 20 7 4 7"/>',
    "target": '<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>',
    "scan": '<path d="M8 3H5a2 2 0 0 0-2 2v3m18 0V5a2 2 0 0 0-2-2h-3m0 18h3a2 2 0 0 0 2-2v-3M3 16v3a2 2 0 0 0 2 2h3"/>',
    "sectors": '<rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/>',
    "clock": '<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>',
    "zap": '<polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>',
    "smartphone": '<rect x="5" y="2" width="14" height="20" rx="2" ry="2"/><line x1="12" y1="18" x2="12.01" y2="18"/>',
    "eye": '<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/>',
    "tool": '<path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/>',
    "type": '<polyline points="4 7 4 4 20 4 20 7"/><line x1="9" y1="20" x2="15" y2="20"/><line x1="12" y1="4" x2="12" y2="20"/>',
    "globe": '<circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>',
    "edit": '<path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>',
    "shield": '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><polyline points="9 12 11 14 15 10"/>',
}


def icon(name, cls="i", label=None):
    aria = f' role="img" aria-label="{esc(label)}"' if label else ' aria-hidden="true"'
    return f'<svg class="{cls}" viewBox="0 0 24 24"{aria}>{ICONS[name]}</svg>'


def esc(s):
    return html.escape(str(s), quote=True)


# ---------------------------------------------------------------- images
MANIFEST = json.loads((ROOT / "tools" / "img-manifest.json").read_text())


def img(key, alt, cls="", lazy=True, sizes=None, srcset=None, w=None, h=None):
    m = MANIFEST[key]
    attrs = [f'src="/assets/img/{m["file"]}"', f'width="{w or m["width"]}"', f'height="{h or m["height"]}"', f'alt="{esc(alt)}"']
    if srcset:
        attrs.append('srcset="' + ", ".join(f'/assets/img/{MANIFEST[k]["file"]} {MANIFEST[k]["width"]}w' for k in srcset) + '"')
    if sizes:
        attrs.append(f'sizes="{sizes}"')
    if cls:
        attrs.append(f'class="{cls}"')
    if lazy:
        attrs.append('loading="lazy" decoding="async"')
    else:
        attrs.append('fetchpriority="high"')
    return "<img " + " ".join(attrs) + ">"


# ---------------------------------------------------------------- content
SERVICES = [
    {
        "slug": "scan-to-bim", "title": "Scan-to-BIM", "icon": "bim", "thumb": "svc-scan-to-bim", "img1": "svc-scan-to-bim-1", "img2": "svc-scan-to-bim-2",
        "short": "We transform 3D scans into intelligent BIM models, giving architects, engineers, and contractors accurate as-built data for flawless design and coordination.",
        "desc": "Scan-to-BIM by Axis 3D Surveys: Leica, Trimble and FARO laser scans of existing buildings converted into precise Revit or ArchiCAD models, up to LOD 400, across London and the UK.",
        "overview": [
            "Our Scan-to-BIM service transforms real-world buildings into intelligent digital models. Using Leica, Trimble and FARO scanners, we capture high-resolution point clouds of existing conditions and convert them into precise Revit or ArchiCAD models.",
            "Whether you’re planning new designs, coordinating MEP systems, or verifying construction accuracy, our BIM deliverables provide a solid foundation for every stage of your project.",
        ],
        "faq": [
            ("How detailed can the BIM model be?", "We can deliver models up to LOD 400, including architectural, structural, and MEP elements, tailored to your project needs."),
            ("Can you model only specific areas of interest?", "Yes, we can produce full-building models or partial models (e.g., MEP spaces, façades) to save time and cost."),
            ("Do I need BIM for a home extension and refurbishment?", "While not essential, a BIM model ensures your architect works from exact measurements, preventing errors and delays in construction."),
        ],
    },
    {
        "slug": "real-estate-walkthroughs", "title": "4D BIM Planning", "icon": "plan", "thumb": "svc-4d", "img1": "svc-4d-1", "img2": "svc-4d-2",
        "short": "SYNCHRO 4D BIM planning that enhances construction sequencing, project collaboration and programme management for commercial and data centre developments across Europe.",
        "desc": "4D BIM Planning by Axis 3D Surveys: your BIM model combined with the construction programme in SYNCHRO 4D and Autodesk Construction Cloud, for commercial developments and data centres across Europe.",
        "overview": [
            "4D BIM Planning combines your BIM model with the construction programme to create a visual representation of the build sequence, enabling project teams to plan, coordinate and monitor construction activities with greater confidence.",
            "We deliver accurate 4D BIM solutions using SYNCHRO 4D and Autodesk Construction Cloud (ACC), supporting collaboration between designers, contractors and clients throughout the project lifecycle.",
            "Our experience includes supporting complex commercial developments and data centres across Europe, where effective sequencing, multidisciplinary coordination and programme certainty are essential to successful project delivery.",
        ],
        "faq": [
            ("How does 4D BIM improve data centre construction?", "4D BIM enables project teams to visualise every stage of construction before work begins, helping to coordinate structural, architectural and MEP activities. This reduces sequencing conflicts, improves programme certainty and supports the efficient delivery of complex data centre projects."),
            ("Can 4D BIM be integrated with Autodesk Construction Cloud (ACC)?", "Yes. Our 4D BIM models can be delivered and managed through Autodesk Construction Cloud, providing a central platform where clients, consultants and contractors can review construction sequences, monitor progress and collaborate using the latest project information."),
            ("Why is 4D BIM important for hyperscale data centres?", "Hyperscale data centres involve multiple contractors working within demanding programmes and strict quality requirements. 4D BIM provides clear construction sequencing and visual planning, improving communication, reducing site coordination issues and helping projects remain on schedule."),
        ],
    },
    {
        "slug": "as-built-verification", "title": "As-Built Verification", "icon": "verify", "thumb": "svc-as-built", "img1": "svc-as-built-1", "img2": "svc-as-built-2",
        "short": "Ensure what’s built matches the design. Our scans verify dimensions and layouts, reducing costly errors and rework.",
        "desc": "As-Built Verification by Axis 3D Surveys: laser scans that confirm what has been built matches the design, catching discrepancies before they become costly rework.",
        "overview": [
            "With As-Built Verification, we ensure that what’s been built on site matches the original design and plans. Our scans provide a true record of completed works, identifying discrepancies before they become costly rework.",
            "Contractors, engineers, and owners benefit from having an independent, precise validation of construction accuracy.",
        ],
        "faq": [
            ("How does this reduce rework?", "We overlay scan data against the design model to spot deviations early, avoiding expensive corrections later."),
            ("Can you provide progressive verification during construction?", "Yes, we can re-scan at key milestones, tracking accuracy throughout the project lifecycle."),
            ("Why would I need this for my renovation?", "It guarantees your builder delivers exactly what was promised, no surprises with dimensions, finishes, or layouts."),
        ],
    },
    {
        "slug": "building-movement-monitoring", "title": "Building Movement Monitoring", "icon": "monitor", "thumb": "svc-monitoring", "img1": "svc-monitoring-1", "img2": None,
        "short": "Track structural shifts over time with precise scanning, providing early warnings and peace of mind for owners and engineers.",
        "desc": "Building Movement Monitoring by Axis 3D Surveys: repeat laser scans that track structural shifts and settlement to millimetre accuracy for high-rise, heritage and excavation-adjacent buildings.",
        "overview": [
            "Our Building Movement Monitoring service tracks structural shifts and settlement with millimetre accuracy. By performing repeat scans over time, we identify even the smallest deformations in walls, columns, or foundations.",
            "Ideal for high-rise buildings, heritage sites, or structures near tunnelling and excavation, this service provides early warnings that protect safety and reduce liability.",
        ],
        "faq": [
            ("How frequently should monitoring be carried out?", "Frequency depends on project risk: for tunnelling sites, daily scans may be required; for heritage buildings, every 1–3 months is prudent."),
            ("Can reports be automated?", "Yes, we can deliver comparative deformation reports after each scan cycle, highlighting changes instantly."),
            ("What happens if you detect movement?", "We notify you immediately with a detailed report, allowing engineers to take preventive measures before damage occurs."),
        ],
    },
    {
        "slug": "heritage-restoration-surveys", "title": "Heritage & Restoration Surveys", "icon": "heritage", "thumb": "svc-heritage", "img1": "svc-heritage-1", "img2": "svc-heritage-2",
        "short": "Capture historic buildings in 3D detail for preservation, documentation, and sensitive refurbishment.",
        "desc": "Heritage & Restoration Surveys by Axis 3D Surveys: non-contact 3D laser scanning of historic buildings for restoration, conservation and documentation.",
        "overview": [
            "Preserving historic architecture requires accuracy without intrusion. Our 3D laser scanning captures intricate details of heritage buildings without physical contact, producing digital records for restoration, conservation, or documentation.",
            "Architects and conservationists gain precise drawings and models, while owners can ensure their property is documented for future generations.",
        ],
        "faq": [
            ("How detailed are the scans for ornate features?", "Our machines capture between 1–2mm error in scanning; from the point cloud we can create an identical 3D element of ornate features such as friezes, external cornices, and art installations."),
            ("Will scanning damage the building?", "No, laser scanning is completely non-invasive, making it ideal for fragile sites."),
            ("What’s the benefit for me?", "You’ll have an accurate 3D record of your property, useful for insurance, restoration, and compliance with planning authorities."),
        ],
    },
    {
        "slug": "digital-twin-creation", "title": "Digital Twin Creation", "icon": "twin", "thumb": "svc-digital-twin", "img1": "svc-digital-twin-1", "img2": "svc-digital-twin-2",
        "short": "Full-scale digital replicas for facility management, maintenance planning, and long-term asset tracking.",
        "desc": "Digital Twin Creation by Axis 3D Surveys: a laser-scanned BIM model of your building integrated with sensors, IoT data or facilities management systems, built in Autodesk Tandem.",
        "overview": [
            "A Digital Twin is a living, data-rich 3D model that mirrors your building in real time. Starting with a laser scan, we build a BIM model and integrate it with sensors, IoT data, or facilities management systems.",
            "The result is a powerful tool for monitoring performance, planning maintenance, and managing assets across the entire building lifecycle.",
        ],
        "faq": [
            ("Can I use the twin for maintenance scheduling?", "Yes, we link assets like HVAC, lifts, and lighting to your twin, enabling predictive maintenance."),
            ("How is a twin different from a BIM model?", "A BIM model is static; a digital twin is dynamic, continuously updated with live or periodic data on any assets within your building. We use Autodesk Tandem to create the Digital Twin."),
            ("Is this useful for smaller properties?", "For large portfolios, it’s most valuable. But even small commercial buildings benefit from having a twin for lifecycle management and planning upgrades."),
        ],
    },
]

PROJECTS = [
    {"slug": "4d-planning-contractor-slough", "title": "4D Planning – Contractor, Slough", "cat": "Scan-to-BIM", "loc": "Slough, England", "year": "2025",
     "overview": ["Axis 3D Surveys developed a 4D BIM model using SYNCHRO 4D to simulate the construction sequence of a new 60 MW hyperscale data centre in Slough. The model integrated the BIM design with the construction programme, providing a clear visual representation of each phase of the build. This enabled project teams to coordinate structural, architectural and MEP activities, improve site logistics and communicate the construction sequence to all stakeholders throughout the project."],
     "challenges": ["Coordinating structural/civils, architectural and MEP installations within a live data centre campus while maintaining a strict construction programme and uninterrupted adjacent operations.",
                    "Integrating Synchro 4D with Autodesk Construction Cloud (ACC) to visualise construction sequencing, improve multidisciplinary coordination and identify programme risks before work commenced."]},
    {"slug": "point-cloud-architect-reading", "title": "Point Cloud – Architect, Reading", "cat": "As-Built Verification, Scan-to-BIM", "loc": "Reading, England", "year": "2026",
     "overview": ["Full external property and surrounding street point cloud model provided to Architect. Point cloud model was required for the creation of an As-built set of drawings for their Client."],
     "challenges": ["Limited access to property due to tenants, assumed flat layouts.",
                    "Capturing complex roof structure where proposed works were going to be undertaken, rigorous accuracy required when modelling in 3D."]},
    {"slug": "point-cloud-contractor-chesham", "title": "Point Cloud – Contractor, Chesham", "cat": "As-Built Verification", "loc": "Chesham, England", "year": "2026",
     "overview": ["Full property survey and walkthrough for Contractor client. Deliverables included: Full .RCP / .RCS & E57 File for contractor, in order to design a proposed scheme for their development."],
     "challenges": ["Capturing complex roof structure from internal, which was the critical zone for the contractor. We gained access via loft to give a detailed view of the internal area."]},
    {"slug": "scan-to-bim-property-developer-soho", "title": "Scan-to-BIM – Property Developer, Soho", "cat": "Scan-to-BIM", "loc": "Soho, London", "year": "2026",
     "overview": ["Full survey and walkthrough for developer client’s commercial unit. Deliverables included LOD300 Revit model, plans, sections, elevations and site topography."],
     "challenges": ["Modelling M&E units with M&E family types in Revit to an accurate degree."]},
    {"slug": "scan-to-bim-property-developer-south-london", "title": "Scan-to-BIM – Property Developer, South London", "cat": "Scan-to-BIM", "loc": "South London", "year": "2026",
     "overview": ["Full property survey and walkthrough for developer client. Deliverables included LOD200 Revit model, plans, sections, elevations and site topography."],
     "challenges": ["Limited access to property due to tenants, assumed flat layouts.",
                    "Capturing complex roof structure where a loft conversion was going to be undertaken, rigorous accuracy required when modelling in 3D."]},
    {"slug": "victorian-terrace-renovation-islington-london", "title": "Victorian Terrace Renovation – Islington, London", "cat": "Scan-to-BIM", "loc": "Islington, London", "year": "2024", "service": "Scan to BIM",
     "overview": ["We provided a full 3D Revit model with 1:50 plans, elevations and sections for a Victorian terraced house undergoing a loft conversion, basement and rear extension. The model captured every uneven wall and floor, giving the architect a precise base for design."],
     "challenges": ["Irregular brickwork and historic alterations required millimetre accuracy.",
                    "Tight access in narrow staircases meant careful scanner positioning.",
                    "We gave blanket notes over discrepancies on drawings and assisted on site too."]},
    {"slug": "3d-walkthrough-for-flat-sale-manchester-city-centre", "title": "Setting out, 3 Storey Commercial Unit – Bedfont Lakes, London", "cat": "As-Built Verification", "loc": "Bedfont Lakes, London", "year": "2026", "service": "Setting out / As-built deviation",
     "overview": ["For a commercial contractor, they required the Architect’s gridlines to be staked out on site and physically sprayed on the floor. These were required to set out proposed MEP duct / pipework in the slab soffit."],
     "challenges": ["Discrepancies between the Architect’s plans and as-built reality.",
                    "Column chamfers were not accounted for, columns slightly out of square."]},
    {"slug": "as-built-deviation-flat-london", "title": "As Built Plans – Apartment, London", "cat": "As-Built Verification, Scan-to-BIM", "loc": "Islington, London", "year": "2025", "service": "As-built plans for verification",
     "overview": ["We scanned six newly built apartments to ensure dimensions matched the design drawings before handover to the Client."],
     "challenges": ["Found discrepancies in window placement and wall thickness, flagged before client snagging.",
                    "Delivered overlay comparison reports for the contractor’s QA process."]},
    {"slug": "house-planning", "title": "Movement Monitoring – Grade II Building, Cambridge", "cat": "Building Movement Monitoring", "loc": "Cambridge", "year": "2025", "service": "Building Movement Monitoring",
     "overview": ["We monitored an Edwardian property for settlement as tunnelling works for an underground railway to an existing line were carried out nearby."],
     "challenges": ["Repeat scans had to align precisely across quarterly monitoring cycles.",
                    "Detected 4mm settlement in one flank wall, allowing engineers to act early."]},
    {"slug": "heritage-scan-grade-ii-building-bath", "title": "Heritage Scan – Grade II Building, Bath", "cat": "Heritage & Restoration Surveys", "loc": "Bath", "year": "2023", "service": "Heritage & Restoration Surveys",
     "overview": ["Our team scanned a Grade II listed building to support conservation architects planning sensitive repairs."],
     "challenges": ["Ornate stone carvings and stained-glass windows required high-resolution scanning.",
                    "No scaffolding allowed; we captured elevated features with tripod extensions and angled scans."]},
    {"slug": "measured-survey-commercial-headquarters-london", "title": "Measured Survey – Commercial Headquarters, London", "cat": "As-Built Verification, Scan-to-BIM", "loc": "Bedfont Lakes, London", "year": "2025", "service": "As-built scan + BIM Revit model",
     "overview": ["Client at Bedfont Lakes, London, was undergoing a refurbishment on their commercial unit. They required a full scan in order to reroute proposed MEP pipework through castellated beams."],
     "extra": ["Scanner used: Leica RTC360", "Measurements were taken with ±2mm accuracy."],
     "challenges": ["Existing beams were pre-cambered. When we supplied the Revit model, we needed to size the beams carefully in order to understand the available penetration dimension for new pipework.",
                    "Trades had to be put on pause on the floor we were working on to gain an accurate model."]},
    {"slug": "cottage-extension-cotswolds", "title": "Cottage Extension – London", "cat": "As-Built Verification, Scan-to-BIM", "loc": "London", "year": "2023", "service": "Scan-to-BIM + As-Built Verification",
     "overview": ["Scanned a brick cottage before and after an extension to verify construction against drawings."],
     "challenges": ["Uneven internal/external walls required bespoke modelling. Provided a dimensional error tolerance on drawings.",
                    "There wasn’t sufficient opening up works – unknown areas highlighted in drawings."]},
    {"slug": "rear-side-loft-extension-potters-bar-london", "title": "Rear/Side/Loft Extension – Potters Bar, London", "cat": "Scan-to-BIM", "loc": "Potters Bar, London", "year": "2025", "service": "Scan-to-BIM + As-Built Verification",
     "overview": ["We delivered a full Scan-to-BIM model for a semi-detached property undergoing a combined rear, side, and loft extension. The model provided the architect with precise existing conditions, ensuring seamless integration of the new spaces with the original structure. Post-construction, we carried out an as-built verification scan to confirm dimensions matched the approved design."],
     "challenges": ["Multiple extensions happening simultaneously required phased scanning and model updates.",
                    "Roof geometry for the loft conversion included complex dormers that needed careful capture and modelling."]},
    {"slug": "rear-extension-watford-london", "title": "Rear Extension – Watford, London", "cat": "Scan-to-BIM", "loc": "Watford, London", "year": "2025", "service": "Scan-to-BIM",
     "overview": ["Our team provided a detailed Scan-to-BIM survey of a detached property in Watford, commissioned ahead of a rear extension. The point cloud data was converted into a Revit model, enabling the architect to design directly from an accurate as-built base."],
     "challenges": ["Narrow garden access meant equipment had to be set up compactly while still capturing the full rear elevation.",
                    "Existing settlement cracks in the property required high-resolution data to document pre-extension conditions for the homeowner."]},
]
PROJECT_BY_SLUG = {p["slug"]: p for p in PROJECTS}
# The six projects the live site's menu lists, in its order (two of its links were dead; they now open the real pages)
MENU_PROJECTS = ["victorian-terrace-renovation-islington-london", "heritage-scan-grade-ii-building-bath", "measured-survey-commercial-headquarters-london",
                 "cottage-extension-cotswolds", "rear-side-loft-extension-potters-bar-london", "rear-extension-watford-london"]

TEAM = [
    {"key": "team-endrit", "slug": "endrit-badallaj", "name": "Endrit Badallaj", "role": "BEng, Director", "phone": "07460 844015", "tel": "+447460844015", "email": "endrit@axis3dsurveys.com",
     "bio": "With over a decade of experience in structural design and digital construction, Endrit brings both technical precision and creative problem solving to every project. Having delivered designs for residential, commercial, industrial and heritage structures, he combines practical engineering knowledge with advanced BIM expertise to ensure accuracy and coordination across all stages of construction."},
    {"key": "team-florjan", "slug": "florjan-mata", "name": "Florjan Mata", "role": "BEng, Senior Surveyor", "phone": "07460 844015", "tel": "+447460844015", "email": "info@axis3dsurveys.com",
     "bio": "Florjan has more than 12 years of expertise in land and building measurement, specialising in GNSS positioning, total station surveying, and 3D laser scanning. Known for their meticulous approach and reliability, they provide precise data capture that forms the backbone of accurate design and construction."},
    {"key": "team-daniel", "slug": None, "name": "Daniel Tosuni", "role": None, "bio": None},  # page not in the export (its live address is /team/erald-krasniqi/)
]

TESTIMONIALS = [
    ("I needed an accurate survey for a house extension, and Axis3D exceeded expectations. They explained everything clearly, delivered quickly, and gave my architect exactly what they needed. Brilliant service.", "Michael T.", "Homeowner, Surrey"),
    ("The level of accuracy in Axis3D’s point cloud and BIM deliverables was excellent. It made clash detection and coordination with other trades so much smoother. They’re now our go-to survey partner.", "Priya S.", "MEP Consultant, Leeds"),
    ("Axis3D Surveys helped us eliminate rework by providing an exact as-built model before we even broke ground. Their fast turnaround and professionalism kept our project on schedule and within budget.", "James K.", "Main Contractor, Birmingham"),
    ("We rely on precision data, and Axis3D delivered exactly that. The laser scans and structural models were spot-on, which made coordination with architects and contractors seamless. Highly recommended for any engineering project.", "David R.", "Structural Engineer, Manchester"),
    ("Axis3D’s Scan-to-BIM service was a game changer for our design team. The accuracy of the models gave us complete confidence, especially on a complex heritage refurbishment. Their attention to detail saved us countless hours on site.", "Sarah L.", "Architect, London"),
]

INFOBOXES = [
    ("target", "Accuracy That Matters", "Every project begins with data you can trust. Our 3D laser scanning and measured surveys deliver millimetre-level accuracy, reducing costly errors and rework."),
    ("scan", "Scan-to-BIM Expertise", "We transform point clouds into intelligent BIM models (Revit/AutoCAD/VW), giving architects, engineers, and contractors the clarity to design, coordinate, and build with confidence."),
    ("plan", "Tailored Project Planning", "From construction sites to heritage buildings, we provide surveys and models designed to meet the exact needs of your project, on time and on budget."),
    ("sectors", "Trusted Across Sectors", "With experience in industrial, commercial, residential, and heritage projects, we adapt our expertise to fit your sector while maintaining the highest standards."),
]

PROGRESS = [("BIM", 80), ("Contractors", 90), ("Real Estate & Developers", 85)]
COUNTERS = [(20, "Happy Clients"), (88, "Projects"), (98, "Work Employed"), (467, "Planning Services")]

HOME_FAQ = [
    ("How accurate are your 3D laser scans and BIM models?", ["Our scans capture data with 1–2mm precision, and our BIM models are built to LOD (Level of Detail) standards that suit your project needs. This ensures architects and engineers can design with confidence, knowing every measurement reflects real-world conditions."]),
    ("How can Scan-to-BIM help contractors during construction?", ["By starting with an accurate digital model, contractors can spot potential clashes, plan logistics more efficiently, and avoid costly rework. Our deliverables help keep projects on schedule and within budget."]),
    ("Do homeowners really need a 3D survey for extensions or renovations?", ["Absolutely. A 3D survey ensures your architect works from precise measurements of your home. This reduces the risk of design errors, speeds up planning approval, and gives peace of mind that your extension will fit seamlessly with the existing structure."]),
    ("How quickly can you deliver survey results and BIM models?", ["Point cloud models are always delivered same day on any project size up to 2000 m².",
                                                                   "Turnaround depends on the deliverable required. As an example, for a residential house smaller than 100 m², we can provide same-day plans, sections and a 3D Revit model.",
                                                                   "Larger commercial or industrial projects (over 5000 m²) may take a few weeks. We always agree on timelines upfront and deliver on schedule."]),
]

CUR = ' aria-current="page"'
NAV = [("/", "Home"), ("/our-services/", "Our Services"), ("/our-projects/", "Our Projects"), ("/about-us/", "About Us"), ("/contact-us/", "Contact Us")]

# ---------------------------------------------------------------- chrome
DEMO_BAR = """<style id="pitch-bar-css">
  #pitch-bar{position:fixed;top:0;left:0;right:0;z-index:2147483000;
    box-sizing:border-box;display:flex;align-items:center;gap:6px;height:48px;
    padding:0 12px;background:#0c0c0c;color:#eee;
    font:600 13px/1 system-ui,-apple-system,"Segoe UI",sans-serif;
    border-bottom:2px solid var(--pitch-accent,#e8b33a)}
  #pitch-bar *{box-sizing:border-box;margin:0}
  #pitch-bar .pitch-chip{background:var(--pitch-accent,#e8b33a);color:#0c0c0c;
    font-size:10px;font-weight:800;letter-spacing:.12em;text-transform:uppercase;
    padding:4px 7px;border-radius:3px;margin-right:6px;flex:none}
  #pitch-bar a{color:#bdbdbd;text-decoration:none;padding:16px 10px 14px;
    white-space:nowrap;border-bottom:3px solid transparent}
  #pitch-bar a:hover{color:#fff}
  #pitch-bar a[aria-current="page"]{color:#fff;
    border-bottom-color:var(--pitch-accent,#e8b33a)}
  body{padding-top:48px !important}
  :root{--demo-offset:48px}
  @media (max-width:479px){
    #pitch-bar{padding:0 6px;gap:2px}
    #pitch-bar a{padding:16px 7px 14px;font-size:12px}
    #pitch-bar .pitch-chip{margin-right:2px}
  }
</style>
<nav id="pitch-bar" aria-label="Demo pages">
  <span class="pitch-chip">Demo</span>
  <a href="/"__SITE__>Improved site</a>
  <a href="/improvements/"__IMPROVEMENTS__>What’s improved</a>
</nav>"""


def demo_bar(tab):
    cur = ' aria-current="page"'
    return (DEMO_BAR.replace("__SITE__", cur if tab == "site" else "")
            .replace("__IMPROVEMENTS__", cur if tab == "improvements" else ""))


def asset(path):
    data = (PUBLIC / path.lstrip("/")).read_bytes()
    return f"{path}?v={hashlib.sha1(data).hexdigest()[:8]}"


def logo(light=False, lazy=True):
    m = MANIFEST["logo-light" if light else "logo"]
    extra = ' loading="lazy"' if lazy else ""
    return f'<img src="/assets/img/{m["file"]}" width="{m["width"]}" height="{m["height"]}" alt="Axis 3D Surveys"{extra}>'


def header(current):
    def sub_services(cls):
        return f'<ul{" class=" + chr(34) + cls + chr(34) if cls else ""}>' + "".join(
            f'<li><a href="/service/{s["slug"]}/"{CUR if current == "/service/" + s["slug"] + "/" else ""}>{esc(s["title"])}</a></li>' for s in SERVICES) + "</ul>"

    def sub_projects(cls):
        return f'<ul{" class=" + chr(34) + cls + chr(34) if cls else ""}>' + "".join(
            f'<li><a href="/project/{slug}/"{CUR if current == "/project/" + slug + "/" else ""}>{esc(PROJECT_BY_SLUG[slug]["title"])}</a></li>' for slug in MENU_PROJECTS) + "</ul>"

    items, mobile_items = [], []
    for href, label in NAV:
        is_cur = href == current
        section = href != "/" and current.startswith(href)
        if href == "/our-services/":
            section = section or current.startswith("/service/")
            sub, msub = sub_services("sub"), sub_services("")
        elif href == "/our-projects/":
            section = section or current.startswith("/project/")
            sub, msub = sub_projects("sub"), sub_projects("")
        elif href == "/about-us/":
            section = section or current.startswith("/team/")
            sub = msub = ""
        else:
            sub = msub = ""
        cls = " ".join(c for c in ("current" if is_cur or section else "", "has-sub" if sub else "") if c)
        aria = ' aria-current="page"' if is_cur else ""
        items.append(f'<li{" class=" + chr(34) + cls + chr(34) if cls else ""}><a href="{href}"{aria}>{label}</a>{sub}</li>')
        mobile_items.append(f'<li><a href="{href}"{aria}>{label}</a>{msub}</li>')
    return f"""<a class="skip-link" href="#main">Skip to content</a>
<header class="site-header">
  <div class="header-top"><div class="container"><div class="inner">
    <a class="brand" href="/" aria-label="Axis 3D Surveys – home">{logo(lazy=False)}</a>
    <div class="header-cta"><a class="btn" href="/contact-us/">Request a Quote</a></div>
    <div class="contact-info">
      <div class="contact-item"><span class="ico">{icon("phone")}</span><div><span class="label-sm">Call Now</span><span class="value"><a href="tel:{SITE["tel"]}">{SITE["phone"]}</a></span></div></div>
      <div class="contact-item"><span class="ico">{icon("mail")}</span><div><span class="label-sm">Email</span><span class="value"><a href="mailto:{SITE["email"]}">{SITE["email"]}</a></span></div></div>
      <div class="contact-item"><span class="ico">{icon("pin")}</span><div><span class="label-sm">Address</span><span class="value">London, UK</span></div></div>
    </div>
    <div class="header-tools">
      <a class="icon-btn call" href="tel:{SITE["tel"]}" aria-label="Call {SITE["phone"]}">{icon("phone")}</a>
      <button class="icon-btn nav-toggle" type="button" aria-expanded="false" aria-controls="mobile-nav" aria-label="Menu"><span class="menu-ico">{icon("menu")}</span><span class="close-ico">{icon("x")}</span></button>
    </div>
  </div></div></div>
  <div class="nav-bar"><div class="container"><nav class="main-nav" aria-label="Main">
    <ul>{"".join(items)}</ul>
    <div class="nav-cta"><a class="phone" href="tel:{SITE["tel"]}">{icon("phone")} {SITE["phone"]}</a><a class="btn btn--sm" href="/contact-us/">Request a Quote</a></div>
  </nav></div></div>
  <nav class="mobile-nav" id="mobile-nav" hidden aria-label="Mobile"><div class="container">
    <ul>{"".join(mobile_items)}</ul>
    <div class="actions"><a class="btn" href="/contact-us/">Request a Quote</a><a class="btn btn--navy" href="tel:{SITE["tel"]}">Call {SITE["phone"]}</a></div>
  </div></nav>
</header>"""


def footer():
    services = "".join(f'<li><a href="/service/{s["slug"]}/">{esc(s["title"])}</a></li>' for s in SERVICES)
    return f"""<footer class="site-footer">
  <div class="footer-top"><div class="container"><div class="footer-grid">
    <div class="footer-brand">
      {logo(light=True)}
      <p>Axis 3D Surveys delivers precise 3D laser scanning, BIM modelling, and as-built verification services across the UK. We help architects, engineers, and contractors design with confidence and accuracy.</p>
      <a class="phone" href="tel:{SITE["tel"]}">{SITE["phone"]}</a><br>
      <a class="btn btn--outline" href="/contact-us/">Request with online form</a>
    </div>
    <div><h3 class="widget-title">Services</h3><ul class="footer-links">{services}</ul></div>
    <div><h3 class="widget-title">Company</h3><ul class="footer-links"><li><a href="/about-us/">About Us</a></li><li><a href="/our-projects/">Our Projects</a></li><li><a href="/our-services/">Our Services</a></li><li><a href="/contact-us/">Contact Us</a></li></ul></div>
    <div><h3 class="widget-title">Get In Touch</h3><ul class="footer-contact">
      <li>{icon("pin")}<address>{SITE["address"][0]},<br>{SITE["address"][1]}</address></li>
      <li>{icon("mail")}Email: <a href="mailto:{SITE["email"]}">{SITE["email"]}</a></li>
      <li>{icon("phone")}Phone: <a href="tel:{SITE["tel"]}">{SITE["phone"]}</a></li>
    </ul></div>
  </div></div></div>
  <div class="copyright"><div class="container"><div class="row">
    <div>© {YEAR} {SITE["legal"]}. All rights reserved.</div>
    <div>Design and development by <a href="http://www.instagram.com/eneslikaj" rel="nofollow noopener" target="_blank">Enes</a></div>
  </div></div></div>
</footer>"""


def jsonld():
    return json.dumps({
        "@context": "https://schema.org", "@type": "ProfessionalService", "name": SITE["legal"],
        "url": SITE["live"], "telephone": SITE["tel"], "email": SITE["email"],
        "address": {"@type": "PostalAddress", "streetAddress": SITE["address"][0], "addressLocality": "London", "postalCode": "N1 3ND", "addressCountry": "GB"},
        "areaServed": "United Kingdom", "description": SITE["tagline"],
    }, ensure_ascii=False)


def layout(title, desc, body, current="", tab="site", schema=True):
    full_title = title if title.endswith("Axis 3D Surveys") else f"{title} – Axis 3D Surveys"
    og_image = f'<meta property="og:image" content="{BASE_URL}/assets/img/{MANIFEST["hero"]["file"]}">' if BASE_URL else ""
    canonical = f'<link rel="canonical" href="{BASE_URL}{current}">' if BASE_URL and current else ""
    ld = f'<script type="application/ld+json">{jsonld()}</script>' if schema else ""
    return f"""<!doctype html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>{esc(full_title)}</title>
<meta name="description" content="{esc(desc)}">
<meta property="og:site_name" content="Axis 3D Surveys">
<meta property="og:title" content="{esc(full_title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:type" content="website">
{og_image}{canonical}
<meta name="theme-color" content="#09162a">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="preload" href="/fonts/rajdhani-latin-700-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/fonts/mulish-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{asset('/fonts/fonts.css')}">
<link rel="stylesheet" href="{asset('/assets/css/site.css')}">
{ld}
</head>
<body>
{demo_bar(tab)}
{header(current)}
<main id="main">
{body}
</main>
{footer()}
<script src="{asset('/assets/js/site.js')}" defer></script>
</body>
</html>
"""


def page_title(h1, crumbs):
    items = '<li><a href="/">Home</a></li>' + "".join(
        (f'<li><a href="{href}">{esc(label)}</a></li>' if href else f'<li aria-current="page">{esc(label)}</li>') for label, href in crumbs)
    return f"""<section class="page-title">
  {img("band-bg", "", srcset=["band-bg-sm", "band-bg"], sizes="100vw", lazy=False)}
  <div class="container"><h1>{h1}</h1><nav aria-label="Breadcrumb"><ol class="breadcrumb">{items}</ol></nav></div>
</section>"""


# ---------------------------------------------------------------- components
def service_card(s):
    return f"""<article class="service-card">
  <div class="media"><a href="/service/{s["slug"]}/" tabindex="-1" aria-hidden="true">{img(s["thumb"], s["title"] + " – service illustration")}</a></div>
  <div class="body">
    <span class="icon">{icon(s["icon"])}</span>
    <h3><a href="/service/{s["slug"]}/">{esc(s["title"])}</a></h3>
    <p>{esc(s["short"])}</p>
    <a class="text-link" href="/service/{s["slug"]}/" aria-label="Read more about {esc(s["title"])}">Read More</a>
  </div>
</article>"""


def project_card(p):
    return f'<a class="project-card" href="/project/{p["slug"]}/">{img("proj-" + p["slug"], p["title"])}<div class="cap"><h3>{esc(p["title"])}</h3><span class="cat">{esc(p["cat"])}</span></div></a>'


def faq(items, open_first=True):
    out = []
    for i, (q, a) in enumerate(items):
        o = " open" if open_first and i == 0 else ""
        paras = a if isinstance(a, list) else [a]
        out.append(f'<details{o}><summary>{esc(q)}</summary><div class="answer">' + "".join(f"<p>{esc(x)}</p>" for x in paras) + "</div></details>")
    return '<div class="faq">' + "".join(out) + "</div>"


def carousel_nav(label):
    return f'<div class="nav"><button type="button" data-dir="prev" aria-label="Previous {label}">{icon("left")}</button><button type="button" data-dir="next" aria-label="Next {label}">{icon("right")}</button></div>'


def testimonials_block():
    cards = []
    for quote, name, role in TESTIMONIALS:
        initials = "".join(w[0] for w in name.replace(".", "").split()[:2]).upper()
        cards.append(f"""<div class="item"><article class="t-card">
  <blockquote>“{esc(quote)}”</blockquote>
  <div class="who"><span class="avatar" aria-hidden="true">{initials}</span><div><div class="name">{esc(name)}</div><div class="role">{esc(role)}</div></div></div>
</article></div>""")
    return f"""<section class="section testimonials" aria-labelledby="testimonials-title">
  {img("testimonials-bg", "")}
  <div class="container">
    <div class="section-head center light"><span class="label">Testimonials</span><h2 id="testimonials-title">What our clients say</h2></div>
    <div class="carousel" data-carousel><div class="track">{"".join(cards)}</div>{carousel_nav("testimonials")}</div>
  </div>
</section>"""


def contact_faq_block():
    return f"""<section class="section section--grey contact-faq" aria-labelledby="questions-title">
  <div class="container"><div class="grid">
    <div>
      <div class="section-head"><span class="label">Contact us</span><h2 id="questions-title">So, any questions?</h2></div>
      <div class="contact-box">
        {img("contact-bg", "", cls="bg")}
        <div class="tab" aria-hidden="true"><span>Contact us</span></div>
        <div class="row"><span class="circle">{icon("phone")}</span><div><span class="small">For any enquiries call now</span><a class="big" href="tel:{SITE["tel"]}">{SITE["phone"]}</a></div></div>
        <div class="row"><span class="circle">{icon("mail")}</span><div><span class="small">Or email us</span><a class="big email" href="mailto:{SITE["email"]}">{SITE["email"]}</a></div></div>
      </div>
    </div>
    <div>{faq(HOME_FAQ)}</div>
  </div></div>
</section>"""


def counters_block():
    counters = "".join(f'<div class="counter"><div class="n" data-count="{n}">{n}</div><div class="t">{esc(t)}</div></div>' for n, t in COUNTERS)
    return f'<section class="counters" aria-label="Key numbers"><div class="container"><div class="grid">{counters}</div></div></section>'


# ---------------------------------------------------------------- pages
def home():
    progress = "".join(f'<div class="progress"><div class="row"><span>{esc(t)}</span><span>{v}%</span></div><div class="bar"><span style="--v:{v}%"></span></div></div>' for t, v in PROGRESS)
    infoboxes = "".join(f'<div class="infobox"><span class="icon">{icon(i)}</span><h3>{esc(t)}</h3><p>{esc(d)}</p></div>' for i, t, d in INFOBOXES)
    body = f"""<section class="hero" aria-labelledby="hero-title">
  <div class="container"><div class="grid">
    <div>
      <h1 id="hero-title"><span class="hl">Need</span><br>Accurate <span class="red">Surveys?</span></h1>
      <p class="lead"><strong>Reliable 3D scans and as-built models delivered when you need them.</strong> Clear communication. Reliable turnaround. Data designers and contractors can use immediately.</p>
      <div class="actions"><a class="btn btn--red" href="/contact-us/">Need a reliable survey? Let’s talk.</a><a class="call" href="tel:{SITE["tel"]}">{icon("phone")} {SITE["phone"]}</a></div>
    </div>
    <div class="visual">{img("hero", "An Axis 3D Surveys surveyor with a Leica laser scanner on a construction site, checking the scan on a tablet", srcset=["hero-sm", "hero"], sizes="(max-width: 991px) 100vw, 640px", lazy=False)}</div>
  </div></div>
</section>

<section class="services-home" aria-labelledby="services-title">
  <div class="container"><div class="band">
    <div class="section-head center light"><span class="label">Our Services</span><h2 id="services-title">3D Scanning and BIM Services</h2></div>
    <div class="grid-3">{"".join(service_card(s) for s in SERVICES)}</div>
  </div>
  <div class="plus-row"><a class="plus-link" href="/our-services/"><span class="sq" aria-hidden="true">+</span>Explore more services</a></div>
  </div>
</section>

<section class="section about-home" aria-labelledby="about-title">
  <div class="container"><div class="grid">
    <div>
      <span class="label">About Us</span>
      <h2 id="about-title">Our mission is simple: to give Architects, Engineers, and Contractors the data they need to design and build with confidence.</h2>
      <p>From small refurbishments to large-scale infrastructure, we provide clear, reliable information that reduces risk, saves time, and supports smarter decisions. With over <strong>88 projects delivered</strong>, we’ve built a reputation for turning complex environments into simple, accurate, and actionable digital models.</p>
      <div style="margin:36px 0 40px">{progress}</div>
      <a class="btn btn--navy" href="/about-us/">Read More</a>
    </div>
    <div class="visual">
      {img("about-home", "A surveyor in a hi-vis jacket and Axis 3D Surveys hard hat sighting through a total station on a tripod")}
      <div class="counter-box"><i></i><i></i><i></i><i></i><div class="n" data-count="88">88</div><div class="t">Projects Completed</div></div>
    </div>
  </div></div>
</section>

<section class="why" aria-labelledby="why-title">
  <div class="container"><div class="grid">
    <div class="photo">{img("why-photo", "A laser scanner on a tripod inside a commercial building under construction, with the scan positions plotted on a tablet in the foreground")}</div>
    <div class="panel">
      <span class="label">Why Choose us</span>
      <h2 id="why-title">We are professional surveyors</h2>
      <p>We combine advanced scanner instruments and software with trusted expertise to deliver precise, reliable, and future-ready survey solutions. Here’s why clients choose us:</p>
      <div class="infobox-grid">{infoboxes}</div>
    </div>
  </div></div>
</section>

{counters_block()}
{testimonials_block()}
{contact_faq_block()}"""
    return layout("Axis 3D Surveys – 3D Laser Scanning, Scan-to-BIM and Measured Surveys, London",
                  "Reliable 3D scans and as-built models delivered when you need them. Scan-to-BIM, 4D BIM planning, as-built verification, building movement monitoring, heritage surveys and digital twins across the UK.",
                  body, "/")


def about():
    cards = []
    for t in TEAM:
        name = f'<a href="/team/{t["slug"]}/">{esc(t["name"])}</a>' if t["slug"] else esc(t["name"])
        role = f'<div class="role">{esc(t["role"])}</div>' if t["role"] else ""
        cards.append(f'<article class="team-card">{img(t["key"], "Portrait of " + t["name"])}<div class="body"><h3>{name}</h3>{role}</div></article>')
    body = page_title("About Us", [("About Us", None)]) + f"""
<section class="section about-page" aria-labelledby="about-title">
  <div class="container"><div class="grid">
    <div>
      <span class="label">About us</span>
      <h2 id="about-title">Our mission is simple: to give Architects, Engineers, and Contractors the data they need to design and build with confidence.</h2>
      <div class="intro-box"><div class="tag" aria-hidden="true"><span>88+ projects delivered</span></div>
        <p><strong>Axis 3D Surveys delivers precise 3D laser scanning, BIM modelling, and as-built verification services across the UK.</strong> We help architects, engineers, and contractors design with confidence and accuracy.</p>
        <p>From small refurbishments to large-scale infrastructure, we provide clear, reliable information that reduces risk, saves time, and supports smarter decisions. With over 88 projects delivered, we’ve built a reputation for turning complex environments into simple, accurate, and actionable digital models.</p>
        <p>We combine advanced scanner instruments and software with trusted expertise to deliver precise, reliable, and future-ready survey solutions.</p>
      </div>
      <p class="visually-hidden">More than eighty-eight projects delivered.</p>
      <a class="btn btn--navy" href="/our-projects/">Our Projects</a>
    </div>
    <div class="visual">{img("about-home", "A surveyor in a hi-vis jacket and Axis 3D Surveys hard hat sighting through a total station on a tripod")}</div>
  </div></div>
</section>
{counters_block()}
<section class="section section--grey" aria-labelledby="team-title">
  <div class="container">
    <div class="section-head center"><span class="label">The professionals</span><h2 id="team-title">Our Team</h2></div>
    <div class="grid-3">{"".join(cards)}</div>
  </div>
</section>"""
    return layout("About Us", "Axis 3D Surveys delivers precise 3D laser scanning, BIM modelling and as-built verification across the UK. Meet the team behind more than 88 projects.", body, "/about-us/")


def team_page(t):
    with_pages = [x for x in TEAM if x["slug"]]
    i = with_pages.index(t)
    prev_t, next_t = with_pages[i - 1], with_pages[(i + 1) % len(with_pages)]
    body = page_title(esc(t["name"]), [("About Us", "/about-us/"), (t["name"], None)]) + f"""
<section class="section" aria-labelledby="member-title">
  <div class="container"><div class="member">
    <div class="photo">{img(t["key"], "Portrait of " + t["name"], lazy=False)}</div>
    <div>
      <h2 id="member-title" style="margin-bottom:6px">{esc(t["name"])}</h2>
      <div class="role">{esc(t["role"])}</div>
      <p>{esc(t["bio"])}</p>
      <dl><dt>Phone</dt><dd><a href="tel:{t["tel"]}">{t["phone"]}</a></dd><dt>Email</dt><dd><a href="mailto:{t["email"]}">{t["email"]}</a></dd></dl>
      <nav class="post-nav" aria-label="Other team members">
        <a href="/team/{prev_t["slug"]}/">{icon("left")} {esc(prev_t["name"])}</a>
        <a class="next" href="/team/{next_t["slug"]}/">{esc(next_t["name"])} {icon("right")}</a>
      </nav>
    </div>
  </div></div>
</section>"""
    return layout(t["name"], f'{t["name"]}, {t["role"]} at Axis 3D Surveys. {t["bio"][:120].rsplit(" ", 1)[0]}…', body, f"/team/{t['slug']}/")


def services_page():
    body = page_title("Our Services", [("Our Services", None)]) + f"""
<section class="section" aria-labelledby="services-title">
  <div class="container">
    <div class="section-head center"><span class="label">Our Services</span><h2 id="services-title">3D Scanning and BIM Services</h2><p>We combine advanced scanner instruments and software with trusted expertise to deliver precise, reliable, and future-ready survey solutions.</p></div>
    <div class="grid-3" style="padding-top:20px">{"".join(service_card(s) for s in SERVICES)}</div>
  </div>
</section>
{contact_faq_block()}"""
    return layout("Our Services", "Scan-to-BIM, 4D BIM Planning, As-Built Verification, Building Movement Monitoring, Heritage & Restoration Surveys and Digital Twin Creation from Axis 3D Surveys, London.", body, "/our-services/")


def projects_page():
    body = page_title("Our Projects", [("Our Projects", None)]) + f"""
<section class="section" aria-labelledby="projects-title">
  <div class="container">
    <div class="section-head center"><span class="label">Recent work</span><h2 id="projects-title">Projects across London and the UK</h2><p>Scan-to-BIM, as-built verification, 4D planning, movement monitoring and heritage scans for homeowners, architects, contractors and developers.</p></div>
    <div class="grid-3">{"".join(project_card(p) for p in PROJECTS)}</div>
  </div>
</section>"""
    return layout("Our Projects", "Fourteen recent Axis 3D Surveys projects: Scan-to-BIM, point clouds, as-built verification, 4D planning, movement monitoring and heritage scans across London and the UK.", body, "/our-projects/")


def service_page(s):
    i = SERVICES.index(s)
    prev_s, next_s = SERVICES[i - 1], SERVICES[(i + 1) % len(SERVICES)]
    side = "".join(f'<li><a href="/service/{x["slug"]}/"{CUR if x is s else ""}>{esc(x["title"])}</a></li>' for x in SERVICES)
    overview = "".join(f"<p>{esc(p)}</p>" for p in s["overview"])
    secondary = f'<div class="secondary">{img(s["img2"], s["title"] + " – drawing, model or site photograph")}</div>' if s["img2"] else ""
    body = page_title(esc(s["title"]), [("Our Services", "/our-services/"), (s["title"], None)]) + f"""
<section class="section" aria-labelledby="overview-title">
  <div class="container"><div class="svc-layout">
    <aside>
      <h2 class="visually-hidden">All services</h2>
      <ul class="svc-list">{side}</ul>
      <div class="help-box"><span class="icon">{icon("phone")}</span><h3>Need help right away?</h3><p>Call us now</p><a class="phone" href="tel:{SITE["tel"]}">{SITE["phone"]}</a><a class="btn" href="/contact-us/">Request a Quote</a></div>
    </aside>
    <div class="svc-main">
      {img(s["img1"], s["title"] + " – example of our work", lazy=False)}
      <h2 id="overview-title">Service Overview</h2>
      {overview}
      {secondary}
      <h2>FAQ</h2>
      {faq(s["faq"])}
      <nav class="post-nav" aria-label="Other services">
        <a href="/service/{prev_s["slug"]}/">{icon("left")} {esc(prev_s["title"])}</a>
        <a class="next" href="/service/{next_s["slug"]}/">{esc(next_s["title"])} {icon("right")}</a>
      </nav>
    </div>
  </div></div>
</section>"""
    return layout(s["title"], s["desc"], body, f"/service/{s['slug']}/")


def project_page(p):
    i = PROJECTS.index(p)
    prev_p, next_p = PROJECTS[i - 1], PROJECTS[(i + 1) % len(PROJECTS)]
    service = f'<p><strong>Service:</strong> {esc(p["service"])}</p>' if p.get("service") else ""
    overview = "".join(f"<p>{esc(t)}</p>" for t in p["overview"])
    extra = "".join(f"<p>{esc(t)}</p>" for t in p.get("extra", []))
    challenges = ('<h3>Challenges</h3><ul class="challenges">' + "".join(f"<li>{esc(c)}</li>" for c in p["challenges"]) + "</ul>") if p["challenges"] else ""
    keys = sorted(k for k in MANIFEST if re.fullmatch(rf'pp-{re.escape(p["slug"])}-\d\d', k))
    gallery_items = "".join(f'<div class="item">{img(k, "%s – drawing or photograph %d of %d" % (p["title"], n, len(keys)))}</div>' for n, k in enumerate(keys, 1))
    gallery = f"""<section class="section section--grey" aria-labelledby="gallery-title" style="padding-top:60px;padding-bottom:60px">
  <div class="container">
    <h2 id="gallery-title" style="font-size:30px">Drawings and photographs</h2>
    <div class="carousel gallery" data-carousel><div class="track">{gallery_items}</div>{carousel_nav("images")}</div>
    <nav class="post-nav" aria-label="Other projects" style="border-top:0;margin-top:20px">
      <a href="/project/{prev_p["slug"]}/">{icon("left")} {esc(prev_p["title"])}</a>
      <a class="next" href="/project/{next_p["slug"]}/">{esc(next_p["title"])} {icon("right")}</a>
    </nav>
  </div>
</section>""" if keys else ""
    body = page_title(esc(p["title"]), [("Our Projects", "/our-projects/"), (p["title"], None)]) + f"""
<section class="section" aria-labelledby="details-title">
  <div class="container">
    <div class="project-hero">
      <div class="visual">{img(f'pp-{p["slug"]}-hero', p["title"] + " – main drawing or photograph", lazy=False)}</div>
      <aside class="project-details"><h3 id="details-title">Project Details</h3><dl>
        <dt>Project Name</dt><dd>{esc(p["title"])}</dd>
        <dt>Category</dt><dd>{esc(p["cat"])}</dd>
        <dt>Location</dt><dd>{esc(p["loc"])}</dd>
        <dt>Year</dt><dd>{esc(p["year"])}</dd>
      </dl></aside>
    </div>
    <div class="summary-grid" style="margin-top:60px">
      <h2>Project Summary</h2>
      <div>{service}{overview}{extra}{challenges}</div>
    </div>
  </div>
</section>
{gallery}"""
    return layout(p["title"], f'{p["cat"]} in {p["loc"]} by Axis 3D Surveys ({p["year"]}). {p["overview"][0][:150].rsplit(" ", 1)[0]}…', body, f"/project/{p['slug']}/")


def contact():
    q = "18 Ongar House, Baxter Road, London N1 3ND"
    body = f"""<section class="page-title" style="min-height:220px">
  {img("band-bg", "", srcset=["band-bg-sm", "band-bg"], sizes="100vw", lazy=False)}
  <div class="container"><h1>Contact Us</h1><nav aria-label="Breadcrumb"><ol class="breadcrumb"><li><a href="/">Home</a></li><li aria-current="page">Contact Us</li></ol></nav></div>
</section>
<div class="map-wrap"><iframe src="https://www.google.com/maps?q={esc(q.replace(' ', '+'))}&amp;output=embed" title="Map showing 18 Ongar House, Baxter Road, London N1 3ND" loading="lazy" referrerpolicy="no-referrer-when-downgrade" allowfullscreen></iframe></div>
<section class="section" style="padding-top:0" aria-labelledby="form-title">
  <div class="container"><div class="contact-card">
    <div class="contact-strip">
      <div class="item"><span class="ico">{icon("pin")}</span><div><h3>Address</h3><p>{SITE["address"][0]},<br>{SITE["address"][1]}<br><a href="https://www.google.com/maps/search/?api=1&amp;query={esc(q.replace(' ', '+'))}" target="_blank" rel="noopener">View on Google Maps</a></p></div></div>
      <div class="item"><span class="ico">{icon("phone")}</span><div><h3>Call now</h3><p><span class="hours">For any enquiries call now</span><br><a href="tel:{SITE["tel"]}">{SITE["phone"]}</a></p></div></div>
      <div class="item"><span class="ico">{icon("mail")}</span><div><h3>Email</h3><p><a href="mailto:{SITE["email"]}">{SITE["email"]}</a></p></div></div>
    </div>
    <span class="label">Contact us</span>
    <h2 id="form-title">Tell Us About Your Project</h2>
    <form data-demo-form action="#" method="post" novalidate>
      <div class="form-grid">
        <div class="field"><label for="f-name">First name</label><input id="f-name" name="first-name" type="text" autocomplete="given-name" required></div>
        <div class="field"><label for="f-email">Email address</label><input id="f-email" name="your-email" type="email" autocomplete="email" required></div>
        <div class="field"><label for="f-industry">Select your industry</label><select id="f-industry" name="industry" required><option value="">Select your industry</option><option>Architect</option><option>Contractor</option><option>Engineer</option><option>Homeowner</option><option>Developer</option></select></div>
        <div class="field"><label for="f-phone">Phone number</label><input id="f-phone" name="phone" type="tel" autocomplete="tel"></div>
      </div>
      <div class="form-foot">
        <label class="consent"><input type="checkbox" name="privacy-consent" required> I accept the privacy and terms.</label>
        <button class="btn" type="submit">Submit Request</button>
      </div>
      <p class="form-note" hidden></p>
    </form>
  </div></div>
</section>"""
    return layout("Contact Us", "Contact Axis 3D Surveys in London: call 07460 844015, email info@axis3dsurveys.com or send your project details for a quote. 18 Ongar House, Baxter Road, London N1 3ND.", body, "/contact-us/")


def improvements(stats):
    def card(ic, title, items):
        lis = "".join(f"<li>{x}</li>" for x in items)
        return f'<article class="imp-card"><h3><span class="icon">{icon(ic)}</span>{title}</h3><ul>{lis}</ul></article>'

    def ba(before, after):
        return f'<div class="ba"><div class="before"><span class="tag">Before</span><p>{before}</p></div><div class="after"><span class="tag">After</span><p>{after}</p></div></div>'

    def check(items):
        return '<ul class="check-list">' + "".join(f"<li>{icon('check')}{x}</li>" for x in items) + "</ul>"

    filler_pages = ["Measured Survey – Commercial Headquarters", "Rear Extension – Watford", "Heritage Scan – Bath", "Cottage Extension", "Rear/Side/Loft Extension – Potters Bar", "Movement Monitoring – Cambridge"]
    body = page_title("What’s improved", [("What’s improved", None)]) + f"""
<section class="section" aria-labelledby="imp-intro">
  <div class="container">
    <div class="section-head"><span class="label">The demo, explained</span><h2 id="imp-intro">Same brand, same words — a tighter, faster, more trustworthy site</h2>
      <p>Nothing about the identity has changed: the logo, the navy and red, the Rajdhani headings and Mulish body text, the page structure, your photographs and every sentence of your copy are yours. What follows is a plain list of what was fixed, what was polished and what still needs your input, all of it checked against a browser export of your 25 pages. Use the tab at the top to go back to the site itself.</p>
    </div>

    <h3 style="font-size:28px;margin-top:10px">Three things you will notice first</h3>
    {ba("Every page’s banner and the footer background were loaded from the theme vendor’s demo server (themecrafter.com), and the header’s “Request a Quote” button and the hero button both pointed at /contact, a page that does not exist.", "Backgrounds come from your own photographs, served from your own site, and every button lands on your contact page.")}
    {ba(f"The homepage loaded {stats['before_files']} files weighing about {stats['before_mb']} MB — {stats['before_css']} stylesheets, {stats['before_js']} scripts and a 1.2 MB hero image — before anything appeared.", f"It now loads about {stats['after_files']} files weighing roughly {stats['after_kb']} KB: one hand-written stylesheet, one small script, WebP images and self-hosted fonts.")}
    {ba("Six project pages carried the theme’s demo text about “freight transportation by air” and “all major airlines” underneath your project summaries.", "The demo text is gone; only your own words remain.")}

    <div class="imp-grid" style="margin-top:40px">
      {card("tool", "Fixed what was broken", [
          "The header’s “Request a Quote” button and the hero button pointed at /contact, which does not exist; both now open your contact page. The “Read More” button under About Us went nowhere; it now opens About Us.",
          "Two entries in the Our Projects menu pointed at pages that do not exist (a “Listed Chapel, Bath” address and a “digital twin pilot… Birmingham” address). They now open the Bath heritage scan and the Commercial Headquarters survey.",
          "The footer address read “18Ongar House, Baxter Road, London, N1 3ND18”; it now reads 18 Ongar House, Baxter Road, London N1 3ND.",
          f"Leftover template text about air freight removed from six project pages ({', '.join(filler_pages)}).",
          "The page banner and the footer background were hot-linked from themecrafter.com rather than your own site; your own project photographs are used instead.",
          "The “Need Help Right away?” panel beside each service was one picture with the phone number and a “Learn More” button baked into it, so nothing in it could be tapped or read aloud. It is now a real panel with a tappable number and a quote button.",
          "Two social-media icons in the header linked to nothing; they are removed until you have profiles to link.",
          "The 4D BIM Planning card said “SYNCRHO”; it now says SYNCHRO.",
      ])}
      {card("type", "One consistent look", [
          "All text in your two typefaces, Rajdhani and Mulish, self-hosted. The hero heading and intro were set in Roboto, the page builder’s default, and the site also downloaded Roboto Slab and Roboto without using them.",
          "One blue: the hero used a second blue (#1e5aa8) beside the site’s navy (#000080). The hero now uses the site’s navy, keeping its red word and red button exactly as designed.",
          "The six service thumbnails are cut to one size; two were narrower (530 and 489 pixels) and sat at different heights.",
          "The fourteen project cards are all the same shape. The Commercial Headquarters card used a 1405×464 panorama that could not fill a portrait card, so a photo from the same project stands in; the Cambridge thumbnail was a small 489×381 image and is enlarged.",
          "Services shown as a full six-card grid instead of a carousel that revealed three at a time; the five testimonials in a two-up carousel with a heading.",
          "The footer’s two empty columns now hold your services and company links, and the footer logo is a light version that reads on the dark background.",
      ])}
      {card("zap", "Faster to load", [
          f"One stylesheet and one small script replace {stats['before_css']} stylesheets and {stats['before_js']} scripts.",
          f"Every image converted to WebP at the size it is displayed: the 1.2 MB hero is now {stats['hero_kb']} KB, and the {stats['n_images']} images across the whole site weigh {stats['images_mb']} MB together, down from {stats['before_images_mb']} MB of PNGs and JPEGs in the export.",
          "Images below the fold load only when needed, and every image declares its size so the page does not jump while loading.",
          "No analytics or page-builder scripts run before your content appears; assets carry a content hash and a one-year cache life while the HTML stays fresh.",
      ])}
      {card("smartphone", "Works properly on phones", [
          "A real menu button with a clear open and close state, plus a one-tap call button in the header.",
          "Every section stacks cleanly with no sideways scrolling from 320px up, and larger tap targets throughout.",
          "On desktop the navigation stays at the top as you scroll, with your phone number and the quote button always in reach.",
      ])}
      {card("eye", "Accessible to everyone", [
          "Descriptive alternative text on every image (the hero, the about photo and every service and project image had none), one clear H1 per page (the homepage had none; its hero was an H2 and its section titles H3s), and a sensible heading order.",
          "Menus, accordions and carousels work with a keyboard, with visible focus outlines and a skip-to-content link.",
          "Body text contrast passes WCAG AA; form fields have proper labels; animations respect the “reduce motion” setting.",
      ])}
      {card("globe", "Ready for search engines and sharing", [
          "Every page has a unique title and description — none of the 25 pages had a description before.",
          "Open Graph tags so links preview properly on WhatsApp, LinkedIn and Facebook, and structured data describing the business, address and phone number for Google.",
          "Existing page addresses are preserved, including the odd ones (see below), so current links and rankings carry over at launch. This demo itself is hidden from search engines until then.",
      ])}
      {card("edit", "Copy tidy-ups", [
          "British spelling throughout: millimetre, modelling, tunnelling, enquiries.",
          "“Commcercial” → “commercial”, “art installatios” → “art installations”, “pre cambered” → “pre-cambered”, “+/- 2mm” → “±2mm”, “m2” → “m²”, “Home Owner” → “Homeowner”, “Autocad” → “AutoCAD”, “Develop and design by” → “Design and development by”.",
          "The phone number appeared as 07460844015, +447460844015 and +44 7460 844015; it reads 07460 844015 everywhere and is tappable everywhere.",
          "Project locations in the usual order (“Slough, England” rather than “England, Slough”); the three testimonials that stopped without a full stop now have one; menu labels match the page titles.",
          "Service overviews and the long FAQ answer split into readable paragraphs; project challenges set as proper lists.",
      ])}
      {card("shield", "What was kept exactly as it was", [
          "The logo, the navy and red, the typefaces and the overall layout of every template.",
          "Every sentence of service, project, team, testimonial and FAQ copy, the counters, the progress bars and the “Request with online form” button.",
          "Your photographs and drawings, and every page address.",
          "The designer’s credit in the footer.",
      ])}
    </div>

    <div class="callout">
      <h3>Needs your input before launch</h3>
      {check([
          "About Us and Our Services were not in the export, so About Us is assembled from your homepage About section and the team pages, and Our Services from the six service cards. Send those two pages’ text if it should differ.",
          "Daniel Tosuni’s team page was not in the export either (its live address is /team/erald-krasniqi/, a leftover name), so he appears on About Us with his photo and name only. Please supply his title and a short bio.",
          "Five page addresses do not match their titles and are kept so existing links work: 4D BIM Planning at /service/real-estate-walkthroughs/, the Bedfont Lakes setting-out job at /project/3d-walkthrough-for-flat-sale-manchester-city-centre/, the Cambridge monitoring job at /project/house-planning/, the apartment as-built plans at /project/as-built-deviation-flat-london/ and the cottage at /project/cottage-extension-cotswolds/. Say the word and they get clean addresses with redirects from the old ones.",
          "The menu called the Bath project “Heritage Scan – Listed Chapel, Bath” and the cottage “Cottage Extension – Cotswolds”, while the pages say “Grade II Building, Bath” and “Cottage Extension – London”. The page titles are used; tell us which is right.",
          "Three backgrounds could not be exported (the page banners, the “why choose us” photo and the contact panel) and are stand-ins from your own project photographs; the testimonials band uses the same photo the live site does. Swap any of them in a minute.",
          "The counters (20 Happy Clients, 88 Projects, 98 Work Employed, 467 Planning Services) and the progress bars (BIM 80%, Contractors 90%, Real Estate & Developers 85%) are shown as they are. Please confirm the figures and the labels “Work Employed” and “Planning Services”.",
          "The contact form is a demo and does not send yet; at launch it is connected to your email or CRM in a few minutes. It has the same fields as yours (name, email, industry, phone, consent) and, like yours, no message box — say if you would like one.",
          "Social profiles to link, opening hours, and a company registration line for the footer if you want one.",
      ])}
      <p style="margin-top:20px">The dark bar at the very top with the two tabs is demo navigation only; it will not exist on the live site.</p>
    </div>
  </div>
</section>"""
    return layout("What’s improved", "A plain-English list of what this demo fixes and refines on the Axis 3D Surveys website while keeping the brand, the photographs and the words exactly as they are.", body, "/improvements/", tab="improvements", schema=False)


def not_found():
    body = f"""<section class="error-page"><div class="container">
  <div class="code" aria-hidden="true">404</div>
  <h1>Page not found</h1>
  <p>The page you were looking for doesn’t exist or has moved. Try the navigation above, or head back to the homepage.</p>
  <p><a class="btn" href="/">Back to the homepage</a> &nbsp; <a class="btn btn--navy" href="/contact-us/">Contact us</a></p>
</div></section>"""
    return layout("Page not found", "The page you were looking for could not be found.", body, "", schema=False)


# ---------------------------------------------------------------- build
def write(path, content):
    out = PUBLIC / path
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(content, encoding="utf-8")


def home_weight(html_text):
    """Files + bytes a first visit to the homepage fetches from this origin."""
    refs = set(re.findall(r'(?:src|href)="(/[^"?#]+)', html_text))
    refs |= set(re.findall(r'(/assets/img/[^ ,"]+)', html_text))
    files = [PUBLIC / r.lstrip("/") for r in refs if (PUBLIC / r.lstrip("/")).is_file()]
    files = [f for f in files if f.suffix != ".svg" or f.name == "favicon.svg"]
    # srcset: a desktop browser picks the larger hero/banner; drop the -sm variants from the count
    files = [f for f in files if not f.name.endswith("-sm.webp")]
    # font files are requested from fonts.css, not the HTML: the weights the homepage actually uses
    for name in ("rajdhani-latin-600-normal.woff2", "rajdhani-latin-700-normal.woff2", "mulish-latin-400-normal.woff2", "mulish-latin-700-normal.woff2"):
        f = PUBLIC / "fonts" / name
        if f not in files:
            files.append(f)
    return len(files) + 1, sum(f.stat().st_size for f in files) + len(html_text.encode())


def main():
    # Measured from the browser export of the live homepage: the files the browser saved with the page
    # (fonts, maps and remote scripts excluded) and the stylesheet/script tags in its HTML.
    before = {"files": 72, "bytes": 6215895, "css": 36, "js": 28, "images_bytes": 66221485}
    index_html = home()
    after_files, after_bytes = home_weight(index_html)
    images = [m for k, m in MANIFEST.items()]
    stats = {
        "before_files": before["files"], "before_mb": f"{before['bytes'] / 1024 / 1024:.1f}", "before_css": before["css"], "before_js": before["js"],
        "after_files": after_files, "after_kb": f"{after_bytes / 1024:.0f}",
        "hero_kb": f"{MANIFEST['hero']['bytes'] / 1024:.0f}", "n_images": len(images), "images_mb": f"{sum(m['bytes'] for m in images) / 1024 / 1024:.1f}",
        "before_images_mb": f"{before['images_bytes'] / 1024 / 1024:.0f}",
    }
    for stale in list(PUBLIC.glob("service/*")) + list(PUBLIC.glob("project/*")) + list(PUBLIC.glob("team/*")):
        if stale.is_dir():
            for f in stale.glob("*.html"):
                f.unlink()
            stale.rmdir()
    write("index.html", index_html)
    write("about-us/index.html", about())
    write("our-services/index.html", services_page())
    write("our-projects/index.html", projects_page())
    write("contact-us/index.html", contact())
    for s in SERVICES:
        write(f"service/{s['slug']}/index.html", service_page(s))
    for p in PROJECTS:
        write(f"project/{p['slug']}/index.html", project_page(p))
    for t in TEAM:
        if t["slug"]:
            write(f"team/{t['slug']}/index.html", team_page(t))
    write("improvements/index.html", improvements(stats))
    write("404.html", not_found())
    print(f"built {sum(1 for _ in PUBLIC.rglob('*.html'))} pages; homepage first visit ≈ {after_files} files, {after_bytes / 1024:.0f} KB; site images {stats['images_mb']} MB in {len(images)} files")


if __name__ == "__main__":
    main()
