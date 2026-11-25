#!/usr/bin/env python3
"""
CarNation Elite pre-publish check. Standard library only (Python 3.8+).

  python3 scripts/prepublish-check.py blog/my-new-post.html     # one or more pages
  python3 scripts/prepublish-check.py --all                     # every blog post (baseline)
  python3 scripts/prepublish-check.py --publish-date 2026-12-01 blog/my-new-post.html

Checks each page for:
  draft placeholders left visible, banned business claims (scripts/business-facts.json),
  invalid JSON-LD, headline/H1 and FAQ text mismatches, date mismatches (visible date,
  meta tags, schema, sitemap), missing local images or image alt/width/height, broken
  internal links and #anchors, missing shared scripts (GA4 + mobile menu), canonical and
  robots problems, sitemap entry, duplicate titles/descriptions across the site,
  rel="me" llms links, and phone/address consistency.

Exit code 0 = no errors (warnings allowed), 1 = errors found.
"""
import argparse, datetime, glob, html, json, os, re, sys
from html.parser import HTMLParser
from urllib.parse import urlparse, unquote

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = 'https://carnationelite.com'
FACTS = json.load(open(os.path.join(ROOT, 'scripts', 'business-facts.json'), encoding='utf-8'))


class Page(HTMLParser):
    """Collects what the checks need in one pass."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids, self.links, self.imgs, self.scripts, self.jsonld = set(), [], [], [], []
        self.metas, self.linkrels, self.times = {}, [], []
        self.title, self.h1, self.text = '', [], []
        self._stack, self._in = [], None
        self._skip = 0          # inside <script>/<style>
        self._buf = ''
        self.faq_visible = []   # (question, answer) from .faq-item blocks
        self._faq = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if 'id' in a: self.ids.add(a['id'])
        if tag == 'a' and a.get('href') is not None: self.links.append(a['href'])
        if tag == 'link':
            self.linkrels.append(a)
            if a.get('href') and a.get('rel') not in ('preconnect', 'dns-prefetch'): self.links.append(a['href'])
        if tag == 'img': self.imgs.append(a)
        if tag == 'meta':
            k = a.get('name') or a.get('property')
            if k: self.metas[k] = a.get('content', '')
        if tag == 'time' and a.get('datetime'): self.times.append(a['datetime'])
        if tag == 'script':
            self._skip += 1
            if a.get('src'): self.scripts.append(a['src'])
            if a.get('type') == 'application/ld+json': self._in = 'jsonld'; self._buf = ''
        if tag == 'style': self._skip += 1
        if tag == 'title': self._in = 'title'; self._buf = ''
        if tag == 'h1': self._in = 'h1'; self._buf = ''
        if tag == 'div' and 'faq-item' in (a.get('class') or '').split(): self._faq = {'q': '', 'a': '', 'mode': None, 'depth': len(self._stack)}
        if self._faq is not None and tag == 'h3': self._faq['mode'] = 'q'
        if self._faq is not None and tag == 'p': self._faq['mode'] = 'a'
        if tag not in ('img', 'meta', 'link', 'br', 'hr', 'input', 'source'): self._stack.append(tag)

    def handle_endtag(self, tag):
        if tag in ('script', 'style'):
            self._skip = max(0, self._skip - 1)
            if self._in == 'jsonld': self.jsonld.append(self._buf); self._in = None
        if tag == 'title' and self._in == 'title': self.title = self._buf.strip(); self._in = None
        if tag == 'h1' and self._in == 'h1': self.h1.append(re.sub(r'\s+', ' ', self._buf).strip()); self._in = None
        if self._faq is not None and tag in ('h3', 'p'): self._faq['mode'] = None
        if self._stack and self._stack[-1] == tag: self._stack.pop()
        if self._faq is not None and tag == 'div' and len(self._stack) == self._faq['depth']:
            self.faq_visible.append((self._faq['q'].strip(), re.sub(r'\s+', ' ', self._faq['a']).strip()))
            self._faq = None

    def handle_data(self, d):
        if self._in in ('jsonld', 'title', 'h1'): self._buf += d
        if self._skip: return
        self.text.append(d)
        if self._faq is not None and self._faq['mode']: self._faq[self._faq['mode']] += d


def load(path):
    raw = open(path, encoding='utf-8').read()
    p = Page(); p.feed(raw)
    p.raw = raw
    p.visible = re.sub(r'\s+', ' ', ' '.join(p.text))
    return p


def sitemap_entries():
    try: s = open(os.path.join(ROOT, 'sitemap.xml'), encoding='utf-8').read()
    except OSError: return {}
    out = {}
    for block in re.findall(r'<url>(.*?)</url>', s, re.S):
        loc = re.search(r'<loc>(.*?)</loc>', block)
        lm = re.search(r'<lastmod>(.*?)</lastmod>', block)
        if loc: out[loc.group(1).strip()] = lm.group(1).strip() if lm else None
    return out


def resolve_local(page_path, href):
    """Return (filesystem path, fragment) for an internal link, or None for external/special."""
    if re.match(r'^(mailto|tel|sms|javascript|data):', href, re.I): return None
    u = urlparse(href)
    if u.scheme in ('http', 'https'):
        if u.netloc not in ('carnationelite.com', 'www.carnationelite.com'): return None
        path = u.path
        base = ROOT
    else:
        path = u.path
        base = ROOT if path.startswith('/') else os.path.dirname(page_path)
    if not path:
        return (page_path, u.fragment)
    fs = os.path.normpath(os.path.join(base, unquote(path.lstrip('/')) if path.startswith('/') else unquote(path)))
    if path.endswith('/') or os.path.isdir(fs): fs = os.path.join(fs, 'index.html')
    return (fs, u.fragment)


def check(path, all_pages_meta, publish_date, today):
    errs, warns = [], []
    rel = os.path.relpath(path, ROOT).replace(os.sep, '/')
    url = SITE + '/' + rel
    p = load(path)
    nocomment = re.sub(r'<!--.*?-->', '', p.raw, flags=re.S)

    # 0. Structure: landmark tags opened and closed the same number of times
    for tag in ('html', 'head', 'body', 'header', 'main', 'footer', 'nav', 'article', 'aside', 'section', 'div', 'table', 'ul', 'ol'):
        o = len(re.findall(r'<%s[\s>]' % tag, nocomment)); c = len(re.findall(r'</%s>' % tag, nocomment))
        if o != c: errs.append(f'Unbalanced <{tag}>: {o} opened, {c} closed')
    n_main = len(re.findall(r'<main[\s>]', nocomment))
    if n_main > 1: errs.append(f'{n_main} <main> elements (only one allowed)')
    elif n_main == 0: warns.append('No <main> landmark (screen readers use it to skip to the content)')

    # 1. Visible draft placeholders (HTML comments are allowed)
    vis_nocomment = Page(); vis_nocomment.feed(nocomment)
    vtxt = ' '.join(vis_nocomment.text)
    for pat in FACTS['placeholder_patterns']:
        m = re.search(pat, vtxt)
        if m: errs.append(f'Visible draft placeholder: "{m.group(0)}"')

    # 2. Banned business claims (visible text + JSON-LD)
    scan = vtxt + ' ' + ' '.join(p.jsonld)
    for b in FACTS['banned_claims']:
        m = re.search(b['pattern'], scan)
        if m: errs.append(f'Banned claim "{m.group(0)}": {b["why"]}')
    gr = FACTS.get('google_rating', {})
    for m in re.finditer(r'"ratingValue"\s*:\s*"?([\d.]+)', ' '.join(p.jsonld)):
        if gr and m.group(1) != gr['value']: errs.append(f'Schema ratingValue {m.group(1)} != approved {gr["value"]}')
    for m in re.finditer(r'"reviewCount"\s*:\s*"?(\d+)', ' '.join(p.jsonld)):
        if gr and m.group(1) != gr['count']: errs.append(f'Schema reviewCount {m.group(1)} != approved {gr["count"]}')

    # 3. JSON-LD
    graph = []
    for i, block in enumerate(p.jsonld):
        try:
            d = json.loads(block)
            graph += d.get('@graph', [d]) if isinstance(d, dict) else d
        except ValueError as e:
            errs.append(f'JSON-LD block {i+1} does not parse: {e}')
    types = {}
    for g in graph:
        t = g.get('@type'); t = t if isinstance(t, list) else [t]
        for x in t: types.setdefault(x, g)
    art = types.get('BlogPosting') or types.get('Article')
    h1 = p.h1[0] if p.h1 else ''
    if len(p.h1) != 1: errs.append(f'Expected exactly one <h1>, found {len(p.h1)}')
    if rel.startswith('blog/') and rel != 'blog/index.html':
        if not art: errs.append('No BlogPosting schema')
        else:
            for k in ('headline', 'datePublished', 'dateModified', 'author', 'image', 'publisher', 'mainEntityOfPage'):
                if not art.get(k): errs.append(f'BlogPosting missing "{k}"')
            if art.get('headline') and html.unescape(art['headline']) != h1:
                warns.append(f'BlogPosting headline differs from H1')
            img = art.get('image'); img = img.get('url') if isinstance(img, dict) else img
            if img and p.metas.get('og:image') and img != p.metas.get('og:image'):
                errs.append('Schema image and og:image differ')
            if p.metas.get('og:image') and p.metas.get('twitter:image') and p.metas['og:image'] != p.metas['twitter:image']:
                errs.append('og:image and twitter:image differ')
    faq = types.get('FAQPage')
    if faq:
        sq = [(q['name'].strip(), q['acceptedAnswer']['text'].strip()) for q in faq.get('mainEntity', [])]
        vq = [(html.unescape(q), html.unescape(a)) for q, a in p.faq_visible]
        norm = lambda s: re.sub(r'\s+', ' ', html.unescape(s)).strip()
        if vq:
            if [(norm(q), norm(a)) for q, a in sq] != [(norm(q), norm(a)) for q, a in vq]:
                errs.append(f'FAQ schema ({len(sq)}) does not match the visible FAQ ({len(vq)}) word for word')
        else:  # page uses other FAQ markup: every schema Q and A must appear in the visible text
            vt = norm(vtxt)
            missing = [q for q, a in sq if norm(q) not in vt or norm(a) not in vt]
            if missing:
                errs.append(f'{len(missing)} of {len(sq)} FAQ schema entries are not visible word for word, e.g. "{missing[0][:70]}"')
    biz = next((g for g in graph if g.get('@id') == SITE + '/#business'), None)
    if biz:
        if biz.get('telephone') != FACTS['phone_schema']: errs.append(f'Business telephone {biz.get("telephone")} != {FACTS["phone_schema"]}')
        if biz.get('address', {}).get('streetAddress') != FACTS['address']['street']: errs.append('Business street address differs from business-facts.json')

    # 4. Dates
    if art:
        dates = {'schema datePublished': art.get('datePublished'), 'article:published_time': p.metas.get('article:published_time')}
        if p.times: dates['visible <time>'] = p.times[0]
        sm = all_pages_meta['sitemap'].get(url)
        if sm: dates['sitemap lastmod'] = sm
        mod = art.get('dateModified')
        vals = {k: (v or '')[:10] for k, v in dates.items() if v}
        if len(set(vals.values())) > 1 and not (sm and set(v for k, v in vals.items() if k != 'sitemap lastmod') == {vals.get('schema datePublished')} and sm == (mod or '')[:10]):
            errs.append('Dates disagree: ' + ', '.join(f'{k}={v}' for k, v in vals.items()))
        pub = vals.get('schema datePublished')
        if publish_date and pub and pub != publish_date:
            errs.append(f'Publish date is {pub}, but you are publishing on {publish_date}')
        if pub and pub > today:
            warns.append(f'Date {pub} is in the future')
        if mod and pub and mod[:10] < pub:
            errs.append('dateModified is earlier than datePublished')

    # 5. Images
    for im in p.imgs:
        src = im.get('src', '')
        if not im.get('alt') and im.get('alt') != '': errs.append(f'Image without alt: {src}')
        if not (im.get('width') and im.get('height')): warns.append(f'Image without width/height: {src}')
        r = resolve_local(path, src)
        if r and not os.path.exists(r[0]): errs.append(f'Missing image file: {src}')
        for part in (im.get('srcset') or '').split(','):
            s = part.strip().split(' ')[0]
            r = resolve_local(path, s) if s else None
            if r and not os.path.exists(r[0]): errs.append(f'Missing srcset file: {s}')

    # 6. Internal links and anchors
    anchor_cache = {}
    for href in p.links:
        r = resolve_local(path, href)
        if not r: continue
        fs, frag = r
        if not os.path.exists(fs):
            errs.append(f'Broken internal link: {href}'); continue
        if frag and fs.endswith('.html'):
            if fs not in anchor_cache: anchor_cache[fs] = p.ids if fs == path else load(fs).ids
            if frag not in anchor_cache[fs]: errs.append(f'Missing anchor #{frag} for link {href}')

    # 7. Scripts
    for s in FACTS['required_scripts']:
        if s not in p.scripts: errs.append(f'Missing shared script {s}')
    inline_menu = "getElementById('ce-menu-toggle')" in p.raw
    if 'mobile-nav__wrapper' not in p.raw and 'mobile-nav__toggler' in p.raw and FACTS['mobile_nav_script'] not in p.scripts and not inline_menu:
        errs.append(f'Mobile menu will not open: add <script src="{FACTS["mobile_nav_script"]}" defer></script>')
    if re.search(r"gtag\('config'", nocomment): warns.append('Inline gtag config found; use /assets/js/analytics.js only')

    # 8. Canonical, robots, sitemap
    canon = [l.get('href') for l in p.linkrels if l.get('rel') == 'canonical']
    if len(canon) != 1: errs.append(f'Expected one canonical, found {len(canon)}')
    elif canon[0] != url and not (rel.endswith('index.html') and canon[0] == url[:-10]):
        errs.append(f'Canonical {canon[0]} is not this page ({url})')
    if p.metas.get('og:url') and canon and p.metas['og:url'] != canon[0]: errs.append('og:url differs from canonical')
    if 'noindex' in p.metas.get('robots', ''): errs.append('Page is noindex')
    if canon and canon[0] not in all_pages_meta['sitemap']: errs.append('Canonical URL is not in sitemap.xml')

    # 9. Titles/descriptions
    t, d = p.title, p.metas.get('description', '')
    if not t: errs.append('Missing <title>')
    elif len(t) > 60: warns.append(f'Title is {len(t)} characters (over 60 may be cut off)')
    if not d: errs.append('Missing meta description')
    elif not 120 <= len(d) <= 160: warns.append(f'Meta description is {len(d)} characters (aim for 120-160)')
    for other, (ot, od) in all_pages_meta['titles'].items():
        if other == rel: continue
        if t and t == ot: errs.append(f'Duplicate title with {other}')
        if d and d == od: errs.append(f'Duplicate meta description with {other}')

    # 10. rel=me llms, phone consistency
    for l in p.linkrels:
        if l.get('rel') == 'me' and 'llms' in (l.get('href') or ''):
            errs.append(f'rel="me" used for {l.get("href")} (rel=me is for profile verification)')
    tels = set(re.findall(r'href="tel:([^"]+)"', p.raw)) | set(re.findall(r'href="sms:([^"?&]+)', p.raw))
    for tel in tels:
        if tel != FACTS['phone_e164']: errs.append(f'Phone link {tel} != {FACTS["phone_e164"]}')

    return errs, warns


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('pages', nargs='*')
    ap.add_argument('--all', action='store_true', help='check every blog post')
    ap.add_argument('--publish-date', help='YYYY-MM-DD the page goes live; dates must match')
    a = ap.parse_args()
    pages = sorted(glob.glob(os.path.join(ROOT, 'blog', '*.html'))) if a.all else [os.path.abspath(x) for x in a.pages]
    if not pages: ap.error('give page paths or --all')
    titles = {}
    for f in glob.glob(os.path.join(ROOT, '**', '*.html'), recursive=True):
        if '/node_modules/' in f or '/design-only/' in f or 'oldbackup' in f: continue
        try: p = load(f)
        except Exception: continue
        if 'noindex' in p.metas.get('robots', ''): continue
        titles[os.path.relpath(f, ROOT).replace(os.sep, '/')] = (p.title, p.metas.get('description', ''))
    meta = {'sitemap': sitemap_entries(), 'titles': titles}
    today = datetime.date.today().isoformat()
    total_e = total_w = 0
    for f in pages:
        head = open(f, encoding='utf-8').read(3000)
        if re.search(r'http-equiv=["\']refresh', head, re.I):
            print(f'SKIP  {os.path.relpath(f, ROOT)}  (redirect page)'); continue
        e, w = check(f, meta, a.publish_date, today)
        total_e += len(e); total_w += len(w)
        status = 'FAIL' if e else ('WARN' if w else 'PASS')
        print(f'{status}  {os.path.relpath(f, ROOT)}  ({len(e)} errors, {len(w)} warnings)')
        for x in e: print('   ERROR  ' + x)
        for x in w: print('   warn   ' + x)
    print(f'\n{len(pages)} page(s): {total_e} errors, {total_w} warnings')
    sys.exit(1 if total_e else 0)


if __name__ == '__main__':
    main()
