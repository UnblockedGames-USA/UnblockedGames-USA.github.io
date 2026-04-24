from pathlib import Path
import re

def main():
    root = Path(r"C:\Users\berra\Documents\GitHub\UnblockedGames-USA.github.io")
    
    # Use your good multiplayer page as template
    template_path = root / "categ" / "multiplayer" / "index.html"
    if not template_path.exists():
        print("❌ Cannot find multiplayer/index.html")
        return
    
    template = template_path.read_text(encoding="utf-8")
    
    # Category data
    categories = {
        "shooter":      ("🎯", "#E8192C", "Shooter Games", "Fast-paced shooting action"),
        "platformer":   ("🏃", "#FF9800", "Platformer Games", "Jump, run and master levels"),
        "2-player":     ("👥", "#4CAF50", "2 Player Games", "Play together with friends"),
        "fighting":     ("🥊", "#F44336", "Fighting Games", "Epic battles and combos"),
        "driving":      ("🚗", "#2196F3", "Driving Games", "Race, drift and stunt"),
        "puzzle":       ("🧠", "#9C27B0", "Puzzle Games", "Challenge your brain"),
        "multiplayer":  ("🌐", "#2655cc", "Multiplayer Games", "Connect and Compete in Unblocked Multiplayer"),
        "action":       ("💥", "#FF5722", "Action Games", "Non-stop adrenaline action"),
        "skill":        ("🏆", "#FFC107", "Skill Games", "Test your reflexes and precision"),
        "adventure":    ("🗺️", "#3F51B5", "Adventure Games", "Explore exciting worlds"),
        "racing":       ("🏁", "#FF9800", "Racing Games", "Speed, stunts and competition"),
        "strategy":     ("♟️", "#607D8B", "Strategy Games", "Think and conquer"),
        "sports":       ("⚽", "#4CAF50", "Sports Games", "Play your favorite sports"),
        "simulation":   ("🏙️", "#00BCD4", "Simulation Games", "Realistic life and management"),
        "clicker":      ("🖱️", "#E91E63", "Clicker Games", "Idle and incremental fun"),
        "horror":       ("👻", "#673AB7", "Horror Games", "Face your fears"),
        "kids":         ("🧸", "#FFEB3B", "Kids Games", "Fun for all ages"),
    }
    
    categ_dir = root / "categ"
    fixed = 0
    
    for folder in categ_dir.iterdir():
        if not folder.is_dir():
            continue
        slug = folder.name
        index_path = folder / "index.html"
        if not index_path.exists():
            continue
        
        content = index_path.read_text(encoding="utf-8")
        
        # Extract games grid and pagination from current file
        games_grid_match = re.search(r'(<div class="games-grid"[^>]*>.*?</div>)', content, re.DOTALL)
        pagination_match = re.search(r'(<div class="pagination"[^>]*>.*?</div>)', content, re.DOTALL)
        
        games_grid = games_grid_match.group(1) if games_grid_match else ""
        pagination = pagination_match.group(1) if pagination_match else ""
        
        data = categories.get(slug, ("🎮", "#2655cc", slug.replace('-',' ').title(), "Play awesome unblocked games"))
        
        # Replace key parts
        new_content = template
        new_content = re.sub(r'<title>.*?</title>', f'<title>{data[2]} Unblocked - Free Online Games</title>', new_content)
        new_content = re.sub(r'<h1>.*?</h1>', f'<h1>{data[0]} {data[2]}</h1>', new_content, flags=re.DOTALL)
        new_content = re.sub(r'<p>.*?</p>', f'<p>{data[3]}</p>', new_content, count=1, flags=re.DOTALL)
        new_content = re.sub(r'style="--cat-accent: #2655cc;"', f'style="--cat-accent: {data[1]};"', new_content)
        
        # Replace games grid and pagination
        if games_grid:
            new_content = re.sub(r'<div class="games-grid"[^>]*>.*?</div>', games_grid, new_content, flags=re.DOTALL)
        if pagination:
            new_content = re.sub(r'<div class="pagination"[^>]*>.*?</div>', pagination, new_content, flags=re.DOTALL)
        
        index_path.write_text(new_content, encoding="utf-8")
        print(f"✅ Fixed: categ/{slug}")
        fixed += 1
    
    print(f"\n🎉 Done! Fixed {fixed} category pages.")

if __name__ == "__main__":
    main()