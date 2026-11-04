"""Validate saved real positive cases from the revised pilot."""
import csv
from pathlib import Path
p = Path(__file__).resolve().parent
rows = list(csv.DictReader((p / 'validation_products.csv').open(encoding='utf-8-sig')))
assert rows and all(0 < len(r['product_description']) < 180 for r in rows)
assert any('ROCm' in r['new_product'] and '10' in r['new_product'] for r in rows)
assert any('BioNeMo' in r['new_product'] for r in rows)
print('Saved real-positive pilot checks passed.')
