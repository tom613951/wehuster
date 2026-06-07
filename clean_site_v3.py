import os
import re

STATIC_DIR = r"C:\Users\26503\Documents\antigravity\fearless-raman\wehuster-static"
LAYOUT_CHUNK = os.path.join(STATIC_DIR, "next_assets", "static", "chunks", "app", "layout-05d0b1f664550a24.js")

# 1. Clean Layout JS Chunk
def clean_layout_js():
    if not os.path.exists(LAYOUT_CHUNK):
        print(f"Layout chunk not found: {LAYOUT_CHUNK}")
        return

    with open(LAYOUT_CHUNK, "r", encoding="utf-8") as f:
        content = f.read()

    original = content

    # Replace LOG IN button
    login_target = '[(0,t.jsx)("a",{href:"/login",className:"inline-flex items-center justify-center px-5 py-2 mr-3 text-base font-medium text-center text-white rounded-lg bg-yellow-500 hover:bg-yellow-600 focus:ring-4 focus:ring-primary-300",children:"LOG IN"}),(0,t.jsxs)("button"'
    login_replacement = '[(0,t.jsxs)("button"'
    if login_target in content:
        content = content.replace(login_target, login_replacement)
        print("Replaced LOG IN button in layout chunk.")

    # Replace Header menu items
    home_idx = content.find('"Home"')
    about_idx = content.find('"About"')
    if home_idx != -1 and about_idx != -1:
        prefix = "children:["
        prefix_idx = content.rfind(prefix, 0, home_idx)
        suffix_idx = content.find("]", about_idx)
        
        if prefix_idx != -1 and suffix_idx != -1:
            start_pos = prefix_idx + len(prefix)
            end_pos = suffix_idx
            
            new_menu_items = (
                '(0,t.jsx)("li",{children:(0,t.jsx)("a",{href:"/cet4",className:"block py-1 pr-4 pl-4 text-white rounded-md hover:bg-white hover:text-purple-600 transition-colors duration-200",children:"四级真题"})}),'
                '(0,t.jsx)("li",{children:(0,t.jsx)("a",{href:"/cet6",className:"block py-1 pr-4 pl-4 text-white rounded-md hover:bg-white hover:text-purple-600 transition-colors duration-200",children:"六级真题"})})'
            )
            content = content[:start_pos] + new_menu_items + content[end_pos:]
            print("Replaced Header menu items in layout chunk.")
        else:
            print("Could not find menu items array boundaries.")
    else:
        print("Could not find 'Home' or 'About' in layout chunk.")

    if content != original:
        with open(LAYOUT_CHUNK, "w", encoding="utf-8") as f:
            f.write(content)
        print("Updated layout JS chunk successfully!")
    else:
        print("No changes needed for layout JS chunk.")

# 2. Clean HTML Files
def clean_html_file(file_path):
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    original = content

    # 2a. Remove static DOM footer element
    content = re.sub(r'<footer[^>]*>.*?</footer>', '', content, flags=re.DOTALL | re.IGNORECASE)

    # 2b. Remove static DOM header links
    content = re.sub(r'<a href="/login"[^>]*>LOG IN</a>', '', content, flags=re.IGNORECASE)
    content = re.sub(r'<li[^>]*><a[^>]*href="/"[^>]*>Home</a></li>', '', content, flags=re.IGNORECASE)
    content = re.sub(r'<li><a href="/linear_algebra"[^>]*>.*?</a></li>', '', content, flags=re.IGNORECASE)
    content = re.sub(r'<li><a href="/calculus"[^>]*>.*?</a></li>', '', content, flags=re.IGNORECASE)
    content = re.sub(r'<li><a href="/about"[^>]*>.*?</a></li>', '', content, flags=re.IGNORECASE)

    # 2c. Remove serialized footer payload in self.__next_f.push
    footer_start = '[\\"$\\",\\"footer\\",null,'
    footer_end = '\\"© 2026 WeHUSTER All Rights Reserved.\\"}]}]]}]}]'
    
    f_start_idx = content.find(footer_start)
    if f_start_idx != -1:
        f_end_idx = content.find(footer_end, f_start_idx)
        if f_end_idx != -1:
            content = content[:f_start_idx] + "null" + content[f_end_idx + len(footer_end):]
            print(f"Removed footer payload in: {file_path}")

    # 2d. Homepage-specific cleanups
    is_homepage = os.path.basename(file_path) == "index.html" and os.path.dirname(file_path) == STATIC_DIR
    if is_homepage:
        # Remove static DOM cards
        content = re.sub(r'<a data-testid="flowbite-card" href="/linear_algebra".*?</a>', '', content, flags=re.DOTALL)
        content = re.sub(r'<a data-testid="flowbite-card" href="/calculus".*?</a>', '', content, flags=re.DOTALL)
        
        # Remove static DOM Contact Us section
        content = re.sub(r'<section[^>]*>\s*<div[^>]*>\s*<h2[^>]*>Contact Us</h2>.*?</form>\s*</div>\s*</section>', '', content, flags=re.DOTALL)

        # Remove serialized linear_algebra and calculus cards payload in self.__next_f.push
        card2_start = ',[\\"$\\",\\"$L10\\",\\"2\\",{\\"href\\":\\"/linear_algebra\\"'
        card3_end_text = '\\"近五年华中科技大学微积分考试真题和答案\\"}'
        
        c_start_idx = content.find(card2_start)
        if c_start_idx != -1:
            c_end_text_idx = content.find(card3_end_text, c_start_idx)
            if c_end_text_idx != -1:
                c_end_idx = content.find(']]}]', c_end_text_idx)
                if c_end_idx != -1:
                    content = content[:c_start_idx] + content[c_end_idx + 4:]
                    print(f"Removed linear_algebra and calculus cards payload in: {file_path}")

    if content != original:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Updated HTML file: {file_path}")

def clean_all_html_files():
    for root, dirs, files in os.walk(STATIC_DIR):
        for file in files:
            if file.endswith(".html"):
                clean_html_file(os.path.join(root, file))

if __name__ == "__main__":
    clean_layout_js()
    clean_all_html_files()
    print("Cleanup complete!")
