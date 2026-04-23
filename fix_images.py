import os

folder_path = r"C:\Users\berra\Documents\GitHub\UnblockedGames-USA.github.io"

def fix_image_paths(content):
    replacements = [
        ('https://unblockedgames-usa.github.io/', 'images/'),
        ('https://unblockedgames-usa.github.io', 'images/'),
        ('src="', 'src="images/'),
        ("src='", "src='images/"),
        ('url(', 'url(images/'),
        ('background-image:url(', 'background-image:url(images/'),
    ]
    
    for old, new in replacements:
        content = content.replace(old, new)
    
    return content

count = 0
for root, dirs, files in os.walk(folder_path):
    for file in files:
        if file.endswith('.html'):
            filepath = os.path.join(root, file)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                new_content = fix_image_paths(content)
                
                if new_content != content:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    count += 1
                    print(f"✅ Updated: {file}")
            except Exception as e:
                print(f"❌ Error with {file}: {e}")

print(f"\n🎉 Finished! Updated {count} HTML files.")