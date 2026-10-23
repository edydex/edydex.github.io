from pathlib import Path
from html import escape
import json
from argparse import ArgumentParser

ROOT = Path(__file__).parent
PRODUCTS = [
    dict(slug='libre-faith', domain='libre.faith', name='Heritage Bible', short='Bible',
         description='A study Bible for web and Android. Read Scripture alongside commentary, keep notes, and follow a reading plan.',
         intro='Your Bible, with room to study.',
         action='Open the Bible', href='https://heritage.faith/',
         source='https://github.com/edydex/heritage_study_bible',
         details=[('Read and compare', 'Read translations side by side, with commentary close to the passage.'), ('Keep your place', 'Save notes and bookmarks, or work through a reading plan at your own pace.'), ('Bring your library', 'Read offline and add resources from a church’s Content Server.')],
         note='The reader works on its own. Connecting a church community is optional.',
         symbol='<path d="M32 17C24 10 13 10 6 14v35c8-4 18-3 26 3 8-6 18-7 26-3V14c-7-4-18-4-26 3Zm0 0v35"/><path d="M46 14v19l-4-3-4 3V13"/>'),
    dict(slug='libre-show', domain='libre.show', name='LibreShow', short='Presentation',
         description='Prepare a church service in your browser, then bring it to the room with SyncShow for Windows, macOS, or Linux.',
         intro='A good service starts here.',
         action='Download SyncShow', href='https://github.com/edydex/SyncShow/releases/latest',
         prepare='/prepare/',
         source='https://github.com/edydex/SyncShow',
         details=[('Start in your browser', 'Open a portable service or start from scratch. Add sections, text slides, and blanks, and arrange your service.'), ('Keep your work with you', 'Your files stay on your device. Download a service file to continue on another computer; no account or church server is needed.'), ('Present with SyncShow', 'Use the desktop app for advanced editing, songs, Scripture, media, and coordinated venue screens.')],
         note='Prepare online is a preview with a focused set of editing tools. Supported advanced content stays in your file; edit it in the desktop app. For the current public SyncShow download, save with the .syncshow-service option. The newer .libreshow extension uses the same archive and is available for newer desktop builds.',
         symbol='<rect x="6" y="10" width="39" height="29" rx="3"/><path d="M18 47h16m-8-8v8"/><rect x="35" y="29" width="23" height="25" rx="3"/><path d="m43 36 8 6-8 6Z"/>'),
    dict(slug='libre-church', domain='libre.church', name='LibreChurch Stack', short='Stack & community',
         description='Bible study, church community, and service presentation. LibreChurch Stack brings Heritage Bible, Heritage Community, and SyncShow together.',
         intro='A shared home for church life.',
         action='Explore the stack', href='https://github.com/edydex/heritage-community',
         source='https://github.com/edydex/heritage-community',
         details=[('Study with Heritage Bible', 'Read Scripture, compare translations, and keep personal notes at the Bible side of the stack.'), ('Organize your community', 'Host church resources, invite members, share events, collect RSVPs, and export calendars with Heritage Community.'), ('Present with SyncShow', 'Prepare a service and run coordinated screens, connected to your church’s own community server.')],
         note='This is the public project site. Each church runs its own community; there is no shared member sign-in here.',
         symbol='<path d="m8 29 24-17 24 17M13 27v27h38V27M32 7v12m-6-6h12"/><circle cx="24" cy="35" r="4"/><circle cx="40" cy="35" r="4"/><path d="M17 48v-3a7 7 0 0 1 14 0v3m2 0v-3a7 7 0 0 1 14 0v3"/>')
]
CSS = '''@font-face{font-family:system-local;src:local("Georgia")}*{box-sizing:border-box}html{color-scheme:light dark}body{margin:0;background:#f5f3ed;color:#242623;font:16px/1.65 system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}a{color:inherit;text-underline-offset:.22em}a:hover{text-decoration-thickness:2px}a:focus-visible{outline:2px solid #607460;outline-offset:5px}.shell{max-width:1000px;margin:auto;padding:0 36px}.skip{position:absolute;top:-60px}.skip:focus{top:12px;background:#fff;padding:8px}header{display:flex;justify-content:space-between;gap:24px;align-items:center;padding:31px 0;border-bottom:1px solid #d2d5cb}.brand{display:flex;align-items:center;gap:12px;font-weight:650;text-decoration:none;line-height:1.35}.brand img{width:37px;height:37px}nav{display:flex;gap:23px;font-size:13px}nav a{text-decoration:none;color:#5d655b}nav a[aria-current=page]{color:#263a2b;text-decoration:underline;text-underline-offset:.5em}.hero{padding:78px 0 63px;max-width:730px}.hero .stack-link{font-size:13px;margin:0 0 18px}.hero h1{font:normal clamp(38px,6vw,62px)/1.12 Georgia,serif;letter-spacing:-.045em;margin:0 0 25px}.hero p{font-size:19px;line-height:1.65;max-width:620px;margin:0;color:#596254}.actions{display:flex;gap:23px;align-items:center;flex-wrap:wrap;margin-top:31px}.primary{display:inline-block;background:#314b38;color:#fff;padding:11px 19px;border-radius:3px;text-decoration:none;font-size:14px;font-weight:600}.secondary{font-size:14px}.details{border-top:1px solid #d2d5cb;border-bottom:1px solid #d2d5cb;display:grid;grid-template-columns:repeat(3,1fr);gap:39px;padding:31px 0}.details h2{font-size:15px;font-weight:650;margin:0 0 9px}.details p{font-size:14px;color:#596254;line-height:1.7;margin:0}.note{max-width:690px;color:#596254;font-size:13px;margin:24px 0 57px}.related{padding-bottom:49px}.related h2{font-size:14px;margin:0 0 16px;font-weight:600}.related-links{display:grid;grid-template-columns:1fr 1fr;gap:18px}.related-links a{display:flex;gap:13px;align-items:center;text-decoration:none;padding:16px 0;border-top:1px solid #d2d5cb}.related-links img{width:31px;height:31px}.related-links strong{display:block;font-size:14px;font-weight:600}.related-links small{display:block;color:#596254;font-size:12px}.related-links a:hover strong{text-decoration:underline}footer{border-top:1px solid #d2d5cb;padding:24px 0 33px;display:flex;justify-content:space-between;gap:20px;font-size:12px;color:#596254}footer a{text-decoration:none}@media(prefers-color-scheme:dark){body{background:#1b1d1a;color:#ecefe5}header,.details,.related-links a,footer{border-color:#3c4439}nav a,.hero p,.details p,.note,.related-links small,footer{color:#b4bead}nav a[aria-current=page]{color:#edf0e9}.primary{background:#c2d3b9;color:#1b261b}.skip:focus{background:#1b1d1a}}@media(max-width:650px){.shell{padding:0 23px}header{display:block;padding:24px 0}.brand{font-size:15px}nav{margin-top:23px;gap:25px}.hero{padding:46px 0 40px}.hero p{font-size:17px}.hero h1{font-size:39px}.details{grid-template-columns:1fr;gap:25px;padding:28px 0}.note{margin-bottom:39px}.related-links{grid-template-columns:1fr;gap:0}footer{flex-wrap:wrap}.actions{gap:19px}}@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}}'''
HEADERS = '''/*
  Content-Security-Policy: default-src 'self'; style-src 'self'; img-src 'self'; base-uri 'none'; frame-ancestors 'none'; form-action 'none'
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
'''
parser = ArgumentParser(description='Build only the approved LibreChurch and LibreShow static sites. LibreFaith is paused.')
parser.add_argument('--site', action='append', choices=['libre-church', 'libre-show'], help='Build one approved site; may be repeated. Default: both.')
selected = set(parser.parse_args().site or ['libre-church', 'libre-show'])
for p in PRODUCTS:
    if p['slug'] not in selected:
        continue
    out = ROOT/p['slug']/'dist'
    out.mkdir(parents=True, exist_ok=True)
    svg_start='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">'
    for q in PRODUCTS:
        svg=svg_start+'<style>svg{color:#314b38}@media(prefers-color-scheme:dark){svg{color:#eef2e8}}</style>'+q['symbol']+'</svg>\n'
        (out/(q['slug']+'.svg')).write_text(svg)
    nav=''.join(f'<a href="https://{q["domain"]}/"'+(' aria-current="page"' if p==q else '')+f'>{q["short"]}</a>' for q in [PRODUCTS[2], PRODUCTS[0], PRODUCTS[1]])
    related=''.join(f'<a href="https://{q["domain"]}/"><img src="/{q["slug"]}.svg" alt="" width="31" height="31"><span><strong>{q["name"]}</strong><small>{q["domain"]}</small></span></a>' for q in PRODUCTS if q!=p)
    details=''.join(f'<section><h2>{escape(a)}</h2><p>{escape(b)}</p></section>' for a,b in p['details'])
    secondary='' if p['source']==p['href'] else f'<a class="secondary" href="{p["source"]}">Source code</a>'
    primary=f'<a class="primary" href="{p["href"]}">{p["action"]} <span aria-hidden="true">↗</span></a>'
    if p.get('prepare'):
        primary=f'<a id="prepare-online" class="primary" href="{p["prepare"]}">Prepare online <span class="preview-label">Preview</span></a>'
        secondary=f'<a id="download-syncshow" class="secondary-button" href="{p["href"]}">{p["action"]} <span aria-hidden="true">↗</span></a>'+secondary
    html=f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{p['name']} · {p['domain']}</title><meta name="description" content="{escape(p['description'],quote=True)}"><meta name="theme-color" content="#f5f3ed" media="(prefers-color-scheme:light)"><meta name="theme-color" content="#1b1d1a" media="(prefers-color-scheme:dark)"><link rel="canonical" href="https://{p['domain']}/"><link rel="icon" type="image/svg+xml" href="/{p['slug']}.svg"><link rel="stylesheet" href="/style.css"><meta property="og:title" content="{p['name']}"><meta property="og:description" content="{escape(p['description'],quote=True)}"><meta property="og:url" content="https://{p['domain']}/"><meta property="og:type" content="website"></head>
<body><a href="#main" class="skip">Skip to content</a><div class="shell"><header><a class="brand" href="/"><img src="/{p['slug']}.svg" width="37" height="37" alt="">{p['name']}</a><nav aria-label="LibreChurch Stack">{nav}</nav></header><main id="main" tabindex="-1"><section class="hero"><p class="stack-link"><a href="https://libre.church/">LibreChurch Stack</a></p><h1>{p['intro']}</h1><p>{p['description']}</p><div class="actions">{primary}{secondary}</div></section><div class="details">{details}</div><p class="note">{p['note']}</p><section class="related"><h2>Works with</h2><div class="related-links">{related}</div></section></main><footer><a href="https://mayos.dev/projects/">Built by Oles Maiovskyi</a><a href="mailto:oles@mayo.onl">oles@mayo.onl</a></footer></div></body></html>\n'''
    (out/'index.html').write_text(html)
    show_css='.secondary-button{display:inline-block;padding:10px 18px;border:1px solid #91a28b;border-radius:3px;text-decoration:none;font-size:14px;font-weight:600}.preview-label{font-size:10px;margin-left:7px;opacity:.85}.actions .secondary{font-size:12px}' if p.get('prepare') else ''
    (out/'style.css').write_text(CSS+show_css+'\n')
    (out/'_headers').write_text(HEADERS)
    (out/'robots.txt').write_text(f'User-agent: *\nAllow: /\nSitemap: https://{p["domain"]}/sitemap.xml\n')
    (out/'sitemap.xml').write_text(f'<?xml version="1.0" encoding="utf-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>https://{p["domain"]}/</loc></url></urlset>\n')
    (out/'404.html').write_text(f'<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="stylesheet" href="/style.css"><title>Page not found · {p["name"]}</title><main class="shell hero"><h1>Page not found</h1><p><a href="/">Back to {p["name"]}</a></p></main></html>\n')
    config={'name':p['slug'],'compatibility_date':'2026-10-22','assets':{'directory':'./package' if p.get('prepare') else './dist','not_found_handling':'404-page'}}
    (out.parent/'wrangler.jsonc').write_text(json.dumps(config,indent=2)+'\n')
    print(p['domain'],len(list(out.iterdir())),'static files')
