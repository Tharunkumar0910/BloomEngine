import re

# Verify app.py
content = open('app.py', encoding='utf-8').read()
lines = content.splitlines()
print('app.py line count:', len(lines))

checks = [
    ('import string', 'import string'),
    ('SequenceMatcher', 'SequenceMatcher'),
    ('CONCEPT_SYNONYMS', 'CONCEPT_SYNONYMS import'),
    ('BLOOM_PROFILES', 'BLOOM_PROFILES import'),
    ('[PROMPT SELECTION]', 'debug PROMPT SELECTION print'),
]
print()
print('=== app.py verification (CLEAN = removed successfully) ===')
for needle, label in checks:
    hits = [i+1 for i,l in enumerate(lines) if needle in l]
    status = 'CLEAN' if not hits else ('STILL PRESENT at L' + str(hits))
    print('  ' + label + ': ' + status)

# Check export_rejections no longer has inner imports
in_fn = False
for i, l in enumerate(lines):
    if 'def export_rejections' in l:
        in_fn = True
    if in_fn and ('import csv' in l or 'import json' in l):
        print('  inner imports in export_rejections: STILL PRESENT at L' + str(i+1))
        break
    if in_fn and 'if REJECTION_LOGS' in l:
        print('  inner imports in export_rejections: CLEAN')
        break

# Verify main.js
content2 = open('static/js/main.js', encoding='utf-8').read()
lines2 = content2.splitlines()
print()
print('main.js line count:', len(lines2))
checks2 = [
    ('Script loaded', 'console.log Script loaded'),
    ('DOMContentLoaded fired', 'console.log DOMContentLoaded'),
    ('switchTab executed', 'console.log switchTab'),
    ('fetchBatchHistory started', 'console.log fetchBatchHistory'),
    ('renderDashboardConfidenceChart', 'dead confidence chart fn'),
    ('window.viewManualDetails', 'dead viewManualDetails fn'),
]
print()
print('=== main.js verification (CLEAN = removed successfully) ===')
for needle, label in checks2:
    hits = [i+1 for i,l in enumerate(lines2) if needle in l]
    status = 'CLEAN' if not hits else ('STILL PRESENT at L' + str(hits))
    print('  ' + label + ': ' + status)
