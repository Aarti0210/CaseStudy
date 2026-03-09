"""Script to attempt importing every module in the project to detect broken imports."""
import os, sys, importlib, traceback

base='.'

# add project root to path
sys.path.insert(0, os.path.abspath(base))
errors=[]
for root, dirs, files in os.walk(base):
    # skip venv
    if '.venv' in root or 'venv' in root or 'site-packages' in root:
        continue
    for f in files:
        if f.endswith('.py'):
            rel=os.path.relpath(os.path.join(root,f), base)
            module=rel.replace(os.sep,'.')[:-3]  # drop .py
            if module.startswith('scripts'):
                continue
            try:
                importlib.import_module(module)
            except Exception as e:
                errors.append((module,e))

if errors:
    print('Import errors:')
    for mod,e in errors:
        print(mod,":", e)
    sys.exit(1)
else:
    print('All modules imported successfully.')
    sys.exit(0)
