import os
from pathlib import Path
import shutil
import subprocess
import re

def slug_to_title(slug: str) -> str:
    """Convert folder-name to nice title (e.g. all-star-blast → All Star Blast)"""
    return ' '.join(word.capitalize() for word in slug.split('-'))

def main():
    repo_root = Path(r"C:\Users\berra\Documents\GitHub\UnblockedGames-USA.github.io")
    template_path = repo_root / "template.html"
    
    if not template_path.exists():
        print("❌ Please save the clean 'zoom-be-3' HTML content (the first <FILE> you provided) as 'template.html' in the repo root.")
        print("   Then run this script again.")
        return
    
    template = template_path.read_text(encoding="utf-8")
    
    # Folders to skip
    exclude = {'.git', 'images', 'categ', 'assets', '__pycache__', 'node_modules', '.github'}
    
    game_folders = [
        d for d in repo_root.iterdir()
        if d.is_dir() and not d.name.startswith('.') and d.name not in exclude
    ]
    
    print(f"Found {len(game_folders)} potential game folders. Starting update...\n")
    
    updated_count = 0
    for folder in game_folders:
        slug = folder.name
        index_path = folder / "index.html"
        
        if not index_path.exists():
            print(f"⚠️  Skipping {slug} — no index.html found")
            continue
        
        game_title = slug_to_title(slug)
        
        # Standard URLs for this game
        iframe_url = f"https://iframe.unblocked-76-games.org/{slug}-main"
        image_url = f"https://unblockedgames-usa.github.io/images/{slug}.png"
        page_url = f"https://unblockedgames-usa.github.io/{slug}"
        
        # Start with clean template
        new_content = template
        
        # === 1. Replace slug everywhere ===
        new_content = new_content.replace("zoom-be-3", slug)
        
        # === 2. Replace titles ===
        new_content = new_content.replace("Zoom Be 3", game_title)
        new_content = re.sub(
            r"Zoom Be 3 Unblocked.*?Unblocked Games USA",
            f"{game_title} Unblocked — Free {game_title} Game | Unblocked Games USA",
            new_content,
            flags=re.DOTALL
        )
        
        # === 3. Fix iframe ===
        new_content = new_content.replace(
            "https://iframe.unblocked-76-games.org/zoom-be-3-main",
            iframe_url
        )
        
        # === 4. Fix image URLs ===
        new_content = new_content.replace(
            "https://unblockedgames-usa.github.io/images/zoom-be-3.png",
            image_url
        )
        
        # === 5. Fix canonical + OG URLs ===
        new_content = re.sub(
            r"https://unblockedgames-usa\.github\.io/zoom-be-3",
            page_url,
            new_content
        )
        
        # === 6. Update game header h1 + p ===
        new_content = re.sub(
            r"<h1>.*?</h1>",
            f"<h1>{game_title} Unblocked</h1>",
            new_content,
            flags=re.DOTALL | re.IGNORECASE
        )
        
        # Basic description (you can edit later)
        basic_p = f"{game_title} is a fun unblocked game. Play it instantly at school!"
        new_content = re.sub(
            r"<p>The final cooperative adventure:.*?</p>",
            f"<p>{basic_p}</p>",
            new_content,
            flags=re.DOTALL
        )
        
        # === Backup old file ===
        if index_path.exists():
            backup_path = index_path.with_suffix(".old.html")
            shutil.copy2(index_path, backup_path)
        
        # === Write new clean index.html ===
        index_path.write_text(new_content, encoding="utf-8")
        print(f"✅ Updated → {slug}/index.html")
        updated_count += 1
    
    print(f"\n🎉 Finished! Updated {updated_count} games.")
    
    # === Git commit & push ===
    try:
        print("\nCommitting changes to Git...")
        subprocess.run(["git", "add", "."], cwd=repo_root, check=True)
        commit_msg = f"feat: standardize {updated_count} game pages to new Zoom Be 3 template"
        subprocess.run(["git", "commit", "-m", commit_msg], cwd=repo_root, check=True)
        print("Pushing to GitHub...")
        subprocess.run(["git", "push"], cwd=repo_root, check=True)
        print("🚀 Successfully pushed to GitHub!")
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Git command failed: {e}")
        print("   You can run 'git push' manually if needed.")
    except Exception as e:
        print(f"Error during git: {e}")

if __name__ == "__main__":
    main()