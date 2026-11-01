"""Check the real SEC positive fixture after running validation_manifest.json."""
import csv
import json
from extract import ROOT

csv_path = ROOT / 'validation' / 'products.csv'
log_path = ROOT / 'validation' / 'processing_log.json'
if not csv_path.exists():
    csv_path, log_path = ROOT / 'validation_products.csv', ROOT / 'validation_processing_log.json'
rows = list(csv.DictReader(csv_path.open(encoding='utf-8-sig')))
logs = json.loads(log_path.read_text())
assert len(logs) == 1 and logs[0]['status'] == 'processed', logs
assert len(rows) == 1, rows
assert 'Crypto Processing Services' in rows[0]['new_product'], rows
assert rows[0]['stock_name'] == 'MITI' and len(rows[0]['product_description']) < 180
print('Real SEC positive fixture passed: one supported product row.')
