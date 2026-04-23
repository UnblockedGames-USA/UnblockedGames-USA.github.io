"""
rebrand.py — Unblocked Games USA
=================================
HOW TO USE:
1. Put this file in your repo folder (same level as index.html)
2. Open CMD in that folder
3. Run: python rebrand.py
"""

import os
import re

OLD_DOMAIN  = "incredibox-sprunki.github.io"
NEW_DOMAIN  = "unblockedgames-usa.github.io"
OLD_ADSENSE = "ca-pub-7305083056611385"

# ── USA CSS injected once into every page ────────────────────────────────────
USA_CSS = """<style id="usa-rebrand">
    @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Barlow:wght@400;600;700&display=swap');
    :root {
        --primary:     #E8192C !important;
        --secondary:   #2655cc !important;
        --accent:      #E8192C !important;
        --dark-bg:     #000510 !important;
        --dark-card:   #07102b !important;
        --dark-text:   #dce8ff !important;
        --dark-border: rgba(255,255,255,0.08) !important;
    }
    body { background: #000510 !important; color: #dce8ff !important; }
    header {
        background: linear-gradient(90deg,#002868 0%,#0d1f5c 40%,#1a0a2e 60%,#E8192C 100%) !important;
        border-bottom: 3px solid #E8192C !important;
    }
    .logo { font-family: 'Bebas Neue', sans-serif !important; letter-spacing: 2px !important; text-shadow: 0 0 20px rgba(232,25,44,0.6) !important; }
    .game-card { background: #07102b !important; border: 1px solid rgba(255,255,255,0.08) !important; animation: none !important; }
    .game-card:hover { transform: translateY(-6px) !important; box-shadow: 0 12px 35px rgba(0,0,0,0.5), 0 0 0 1px rgba(232,25,44,0.35) !important; border-color: rgba(232,25,44,0.4) !important; }
    .section-title, .categories-title { font-family: 'Bebas Neue', sans-serif !important; background: linear-gradient(135deg,#002868,#2655cc,#E8192C) !important; -webkit-background-clip: text !important; -webkit-text-fill-color: transparent !important; background-clip: text !important; }
    .hero-header, .game-header { background: linear-gradient(135deg,rgba(0,20,80,0.95),rgba(10,5,30,0.9),rgba(100,10,20,0.95)) !important; border: 1px solid rgba(255,255,255,0.07) !important; }
    .hero-header h1, .game-header h1 { font-family: 'Bebas Neue', sans-serif !important; letter-spacing: 3px !important; background: linear-gradient(135deg,#002868,#2655cc,#E8192C) !important; -webkit-background-clip: text !important; -webkit-text-fill-color: transparent !important; background-clip: text !important; }
    .category-item, .category-tag-item { background: linear-gradient(135deg,#1a3a8a,#E8192C) !important; color: white !important; border-radius: 50px !important; border: 1px solid rgba(255,255,255,0.1) !important; }
    .category-grid { display: flex !important; flex-wrap: wrap !important; gap: 8px !important; justify-content: center !important; }
    .game-description, .site-description, .game-container { background: #07102b !important; border: 1px solid rgba(255,255,255,0.08) !important; }
    .game-description h2, .game-description h3, .site-description h2, .site-description h3 { color: #E8192C !important; }
    .play-button { background: linear-gradient(135deg,#002868,#E8192C) !important; }
    .fullscreen-btn:hover { background: #E8192C !important; }
    #scrollToTopBtn { background: linear-gradient(135deg,#002868,#E8192C) !important; }
    footer { background: #010812 !important; border-top: 2px solid #E8192C !important; }
    .footer-section h3 { color: #E8192C !important; }
    .footer-section p  { color: rgba(255,255,255,0.45) !important; }
    .footer-bottom      { color: #ffffff !important; }
    .footer-bottom p    { color: #ffffff !important; }
    .footer-links a     { color: #ffffff !important; }
    .footer-links a:hover { color: rgba(255,255,255,0.65) !important; }
    .social-icons a:hover { background: #E8192C !important; }
    .main-nav a:hover { background-color: #E8192C !important; }
    .search-bar button { background: #E8192C !important; }
</style>"""

# ── Google Analytics ─────────────────────────────────────────────────────────
GA_SNIPPET = """    <!-- Google Analytics -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-L6FNHSMWF4"></script>
    <script>
        window.dataLayer = window.dataLayer || [];
        function gtag(){dataLayer.push(arguments);}
        gtag('js', new Date());
        gtag('config', 'G-L6FNHSMWF4');
    </script>"""

# ── Patterns ─────────────────────────────────────────────────────────────────

# Russian tracker
RE_TRACKER      = re.compile(r'<div class="analytics-counter">.*?</div>', re.DOTALL)
RE_LIVEINTERNET = re.compile(r'<!--LiveInternet counter-->.*?<!--/LiveInternet-->', re.DOTALL)

# Footer brand block — the whole footer-content div with brand info inside
# Matches: <div class="footer-content">...</div>
RE_FOOTER_CONTENT = re.compile(r'<div class="footer-content">.*?</div>\s*', re.DOTALL)

# AdSense — remove publisher ID, leave slot tag intact but empty client
RE_ADSENSE_CLIENT = re.compile(
    r'data-ad-client="ca-pub-[0-9]+"',
    re.IGNORECASE
)
# Also the script loader that has the client in the URL
RE_ADSENSE_URL = re.compile(
    r'(pagead2\.googlesyndication\.com/pagead/js/adsbygoogle\.js\?client=)ca-pub-[0-9]+',
    re.IGNORECASE
)

# Remove inline background-color from category items
RE_CAT_BG = re.compile(
    r'(class="category-item"[^>]*?)\s*style="background-color:\s*#[0-9A-Fa-f]{3,6};"',
    re.IGNORECASE
)
RE_TAG_BG = re.compile(
    r'(class="category-tag-item"[^>]*?)\s*style="background-color:\s*#[0-9A-Fa-f]{3,6};"',
    re.IGNORECASE
)

# Old image URLs still on old domain
RE_IMG_OLD = re.compile(
    r'https://incredibox-sprunki\.github\.io/([^"\'>\s]+\.png)',
    re.IGNORECASE
)

# ── Processor ─────────────────────────────────────────────────────────────────

def process(filepath):
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        html = f.read()

    original = html

    # 1. Domain
    html = html.replace(OLD_DOMAIN, NEW_DOMAIN)

    # 2. Brand name
    html = html.replace("Unbanned Games G+",     "Unblocked Games USA")
    html = html.replace("Unbanned Games G plus", "Unblocked Games USA")
    html = html.replace("UnbannedGamesG+",       "UnblockedGamesUSA")
    html = html.replace("Unbanned",              "Unblocked")
    html = html.replace("unbanned",              "unblocked")

    # 3. AdSense — remove publisher ID, leave everything else
    html = RE_ADSENSE_CLIENT.sub('data-ad-client=""', html)
    html = RE_ADSENSE_URL.sub(r'\1', html)
    # Also plain string replacement as fallback
    html = html.replace(OLD_ADSENSE, "")

    # 4. Fix image paths — images are at ROOT (no /images/ subfolder)
    html = html.replace(f"https://{NEW_DOMAIN}/images/", f"https://{NEW_DOMAIN}/")
    html = RE_IMG_OLD.sub(lambda m: f"https://{NEW_DOMAIN}/{m.group(1)}", html)

    # 5. Remove Russian tracker
    html = RE_LIVEINTERNET.sub('', html)
    html = RE_TRACKER.sub('', html)

    # 6. Remove footer-content block (brand section with social icons)
    html = RE_FOOTER_CONTENT.sub('', html)

    # 7. Strip inline background-color from category items
    html = RE_CAT_BG.sub(r'\1', html)
    html = RE_TAG_BG.sub(r'\1', html)

    # 8. Google Analytics
    if 'G-L6FNHSMWF4' not in html and '</head>' in html:
        html = html.replace('</head>', GA_SNIPPET + '\n</head>', 1)

    # 9. USA CSS
    if 'usa-rebrand' not in html and '</head>' in html:
        html = html.replace('</head>', USA_CSS + '\n</head>', 1)

    # 10. Flag emoji on logo
    html = re.sub(
        r'(<a[^>]+class="logo"[^>]*>)\s*(Unblocked Games USA)\s*(</a>)',
        r'\1 🇺🇸 Unblocked Games USA \3',
        html
    )

    if html != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        return True
    return False

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    root = os.getcwd()
    print(f"\n🇺🇸  Unblocked Games USA — Rebranding")
    print(f"📁  Folder: {root}\n")

    total = 0
    changed = 0

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if not d.startswith('.')]
        for filename in filenames:
            if not filename.endswith('.html'):
                continue
            total += 1
            filepath = os.path.join(dirpath, filename)
            rel = os.path.relpath(filepath, root)
            try:
                if process(filepath):
                    changed += 1
                    print(f"  ✅  {rel}")
                else:
                    print(f"  ⏭️   {rel}  (already clean)")
            except Exception as e:
                print(f"  ❌  {rel}  ERROR: {e}")

    print(f"\n{'─'*55}")
    print(f"✅  {changed} files updated")
    print(f"⏭️   {total - changed} already clean")
    print(f"📄  {total} total files scanned")
    print(f"\n📌  Now push to GitHub:")
    print(f"      git add .")
    print(f'      git commit -m "Rebrand to Unblocked Games USA"')
    print(f"      git push\n")

if __name__ == "__main__":
    main()