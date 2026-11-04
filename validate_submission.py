"""Validate the saved submission files without making model or network calls."""
import csv
import hashlib
import json
from datetime import datetime
from pathlib import Path
from extract import FIELDS, normalize

root = Path(__file__).resolve().parent
with (root / 'products.csv').open(encoding='utf-8-sig', newline='') as handle:
    reader = csv.DictReader(handle)
    assert reader.fieldnames == FIELDS, reader.fieldnames
    rows = list(reader)
assert len(rows) >= 100, f'Rubric requires at least 100 entries; found {len(rows)}'
keys = set()
for row in rows:
    assert all(isinstance(value, str) and value.strip() for value in row.values())
    assert 0 < len(row['product_description']) < 180
    stamp = datetime.fromisoformat(row['filing_time'].replace('Z', '+00:00'))
    assert stamp.tzinfo is not None
    key = (row['stock_name'], normalize(row['new_product']))
    assert key not in keys, f'Duplicate product: {key}'
    keys.add(key)
review = json.loads((root / 'manual_review.json').read_text(encoding='utf-8'))
assert rows == review['final_rows']
for proof in review['decisions']:
    decision = proof['review']
    assert hashlib.sha256(proof['evidence'].encode()).hexdigest() == decision['reviewed_evidence_sha256']
summary = json.loads((root / 'summary.json').read_text())
logs = json.loads((root / 'processing_log.json').read_text(encoding='utf-8'))
assert summary['reviewed_product_rows'] == len(rows)
assert summary['filings_attempted'] == len(logs)
meta = json.loads((root / 'run_metadata.json').read_text(encoding='utf-8'))
assert meta['script_sha256'] == hashlib.sha256((root / 'extract.py').read_bytes()).hexdigest()
print(f'PASS: {len(rows)} reviewed rows, five required columns, unique product keys, valid timestamps, descriptions under 180 characters, and matching source-review hashes.')
