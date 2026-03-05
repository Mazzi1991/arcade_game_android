import os
import re

with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

if 'BASE_DIR = os.path.dirname(os.path.abspath(__file__))' not in content:
    content = content.replace('import traceback', 'import traceback\nBASE_DIR = os.path.dirname(os.path.abspath(__file__))')

def replace_exists(m):
    return f'os.path.exists(os.path.join(BASE_DIR, "{m.group(1)}"))'

def replace_load(m):
    return f'pygame.image.load(os.path.join(BASE_DIR, "{m.group(1)}"))'

content = re.sub(r'os\.path\.exists\("([^"]+)"\)', replace_exists, content)
content = re.sub(r'pygame\.image\.load\("([^"]+)"\)', replace_load, content)

with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Done")
