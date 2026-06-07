import os
import re
import urllib.request
import urllib.parse
from concurrent.futures import ThreadPoolExecutor

BASE_URL = "https://www.wehuster.com"
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

# File extensions to exclude from local download (large assets go remote)
REMOTE_EXTENSIONS = {'.pdf', '.mp3'}

def get_html(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as response:
            return response.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def download_file(url, local_path):
    local_dir = os.path.dirname(local_path)
    os.makedirs(local_dir, exist_ok=True)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as response:
            with open(local_path, "wb") as f:
                f.write(response.read())
        print(f"Downloaded asset: {url}")
        return True
    except Exception as e:
        print(f"Error downloading asset {url}: {e}")
        return False

def clean_html_content(html_content, is_category_page=False):
    # 1. Rename _next references to next_assets
    html_content = html_content.replace('/_next/', '/next_assets/')
    html_content = html_content.replace('/_next?', '/next_assets?')
    html_content = html_content.replace('\\"/_next/', '\\"/next_assets/')

    # 2. Redirect PDF download button
    pdf_assets = re.findall(r'["\'](/static/[^"\']+\.pdf)["\']', html_content)
    if pdf_assets:
        pdf_path = BASE_URL + pdf_assets[0]
        button_pattern = r'(<button[^>]*>\s*<span[^>]*>Download PDF</span>\s*</button>)'
        if re.search(button_pattern, html_content, re.IGNORECASE):
            html_content = re.sub(
                button_pattern,
                rf'<a href="{pdf_path}" download class="inline-block">\1</a>',
                html_content,
                flags=re.IGNORECASE
            )

    # 3. Rewrite all static PDF/MP3 to point to the remote server
    def make_remote_urls(content):
        def replacer(match):
            quote = match.group(1)
            path = match.group(2)
            return f'{quote}{BASE_URL}{path}{quote}'
        return re.sub(r'(["\'])(/static/[^"\']+\.(?:pdf|mp3))(["\'])', replacer, content)
    
    html_content = make_remote_urls(html_content)

    # 4. Remove static HTML footer
    html_content = re.sub(r'<footer[^>]*>.*?</footer>', '', html_content, flags=re.DOTALL | re.IGNORECASE)

    # 5. Remove header links and login button
    html_content = re.sub(r'<a href="/login"[^>]*>LOG IN</a>', '', html_content, flags=re.IGNORECASE)
    html_content = re.sub(r'<li[^>]*><a[^>]*href="/"[^>]*>Home</a></li>', '', html_content, flags=re.IGNORECASE)
    html_content = re.sub(r'<li><a href="/linear_algebra"[^>]*>.*?</a></li>', '', html_content, flags=re.IGNORECASE)
    html_content = re.sub(r'<li><a href="/calculus"[^>]*>.*?</a></li>', '', html_content, flags=re.IGNORECASE)
    html_content = re.sub(r'<li><a href="/about"[^>]*>.*?</a></li>', '', html_content, flags=re.IGNORECASE)

    # 6. Point WeHUSTER logo to /cet4
    html_content = re.sub(
        r'<a[^>]*href="/"[^>]*class="flex items-center"',
        '<a href="/cet4" class="flex items-center"',
        html_content,
        flags=re.IGNORECASE
    )

    # 7. Replace serialized footer payload in self.__next_f.push with null
    footer_start = '[\\"$\\",\\"footer\\",null,'
    footer_end = 'All Rights Reserved.\\"}]}]]}]}]'
    
    f_start_idx = html_content.find(footer_start)
    if f_start_idx != -1:
        f_end_idx = html_content.find(footer_end, f_start_idx)
        if f_end_idx != -1:
            html_content = html_content[:f_start_idx] + "null" + html_content[f_end_idx + len(footer_end):]

    return html_content

def download_assets_from_html(html_content):
    # Find any images, stylesheets or scripts we need to host locally
    links = re.findall(r'href=["\']([^"\']+)["\']', html_content)
    srcs = re.findall(r'src=["\']([^"\']+)["\']', html_content)
    
    assets_to_download = []
    
    for val in links + srcs:
        parsed = urllib.parse.urlparse(val)
        if (not parsed.netloc or parsed.netloc == "www.wehuster.com" or parsed.netloc == "wehuster.com"):
            path = parsed.path
            if path.startswith("/"):
                # Clean path
                clean_p = path.replace("\\", "/")
                if "?" in clean_p:
                    clean_p = clean_p.split("?")[0]
                
                ext = os.path.splitext(clean_p)[1].lower()
                
                # We host CSS, JS, WOFF2 and images locally
                # Do NOT download pdf or mp3
                if ext in {'.css', '.js', '.woff2', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico'}:
                    assets_to_download.append((path, clean_p))

    for original_path, clean_path_local in assets_to_download:
        # Determine local file path
        # If it originally referenced _next, it maps to next_assets
        local_rel_path = clean_path_local.lstrip("/")
        if local_rel_path.startswith("_next/"):
            local_rel_path = local_rel_path.replace("_next/", "next_assets/", 1)
        
        dest_path = os.path.join(OUTPUT_DIR, local_rel_path)
        if not os.path.exists(dest_path):
            download_file(BASE_URL + original_path, dest_path)

def process_subpage(path):
    print(f"Checking subpage: {path}")
    local_dir = os.path.join(OUTPUT_DIR, path.lstrip("/"))
    local_file = os.path.join(local_dir, "index.html")
    
    # Check if page already exists
    if os.path.exists(local_file):
        # We already have this page. Keep it.
        return True

    print(f"New page discovered! Downloading: {path}")
    html_content = get_html(BASE_URL + path)
    if not html_content:
        return False
        
    # Download assets from this subpage
    download_assets_from_html(html_content)
    
    # Clean HTML
    cleaned = clean_html_content(html_content)
    
    # Save file
    os.makedirs(local_dir, exist_ok=True)
    with open(local_file, "w", encoding="utf-8") as f:
        f.write(cleaned)
    print(f"Saved new page: {path}")
    return True

def update_category(category_name):
    # category_name should be "cet4" or "cet6"
    url = f"{BASE_URL}/{category_name}"
    print(f"Updating category {category_name} index page from: {url}")
    html_content = get_html(url)
    if not html_content:
        print(f"Failed to fetch category page: {url}")
        return

    # Extract all links
    links = re.findall(r'href=["\']([^"\']+)["\']', html_content)
    subpage_links = []
    
    # Find all subpages like /cet4/cet4_... or /cet6/cet6_...
    pattern = rf'^/{category_name}/{category_name}_\w+'
    for link in links:
        parsed = urllib.parse.urlparse(link)
        path = parsed.path
        if re.match(pattern, path):
            if path not in subpage_links:
                subpage_links.append(path)

    print(f"Found {len(subpage_links)} links in category index.")
    
    # Crawl any new subpages in parallel
    with ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(process_subpage, subpage_links)

    # Save the cleaned category index page
    download_assets_from_html(html_content)
    cleaned_index = clean_html_content(html_content, is_category_page=True)
    
    local_index_path = os.path.join(OUTPUT_DIR, category_name, "index.html")
    os.makedirs(os.path.dirname(local_index_path), exist_ok=True)
    with open(local_index_path, "w", encoding="utf-8") as f:
        f.write(cleaned_index)
    print(f"Updated category index: {local_index_path}")

def run_update():
    print("Starting site incremental update...")
    update_category("cet4")
    update_category("cet6")
    print("Site update complete!")

if __name__ == "__main__":
    run_update()
