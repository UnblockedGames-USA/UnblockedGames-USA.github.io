import os
import re
from bs4 import BeautifulSoup

def fix_html_file(filepath):
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    soup = BeautifulSoup(content, 'html.parser')

    # === FIX 1: Add missing game-overlay (play button) if it's gone ===
    game_frame_container = soup.find('div', id='gameFrameContainer')
    if game_frame_container:
        overlay = game_frame_container.find('div', id='gameOverlay')
        if not overlay:
            iframe = game_frame_container.find('iframe', id='gameFrame')
            if iframe:
                # Create overlay
                new_overlay = soup.new_tag('div', id='gameOverlay')
                new_overlay['class'] = 'game-overlay'
                new_overlay['role'] = 'button'
                new_overlay['aria-label'] = 'Play Game'
                new_overlay['tabindex'] = '0'

                play_btn = soup.new_tag('button', id='playButton')
                play_btn['class'] = 'play-button'
                play_btn['aria-label'] = 'Start game'
                play_btn.string = '▶'

                play_text = soup.new_tag('div')
                play_text['class'] = 'play-text'
                h1 = soup.find('h1')
                title = h1.get_text(strip=True) if h1 else 'Game'
                play_text.string = f'Play {title}'

                new_overlay.append(play_btn)
                new_overlay.append(play_text)

                iframe.insert_before(new_overlay)

    # === FIX 2: Remove broken leftover HTML after similar games section ===
    similar = soup.find('section', class_='similar-games') or soup.find('div', class_='similar-games')
    if similar:
        # Remove everything until we hit .categories or footer
        current = similar.find_next_sibling()
        while current:
            tag_name = current.name
            classes = current.get('class', [])
            if (tag_name == 'div' and 
                ('game-info' in classes or 'game-card' in classes or 'game-link' in classes)):
                to_delete = current
                current = current.find_next_sibling()
                to_delete.decompose()
            else:
                break

    # === FIX 3: Remove duplicate/injected UG_SIMILAR section ===
    for ug in soup.find_all('div', class_='ug-similar'):
        ug.decompose()
    for style in soup.find_all('style', id='ug-similar-css'):
        style.decompose()

    # === FIX 4: Clean up any stray closing tags or extra content ===
    # Remove any remaining broken similar games remnants
    for remnant in soup.find_all(string=re.compile(r'SIMILAR_GAMES_START|UG_SIMILAR')):
        if remnant.parent:
            remnant.parent.decompose()

    # Write cleaned file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(str(soup))

    print(f"✅ Fixed: {os.path.basename(filepath)}")

# === RUN ON ALL GAME PAGES ===
root = r"C:\Users\berra\Documents\GitHub\UnblockedGames-USA.github.io"

skip_files = ['index.html', 'privacy-policy.html', 'contact.html', 'faq.html', 'dmca.html']

for dirpath, _, filenames in os.walk(root):
    for filename in filenames:
        if filename.endswith('.html') and filename not in skip_files:
            filepath = os.path.join(dirpath, filename)
            try:
                fix_html_file(filepath)
            except Exception as e:
                print(f"❌ Error on {filename}: {e}")

print("\n🎉 All game pages have been cleaned and fixed!")