"""Apply the documented review artifact without changing the raw LLM results."""
import argparse
import csv
import json
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('--review', type=Path, default=Path(__file__).resolve().parent / 'manual_review.json')
parser.add_argument('--output', type=Path, default=Path(__file__).resolve().parent / 'products.csv')
args = parser.parse_args()
rows = json.loads(args.review.read_text(encoding='utf-8'))['final_rows']
fields = ['company_name', 'stock_name', 'filing_time', 'new_product', 'product_description']
for row in rows:
    assert set(row) == set(fields) and 0 < len(row['product_description']) < 180
with args.output.open('w', encoding='utf-8-sig', newline='') as handle:
    writer = csv.DictWriter(handle, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)
print(f'Wrote {len(rows)} reviewed product rows. See manual_review.json for decisions and limitations.')
