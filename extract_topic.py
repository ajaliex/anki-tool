import json
import re
import sys
import os
import glob
from html.parser import HTMLParser

class TopicParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_doc = False
        self.in_title = False
        self.in_param = False
        
        self.title_text = ""
        self.categories = []
        self.content_html = ""
        
        # Flags to capture "param" text for category
        self.current_param_text = ""

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        class_list = attrs_dict.get('class', '').split()
        id_val = attrs_dict.get('id', '')

        if tag == 'title':
            self.in_title = True
        
        if 'param' in class_list:
            self.in_param = True
            self.current_param_text = ""
        
        if id_val == 'doc' or self.in_doc:
            if id_val == 'doc':
                self.in_doc = True
            else:
                # Reconstruct the tag
                self.content_html += f"<{tag}"
                for k, v in attrs:
                    self.content_html += f' {k}="{v}"'
                self.content_html += ">"

    def handle_endtag(self, tag):
        if tag == 'title':
            self.in_title = False
        
        if self.in_param and tag == 'div': # assuming params are divs based on provided info
            self.in_param = False
            self.categories.append(self.current_param_text.strip())
            
        if self.in_doc:
            if tag == 'div' and self.content_html.count('<div') == self.content_html.count('</div>') + 1:
                # This logic is flawed for nested divs without a proper tree.
                # However, for 'doc', simpler regex might be safer for extraction if parser is complex.
                # Let's switch to regex for the 'doc' part or just dump everything until the end?
                # Actually, HTMLParser is stream-based, so reconstruction is hard.
                # Let's restart with a simpler Regex approach for the whole file since we need a specific div's innerHTML.
                pass
            self.content_html += f"</{tag}>"

    def handle_data(self, data):
        if self.in_title:
            self.title_text += data
        if self.in_param:
            self.current_param_text += data
        if self.in_doc:
            self.content_html += data

# Alternative simpler approach using Regex for robust "inner html" extraction of a specific ID
# since HTMLParser is tricky for reconstructing exact HTML source including attributes.

def extract_data_from_file_safe(file_path):
    encodings = ['utf-8', 'cp932', 'shift_jis']
    for enc in encodings:
        try:
            return extract_data_regex(file_path, encoding=enc)
        except Exception as e:
            continue
    print(f"Failed to read {file_path} with tried encodings.")
    return None

# Update extract_data_regex signature to accept encoding
def extract_data_regex(file_path, encoding='utf-8'):
    with open(file_path, 'r', encoding=encoding) as f:
        html_content = f.read()

    # Title
    title_match = re.search(r'<title>(.*?)</title>', html_content, re.DOTALL | re.IGNORECASE)
    full_title = title_match.group(1).replace(' - スタディング', '').strip() if title_match else "Unknown"

    # ID from Title
    # Support various hyphens: ASCII(-), U+2010(‐), U+2212(−), U+2013(–), U+2014(—), U+2015(―)
    id_pattern = r'([０-９0-9]+[‐−–—―-][０-９0-9]+)'
    id_match = re.search(id_pattern, full_title)
    
    def normalize_id(id_str):
        # Translate full-width numbers to half-width
        id_str = id_str.translate(str.maketrans('０１２３４５６７８９', '0123456789'))
        # Normalize all hyphens to ASCII hyphen
        for char in ['‐', '−', '–', '—', '―']:
            id_str = id_str.replace(char, '-')
        return id_str

    if id_match:
        topic_id = normalize_id(id_match.group(1))
    else:
        # Fallback: try to find ID in filename
        filename = os.path.basename(file_path)
        id_match_file = re.search(id_pattern, filename)
        if id_match_file:
             topic_id = normalize_id(id_match_file.group(1))
        else:
             topic_id = "unknown"

    # Category from <div class="param">...</div>
    params = re.findall(r'<div class="param">\s*(.*?)</div>', html_content, re.DOTALL | re.IGNORECASE)
    category = "Uncategorized"
    for p_text in params:
        clean_text = re.sub(r'<[^>]+>', '', p_text).strip()
        if '【法人】' in clean_text:
            category = '法人税'
            break
        elif '【消費】' in clean_text:
            category = '消費税'
            break
    
    # Simple category fallback if based on filename or other markers?
    if category == "Uncategorized":
         # Maybe verify if there are other known categories?
         pass

    start_tag_match = re.search(r'<div id="doc"[^>]*>', html_content)
    content_html = ""
    if start_tag_match:
        start_index = start_tag_match.end()
        cnt = 1
        i = start_index
        while cnt > 0 and i < len(html_content):
            if html_content[i:i+4] == '<div':
                cnt += 1
                i += 4
            elif html_content[i:i+6] == '</div>':
                cnt -= 1
                if cnt == 0:
                    break
                i += 6
            else:
                i += 1
        content_html = html_content[start_index:i]

    # Clean up content:
    # 1. Remove style attributes? (Optional, maybe keep for now)
    # 2. Ensure mask tags are preserved (class="span-memory")
    
    # Check for mask usage
    # Based on grep, likely: <span class="span-memory">...</span>
    
    return {
        "id": topic_id,
        "category": category,
        "title": full_title,
        "content": content_html.strip()
    }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python extract_topic.py <html_file_path_or_directory>")
        sys.exit(1)

    input_path = sys.argv[1]
    results = []

    if os.path.isdir(input_path):
        # Process all HTML files in directory recursively
        html_files = glob.glob(os.path.join(input_path, "**", "*.html"), recursive=True)
        for file_path in html_files:
            # Skip saved_resource.html, iframe, or files inside *_files directories (common in "Save as Complete")
            if "saved_resource" in file_path or "iframe" in file_path or "_files" in file_path:
                continue
            
            data = extract_data_from_file_safe(file_path)
            if data and data['content']: # Only add if content was found
                results.append(data)
                print(f"Processed: {os.path.basename(file_path)} -> ID: {data['id']}")
            else:
                print(f"Skipped (no content or error): {os.path.basename(file_path)}")
    else:
        # Single file
        data = extract_data_from_file_safe(input_path)
        if data:
            results.append(data)

    # Sort results by ID (Natural sort for "1-2" vs "1-10")
    def sort_key(item):
        id_str = item.get('id', '')
        # Handle "unknown" or empty
        if not id_str or id_str == 'unknown':
            return (999999, 999999)
        try:
            # Expecting "Num-Num" format
            parts = id_str.split('-')
            if len(parts) >= 2:
                return (int(parts[0]), int(parts[1]))
            else:
                 # Fallback for simple numbers
                return (int(parts[0]), 0)
        except ValueError:
            # If not parseable as int, fallback to string sort but push to end
            return (999999, id_str)

    results.sort(key=sort_key)

    output_file = "topics.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"Extraction complete. {len(results)} topics saved to {output_file}")
