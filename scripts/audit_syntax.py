"""Utility script to scan project files for Python syntax errors."""
import os, ast, sys

base='.'
errors=[]
for root, dirs, files in os.walk(base):
    # skip virtual environments
    if '.venv' in root or 'venv' in root or 'site-packages' in root:
        continue
    for f in files:
        if f.endswith('.py'):
            path=os.path.join(root,f)
            with open(path,'r', encoding='utf-8') as fh:
                try:
                    ast.parse(fh.read())
                except SyntaxError as e:
                    errors.append((path,e))
if errors:
    print('Syntax errors:')
    for path,e in errors:
        print(path, e)
    sys.exit(1)
else:
    print('No syntax errors detected.')
    sys.exit(0)
