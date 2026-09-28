import os

path = os.path.join('backend', 'stitch_extracted', 'screen1_analysis', 'code.html')
with open(path, 'r', encoding='utf-8') as f:
    html = f.read()

def show_around(title, kw, length=1200):
    pos = html.find(kw)
    if pos >= 0:
        start = max(0, pos - 150)
        print(f"\n=================== {title} ===================")
        print(html[start:start+length])

show_around("Summary Block", "Extractive Contract Summary")
show_around("Missing Clauses Block", "Omission & Missing Clause Audit")
