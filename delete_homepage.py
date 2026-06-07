import os
import re

STATIC_DIR = r"C:\Users\26503\Documents\antigravity\fearless-raman\wehuster-static"
LAYOUT_CHUNK = os.path.join(STATIC_DIR, "next_assets", "static", "chunks", "app", "layout-05d0b1f664550a24.js")

# 1. Update logo link in Layout JS chunk
def update_layout_js():
    if not os.path.exists(LAYOUT_CHUNK):
        print(f"Layout chunk not found: {LAYOUT_CHUNK}")
        return

    with open(LAYOUT_CHUNK, "r", encoding="utf-8") as f:
        content = f.read()

    # Logo link replacement: href:"/" -> href:"/cet4"
    target = '(0,t.jsx)("a",{href:"/",className:"flex items-center"'
    replacement = '(0,t.jsx)("a",{href:"/cet4",className:"flex items-center"'

    if target in content:
        content = content.replace(target, replacement)
        with open(LAYOUT_CHUNK, "w", encoding="utf-8") as f:
            f.write(content)
        print("Updated logo link in layout JS chunk.")
    else:
        print("Logo link target not found in layout chunk (already modified?)")

# 2. Update logo link in all HTML files
def update_html_logo_links():
    for root, dirs, files in os.walk(STATIC_DIR):
        for file in files:
            if file.endswith(".html"):
                path = os.path.join(root, file)
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                
                original = content
                # Replace <a href="/" class="flex items-center">
                content = re.sub(
                    r'<a[^>]*href="/"[^>]*class="flex items-center"',
                    '<a href="/cet4" class="flex items-center"',
                    content,
                    flags=re.IGNORECASE
                )
                
                if content != original:
                    with open(path, "w", encoding="utf-8") as f:
                        f.write(content)
                    print(f"Updated logo link in HTML: {path}")

# 3. Create vercel.json in the root directory
def create_vercel_json():
    vercel_path = os.path.join(STATIC_DIR, "vercel.json")
    config_content = """{
  "redirects": [
    {
      "source": "/",
      "destination": "/cet4",
      "permanent": true
    }
  ]
}
"""
    with open(vercel_path, "w", encoding="utf-8") as f:
        f.write(config_content)
    print("Created vercel.json with root redirect to /cet4.")

# 4. Delete index.html from root
def delete_root_index_html():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        os.remove(index_path)
        print(f"Deleted root index.html: {index_path}")
    else:
        print("Root index.html not found.")

if __name__ == "__main__":
    update_layout_js()
    update_html_logo_links()
    create_vercel_json()
    delete_root_index_html()
    print("Homepage deletion and logo link update complete!")
