import os

path = os.path.join('backend', 'stitch_extracted', 'screen1_analysis', 'code.html')
with open(path, 'r', encoding='utf-8') as f:
    html = f.read()

pos = html.find('Clauses Preview & Stratification')
grid_pos = html.rfind('<div class="grid', 0, pos)
print(html[grid_pos:pos+400])
