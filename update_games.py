import os
from pathlib import Path

def main():
    repo_root = Path(r"C:\Users\berra\Documents\GitHub\UnblockedGames-USA.github.io")
    
    if not repo_root.exists():
        print("❌ Repository path not found!")
        return
    
    # Files to delete
    old_file_names = ["index.old.html", "index.old", "index.old.htm"]
    
    # Folders to skip
    exclude = {'.git', 'images', 'categ', 'assets', '__pycache__', 'node_modules', '.github'}
    
    deleted_count = 0
    skipped_folders = 0
    
    print("🔍 Searching for old backup files...\n")
    
    for folder in repo_root.iterdir():
        if not folder.is_dir() or folder.name in exclude or folder.name.startswith('.'):
            continue
            
        skipped_folders += 1
        for old_name in old_file_names:
            old_file = folder / old_name
            if old_file.exists():
                try:
                    old_file.unlink()  # Delete the file
                    print(f"🗑️  Deleted: {folder.name}/{old_name}")
                    deleted_count += 1
                except Exception as e:
                    print(f"❌ Failed to delete {folder.name}/{old_name} → {e}")
    
    print("\n" + "="*50)
    print(f"✅ Cleanup completed!")
    print(f"   • Files deleted : {deleted_count}")
    print(f"   • Game folders checked : {skipped_folders}")
    print("="*50)

if __name__ == "__main__":
    main()