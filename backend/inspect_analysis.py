import os
import re

path = os.path.join('backend', 'stitch_extracted', 'screen1_analysis', 'code.html')
with open(path, 'r', encoding='utf-8') as f:
    html = f.read()

# Find headings in screen1
headings = re.findall(r'<h[1-4][^>]*>(.*?)</h[1-4]>', html)
for h in headings:
    print('Heading:', re.sub(r'<[^>]+>', '', h).strip())

# Check for specific blocks
keywords = [
    'Extractive Contract Summary',
    'Omission & Missing Clause Audit',
    'Clauses Preview',
    'Fuzzy Logic Risk Assessment',
    'Export PDF Report'
]

for kw in keywords:
    pos = html.find(kw)
    print(f"Keyword '{kw}': found at pos {pos}")
