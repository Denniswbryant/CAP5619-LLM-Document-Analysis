"""Synthetic regression checks; not accuracy measurements on SEC filings."""
import json
from extract import verify

cases = [
    ('Atlas Sensor', 'Example Corp today announced the launch of Atlas Sensor, a wireless temperature sensor, available starting today.', 'CURRENT_PRODUCT_ANNOUNCEMENT'),
    ('Atlas Sensor', 'During the quarter, Example Corp introduced Atlas Sensor. Today the company reported its quarterly financial results.', 'RETROSPECTIVE'),
    ('Atlas Sensor', 'Sales of the existing Atlas Sensor increased 12% this quarter.', 'EXISTING_PRODUCT'),
    ('Zero500NotesDue2031', 'Registered securities: Zero500NotesDue2031, 0.500% Notes due 2031.', 'SECURITY_OR_FINANCING'),
    ('Jane Smith', 'Example Corp today appointed Jane Smith as chief executive officer.', 'OTHER_OR_UNCLEAR'),
]
results = []
for name, text, expected in cases:
    decision = verify({'new_product': name}, text, 'llama3.1:8b')
    passed = decision['category'] == expected
    results.append({'candidate': name, 'expected': expected, **decision, 'passed': passed})
    print(json.dumps(results[-1]), flush=True)
assert all(r['passed'] for r in results), 'Verifier regression failed'
print('All five synthetic verification checks passed.')
