#!/usr/bin/env python3
"""Build menu-preview.html from menu-data.json.

Usage: python3 tools/build_menu.py   (run from the project root)
Edit menu-data.json to add dishes, photos, allergens or flags, then rebuild.
"""
import json
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
data = json.loads((ROOT / "menu-data.json").read_text())
cats = data["categories"]
FLAG_CLASS = {"Popular": "popular", "New": "new", "Weekends only": "weekend", "Sold out": "sold"}


def heat(n):
    if not n:
        return ""
    dots = "".join(f'<i class="{"on" if k < n else ""}"></i>' for k in range(3))
    return f'<span class="heat" role="img" aria-label="Heat {n} of 3">{dots}</span>'


def dish(d):
    img = d.get("image")
    flags = d.get("flags", [])
    cls = ["dish"] + ([] if img else ["no-img"]) + (["sold"] if "Sold out" in flags else [])
    picture = ""
    if img:
        jpg = img.rsplit(".", 1)[0] + ".jpg"
        picture = (f'<picture><source type="image/webp" srcset="{img}">'
                   f'<img class="dish-img" src="{jpg}" width="480" height="480" loading="lazy" decoding="async" alt="{escape(d["alt"])}"></picture>')
    flag_html = ""
    if flags:
        flag_html = '<span class="flags">' + "".join(
            f'<span class="flag {FLAG_CLASS.get(f, "")}">{escape(f)}</span>' for f in flags) + "</span>"
    meta = []
    if d.get("origin"):
        meta.append(escape(d["origin"]))
    if d.get("serves"):
        meta.append(f'Serves {escape(d["serves"])}')
    if d.get("allergens"):
        meta.append("<b>Contains:</b> " + ", ".join(escape(a) for a in d["allergens"]))
    meta_html = f'<p class="dish-meta">{" · ".join(meta)}</p>' if meta else ""
    foot = heat(d.get("heat", 0)) + ('<span class="farm-tag">From our farm</span>' if d.get("farm") else "") + "".join(f'<span class="diet">{escape(x)}</span>' for x in d.get("diet", []))
    foot_html = f'<div class="dish-foot">{foot}</div>' if foot else ""
    price_label = f'{escape(d["price"])}<span class="vh"> (sold out today)</span>' if "Sold out" in flags else escape(d["price"])
    return f'''          <li class="{' '.join(cls)}">
            {picture}
            <div class="dish-body">
              <div class="dish-top"><div><h3>{escape(d["name"])}</h3>{flag_html}</div><span class="price">{price_label}</span></div>
              {meta_html}
              <p class="dish-desc">{escape(d["desc"])}</p>
              {foot_html}
            </div>
          </li>'''


chips = "\n".join(
    f'      <li><a href="#{c["id"]}">{escape(c["name"])}<span class="count">{len(c["dishes"])}</span></a></li>' for c in cats)
sections = "\n".join(f'''  <section class="cat-section" id="{c["id"]}" aria-labelledby="{c["id"]}-title">
    <div class="wrap cat-head">
      <div><h2 id="{c["id"]}-title">{escape(c["name"])}</h2><p class="note">{escape(c["note"])}</p></div>
      <ul class="dish-list">
{chr(10).join(dish(d) for d in c["dishes"])}
      </ul>
    </div>
  </section>''' for c in cats)
total = sum(len(c["dishes"]) for c in cats)

_all = [d for c in cats for d in c["dishes"]]
_legend = []
if any(d.get("heat") for d in _all):
    _legend.append(f'        <span>{heat(2)} Heat, out of 3</span>')
_tags = (['<span class="farm-tag">From our farm</span>'] if any(d.get("farm") for d in _all) else []) + [
    f'<span class="diet">{x}</span>' for x in ("Vegan", "Vegetarian", "Gluten-free") if any(x in d.get("diet", []) for d in _all)]
if _tags:
    _legend.append("        <span>" + " ".join(_tags) + "</span>")
legend_html = "\n".join(_legend)

# ---------- schema.org Menu (JSON-LD) from the same data ----------
DIET_SCHEMA = {"Vegan": "https://schema.org/VeganDiet", "Vegetarian": "https://schema.org/VegetarianDiet",
               "Gluten-free": "https://schema.org/GlutenFreeDiet"}


def menu_item_ld(d):
    item = {"@type": "MenuItem", "name": d["name"], "description": d["desc"],
            "offers": {"@type": "Offer", "price": d["price"].lstrip("$"), "priceCurrency": "CAD"}}
    diets = [DIET_SCHEMA[x] for x in d.get("diet", []) if x in DIET_SCHEMA]
    if diets:
        item["suitableForDiet"] = diets if len(diets) > 1 else diets[0]
    if d.get("image"):
        item["image"] = d["image"]
    return item


menu_ld = {
    "@context": "https://schema.org", "@type": "Menu", "name": "Gracefield Foods & Farms menu", "inLanguage": "en-CA",
    "hasMenuSection": [{"@type": "MenuSection", "name": c["name"], "description": c["note"],
                        "hasMenuItem": [menu_item_ld(d) for d in c["dishes"]]} for c in cats],
}
menu_ld_html = json.dumps(menu_ld, ensure_ascii=False, indent=1).replace("</", "<\\/")

page = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex, nofollow"><!-- REVIEW PREVIEW ONLY: remove on the real site -->
<title>Menu · Gracefield Foods &amp; Farms, Edmonton</title>
<meta name="description" content="The full Gracefield Foods &amp; Farms menu: nyama choma, brochette, stews, matoke, isombe, ugali, sides, snacks and drinks. Call or text 587-566-0074 to order.">
<!-- LAUNCH: replace relative URLs with the full domain (https://…) and add <link rel="canonical">. -->
<meta name="theme-color" content="#f4efe6">
<link rel="icon" href="assets/favicon.svg" type="image/svg+xml">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Gracefield Foods &amp; Farms">
<meta property="og:title" content="The menu · Gracefield Foods &amp; Farms">
<meta property="og:description" content="{total} dishes: nyama choma, matoke, isombe, chapati and more. Call or text 587-566-0074 to order for pickup.">
<meta property="og:image" content="assets/share-ea-1200x630.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Grilled nyama choma with ugali, matoke, isombe, chapati and fried plantain">
<meta property="og:locale" content="en_CA">
<meta name="twitter:card" content="summary_large_image">
<script type="application/ld+json">
{menu_ld_html}
</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo+Black&family=Bricolage+Grotesque:opsz,wght@12..96,400;12..96,500;12..96,600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/gracefield.css">
</head>
<body>
<!-- Generated by tools/build_menu.py from menu-data.json. Edit the JSON, not this file. -->
<a class="skip" href="#main">Skip to content</a>

<header class="site-header is-static">
  <div class="brand-group">
    <a class="brand" href="homepage-preview.html">Gracefield <span class="brand-sub">Foods &amp; Farms</span></a>
    <nav aria-label="Menu"><a class="nav-primary" href="menu-preview.html" aria-current="page">Menu</a></nav>
  </div>
  <button class="menu-toggle" type="button" aria-expanded="false" aria-controls="site-nav"><span class="bars" aria-hidden="true"></span><span class="label">More</span></button>
  <nav class="nav-utility-wrap" id="site-nav" aria-label="Main">
    <ul class="nav-utility">
      <li><a href="homepage-preview.html#order">How to order</a></li>
      <li><a href="homepage-preview.html#about">Our farm</a></li>
      <li><a href="homepage-preview.html#visit">Visit</a></li>
    </ul>
  </nav>
</header>

<main id="main">
  <section class="page-hero" aria-labelledby="page-title">
    <div class="wrap">
      <h1 id="page-title">The menu.</h1>
      <div class="row">
        <p class="lede">{total} dishes across {len(cats)} sections. Find your plate, then call or text and we'll have it hot for pickup.</p>
        <div class="hero-call"><a class="btn btn-primary" href="tel:+15875660074" data-callbar-anchor>Call 587-566-0074 to order</a><p class="open-status" data-open-status hidden></p></div>
      </div>
      <div class="legend">
{legend_html}
        <span>Allergies? Tell us when you call or text.</span>
      </div>
      <span class="placeholder-note">Prices from the Gracefield menu · allergens and farm tags to confirm</span>
    </div>
  </section>

  <nav class="cat-bar" aria-label="Menu sections">
    <ul class="cat-chips">
{chips}
    </ul>
  </nav>

{sections}
</main>

<footer class="site-footer">
  <div class="wrap">
    <div><a class="brand" href="homepage-preview.html">Gracefield <span class="brand-sub">Foods &amp; Farms</span></a><p>African kitchen &amp; farm · Edmonton, Alberta</p>
      <ul class="foot-social" aria-label="Gracefield online">
        <li><a href="https://www.instagram.com/sandrineuwase01/" rel="noopener" target="_blank">Instagram<span class="vh"> (opens in a new tab)</span></a></li>
        <li><a href="https://www.tiktok.com/@uwasesandrine709" rel="noopener" target="_blank">TikTok<span class="vh"> (opens in a new tab)</span></a></li>
        <li><a href="https://www.facebook.com/search/top?q=Gracefield%20Foods%20and%20Farms%20Ltd" rel="noopener" target="_blank">Facebook<span class="vh"> (opens in a new tab)</span></a></li>
        <li><a href="mailto:gracefieldfoodsandfarms@gmail.com">gracefieldfoodsandfarms@gmail.com</a></li>
      </ul>
    </div>
    <div>
      <a class="foot-phone" href="tel:+15875660074">587-566-0074</a>
      <p>Tue–Sun 11:00–21:00</p>
      <span class="placeholder-note">Hours to confirm</span>
    </div>
    <nav aria-label="Footer">
      <ul class="foot-links">
        <li><a href="menu-preview.html">Menu</a></li>
        <li><a href="homepage-preview.html#order">How to order</a></li>
        <li><a href="homepage-preview.html#about">Our farm</a></li>
        <li><a href="homepage-preview.html#visit">Visit</a></li>
      </ul>
    </nav>
  </div>
</footer>

<div class="callbar"><p class="open-status" data-open-status hidden></p><a class="btn btn-primary" href="tel:+15875660074">Call 587-566-0074 to order</a></div>

<script src="assets/gracefield.js"></script>
</body>
</html>
'''
(ROOT / "menu-preview.html").write_text(page)
print(f"menu-preview.html: {total} dishes, {len(cats)} categories")


# ---------- Homepage: favourites, dish count, category chips ----------
# Rewrites only the regions between <!-- build:NAME --> markers in homepage-preview.html.
import re

WORDS = {1: "One", 2: "Two", 3: "Three", 4: "Four", 5: "Five", 6: "Six"}
favs = [d for c in cats for d in c["dishes"] if d.get("home")]
if len(favs) > 6:
    raise SystemExit(f'{len(favs)} dishes have "home": true. Keep the homepage to 6 or fewer.')


def home_item(d):
    sold = "Sold out" in d.get("flags", [])
    origin = f'<span class="region">{escape(d["origin"])}.</span> ' if d.get("origin") else ""
    tag = (' <span class="farm-tag">From our farm</span>' if d.get("farm") else "") + (' <span class="flag sold">Sold out today</span>' if sold else "")
    return (f'            <li class="menu-item{" sold" if sold else ""}">\n'
            f'              <h3>{escape(d["name"])}</h3><span class="price">{escape(d["price"])}</span>\n'
            f'              <p>{origin}{escape(d["desc"])}{tag}</p>\n'
            f'            </li>\n')


home_regions = {
    "lede": f'{WORDS.get(len(favs), len(favs))} house favourites. The full menu has {total} dishes.',
    "favourites": '          <ul class="menu-list">\n' + "".join(home_item(d) for d in favs) + '          </ul>\n',
    "chips": '            <ul class="cat-chips">\n' + "".join(
        f'              <li><a href="menu-preview.html#{c["id"]}">{escape(c["name"])}<span class="count">{len(c["dishes"])}</span></a></li>\n'
        for c in cats) + '            </ul>\n',
}
home_path = ROOT / "homepage-preview.html"
home = home_path.read_text()
for name, html in home_regions.items():
    pattern = re.compile(rf'(<!-- build:{name} -->\n?).*?(<!-- /build:{name} -->)', re.S)
    if not pattern.search(home):
        raise SystemExit(f"Marker build:{name} missing in homepage-preview.html")
    home = pattern.sub(lambda m: m.group(1) + html + m.group(2), home, count=1)
home_path.write_text(home)
print(f"homepage-preview.html: {len(favs)} favourites, {len(cats)} category chips")


# ---------- Cache-busting: stamp ?v=<hash> on the shared CSS/JS links ----------
# Browsers keep old copies of gracefield.css/js; a content hash forces a fresh download after every change.
import hashlib

for asset in ("gracefield.css", "gracefield.js"):
    ver = hashlib.md5((ROOT / "assets" / asset).read_bytes()).hexdigest()[:8]
    for page_name in ("homepage-preview.html", "menu-preview.html", "hero-preview.html"):
        path = ROOT / page_name
        if path.exists():
            text = path.read_text()
            path.write_text(re.sub(rf'assets/{re.escape(asset)}(\?v=\w+)?"', f'assets/{asset}?v={ver}"', text))
    print(f"{asset} stamped ?v={ver}")
