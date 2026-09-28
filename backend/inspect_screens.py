import os
import re

screens = ['screen0_dashboard', 'screen1_analysis', 'screen2_documents', 'screen3_search', 'screen4_assistant']
for s in screens:
    path = os.path.join('backend', 'stitch_extracted', s, 'code.html')
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()
    imgs = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', html)
    print(f'{s} images ({len(imgs)}):', imgs)
