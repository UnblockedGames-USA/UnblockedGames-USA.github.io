from pathlib import Path

def main():
    root = Path(r"C:\Users\berra\Documents\GitHub\UnblockedGames-USA.github.io")
    template = (root / "template_category.html").read_text(encoding="utf-8")
    
    categ_dir = root / "categ"
    
    category_data = {
        "multiplayer":  ("🌐", "#2655cc", "Multiplayer Games", "Connect and Compete in Unblocked Multiplayer"),
        "shooter":      ("🎯", "#E8192C", "Shooter Games", "Fast-paced shooting action"),
        "platformer":   ("🏃", "#FF9800", "Platformer Games", "Jump, run and master levels"),
        "2-player":     ("👥", "#4CAF50", "2 Player Games", "Play together with friends"),
        "fighting":     ("🥊", "#F44336", "Fighting Games", "Epic battles and combos"),
        "driving":      ("🚗", "#2196F3", "Driving Games", "Race and stunt"),
        "puzzle":       ("🧠", "#9C27B0", "Puzzle Games", "Challenge your mind"),
        "action":       ("💥", "#FF5722", "Action Games", "Non-stop adrenaline"),
        "skill":        ("🏆", "#FFC107", "Skill Games", "Test your reflexes"),
        "adventure":    ("🗺️", "#3F51B5", "Adventure Games", "Explore new worlds"),
        "racing":       ("🏁", "#FF9800", "Racing Games", "Speed and competition"),
        "strategy":     ("♟️", "#607D8B", "Strategy Games", "Think and conquer"),
        "sports":       ("⚽", "#4CAF50", "Sports Games", "Play your favorite sports"),
        "simulation":   ("🏙️", "#00BCD4", "Simulation Games", "Realistic experiences"),
        "clicker":      ("🖱️", "#E91E63", "Clicker Games", "Idle and incremental fun"),
        "horror":       ("👻", "#673AB7", "Horror Games", "Face your fears"),
        "kids":         ("🧸", "#FFEB3B", "Kids Games", "Fun for all ages"),
    }
    
    for folder in categ_dir.iterdir():
        if not folder.is_dir(): continue
        slug = folder.name
        index_path = folder / "index.html"
        if not index_path.exists(): continue
            
        data = category_data.get(slug, ("🎮", "#2655cc", slug.replace('-',' ').title(), "Play the best unblocked games"))
        
        content = template.replace("{TITLE}", f"{data[2]} Unblocked - Free Online Games")
        content = content.replace("{DESCRIPTION}", f"Play the best {data[2].lower()} unblocked for free. No download needed.")
        content = content.replace("{KEYWORDS}", f"{slug} games, unblocked {slug}, free online {slug}")
        content = content.replace("{categ_url}", f"/categ/{slug}")
        content = content.replace("{EMOJI}", data[0])
        content = content.replace("{CATEGORY_NAME}", data[2])
        content = content.replace("{SUBTITLE}", data[3])
        content = content.replace("{ACCENT_COLOR}", data[1])
        
        # Keep existing games grid and pagination
        print(f"✅ Updated: categ/{slug}/index.html")
        index_path.write_text(content, encoding="utf-8")
    
    print("\n🎉 All category pages updated successfully!")

if __name__ == "__main__":
    main()