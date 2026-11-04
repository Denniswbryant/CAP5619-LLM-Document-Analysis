"""Apply documented source-review decisions to the immutable raw LLM results.

Run after reviewing evidence.json. Decisions reference ticker + normalized raw name.
Every acceptance, correction and rejection is saved; no placeholder rows are added.
"""
import csv
import hashlib
import argparse
import json
from pathlib import Path
from extract import FIELDS, ROOT, normalize, save_json


def apply_review(evidence_path, decisions_path, output_dir):
    evidence = json.loads(evidence_path.read_text(encoding='utf-8'))
    decisions = json.loads(decisions_path.read_text(encoding='utf-8'))
    rows, records, seen = [], [], set()
    missing = []
    for proof in evidence:
        raw = proof['record']
        key = raw['stock_name'] + ':' + normalize(raw['new_product'])
        if key not in decisions:
            missing.append(key)
            continue
        decision = decisions[key]
        if decision.get('reviewed_evidence_sha256') != hashlib.sha256(proof['evidence'].encode()).hexdigest():
            raise ValueError(f'Source evidence changed since review: {key}')
        if decision['accept']:
            row = {**raw, **decision.get('corrections', {})}
            dedup_key = (row['stock_name'], normalize(row['new_product']))
            if dedup_key in seen:
                records.append({**proof, 'review': {**decision, 'accept': False, 'reason': 'Duplicate after name correction'}})
                continue
            assert set(row) == set(FIELDS)
            assert all(isinstance(v, str) and v.strip() for v in row.values())
            assert 0 < len(row['product_description']) < 180
            assert normalize(row['new_product']) in normalize(proof['evidence']), row
            seen.add(dedup_key)
            rows.append(row)
        records.append({**proof, 'review': decision})
    if missing:
        raise ValueError(f'{len(missing)} products still need source review: {missing[:10]}')
    if len(rows) < 100:
        raise ValueError(f'Only {len(rows)} supported rows remain; expand extraction before submission')
    output_dir.mkdir(parents=True, exist_ok=True)
    with (output_dir / 'products.csv').open('w', newline='', encoding='utf-8-sig') as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    with (output_dir / 'products_pipe.txt').open('w', encoding='utf-8') as handle:
        handle.write(' | '.join(FIELDS) + '\n')
        for row in rows:
            handle.write(' | '.join(row[k].replace('|', '/') for k in FIELDS) + '\n')
    save_json(output_dir / 'manual_review.json', {
        'reviewer': 'Codex-assisted source review, not an independent human-labeled benchmark',
        'definition': 'New named operating products, named versions and new availability, including reporting-period launches summarized in 8-K exhibits',
        'decisions': records, 'final_rows': rows})
    print(f'Saved {len(rows)} reviewed product rows.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence', type=Path, default=ROOT / 'evidence.json')
    parser.add_argument('--decisions', type=Path, default=ROOT / 'review_decisions.json')
    parser.add_argument('--output-dir', type=Path, default=ROOT / 'reviewed_rebuild')
    args = parser.parse_args()
    apply_review(args.evidence, args.decisions, args.output_dir)
