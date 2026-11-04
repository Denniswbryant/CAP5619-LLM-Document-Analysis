# CAP5619 LLM Document Analysis

Analyze SEC Form 8-K filings with a local LLM to extract new product introductions and structure them into a CSV.

The run analyzed 220 filings from 20 companies. 0 filings had document-processing errors or partial processing. All descriptions contain fewer than 180 characters. The earlier three-row submission has been superseded.

## Required deliverables

| File | Purpose |
| --- | --- |
| `extract.py` | Python implementation using Ollama for NER, extraction and verification |
| `products.csv` | Final reviewed CSV with at least 100 genuine product records |
| `methodology_report.docx` | Editable Word methodology report |

The five final CSV columns are:

```text
company_name,stock_name,filing_time,new_product,product_description
```

There are no empty “no product” rows. Repeated ticker/product names are deduplicated across filings, and source review removes additional aliases. Filings with no qualifying introduction add no product rows.

## Setup

The extraction script needs Python 3.10 or later, Ollama and the model below. It uses only Python's standard library and has no paid API dependency.

```powershell
ollama pull qwen3:14b
python test_extraction.py
```

The final model is **Qwen3 14B** (`qwen3:14b`), 14.8 billion parameters, Q4_K_M quantization, approximately a 9.3 GB download. It runs locally at `http://localhost:11434`. The saved run used temperature 0, initial seed 42, a 12,288-token context and a 5,000-token output cap, with thinking disabled. An NVIDIA GPU is helpful; CPU inference can be slower. Run locally rather than expecting a hosted Colab runtime to reach this PC's localhost.

The model digest, Ollama version, settings, source-code hash and actual run counts are in `run_metadata.json`. LLaMA 3.1 8B was used during development; the final revised study uses Qwen3.

## Reproduce the analyzed documents

Replace the example contact with your actual name and email for the SEC identification header. It is not an SEC login or an LLM API key.

```powershell
python extract.py --manifest study_manifest.json --limit 220 --target-products 0 --min-filings 0 --contact "Your Name your-email@example.com" --output-dir rerun
```

`study_manifest.json` fixes the actual analyzed documents. `selected_manifest.json` preserves the larger initial selection. The initial selection contains up to 15 recent 8-Ks from each of 20 chosen technology companies in round-robin order; this is a purposive sample, not a random S&P 500 sample. The development stopping target was 170 raw unique candidates after at least 100 filings, with further extraction if review left fewer than 100 supported entries.

Rerun outputs include `products.csv`, `evidence.json`, `processing_log.json`, `processed_manifest.json`, `run_metadata.json` and per-filing checkpoints. Downloads and inference responses are cached in `cache/`. Keep a run's checkpoints together with its script and model version. Use a fresh output/cache directory when changing prompts or models; do not treat cached outputs from another model as a fresh inference run.

Model output can vary across hardware/model builds. The submitted root `products.csv` is the source-reviewed output, while `raw_products.csv` preserves the final model's unreviewed accepted candidates. Review new model outputs again before submitting them.

## Methodology

1. Load company/ticker/CIK information and filing acceptance timestamps from official SEC JSON APIs.
2. Download the primary filing and linked HTML/text EX-99 exhibits, including press releases. Throttle identified SEC requests and retry transient failures.
3. Remove scripts, styles and hidden inline-XBRL metadata. Preserve visible source passages with IDs. Split long paragraphs at about 2,200 characters with a 150-character overlap.
4. Screen introduction, launch, release, availability and “new” context, retaining neighboring passages and batching at most 16,000 text characters.
5. Use the LLM for NER with ORGANIZATION, PRODUCT and PERSON labels, and structured JSON extraction of names, descriptions, categories and source IDs.
6. Copy the cited source text in Python, validate normalized product names and run a separate LLM verification prompt. One bad candidate does not discard every product in a filing.
7. Deduplicate ticker/product names globally, retain the earliest observed filing in the sample, and source-review accepted records. The timestamp is the filing acceptance time, not the product's launch date.

**Qualifying scope:** named new products, distinct named versions, operating services and new availability. Launches summarized for a reporting quarter count, even when introduced earlier in that quarter. Specifically unveiled new products with future availability can qualify; vague development plans do not. Ordinary sales/adoption statistics, acquisitions, factories, financing, partnership-only mentions and unversioned feature-only changes are excluded. Named families and individual models are reviewed to avoid double-counting an umbrella alongside its components.

Descriptions must be under 180 characters. The script logs any word-boundary shortening. Source review can correct names/descriptions or reject entries, with every change recorded. No placeholder rows are added to meet the threshold.

## Audit and review

| File | Purpose |
| --- | --- |
| `raw_products.csv` | 170 unreviewed unique model candidates |
| `evidence.json` | Python-copied source passages, source IDs, filing URLs and model decisions |
| `audit.json` | Full per-filing extraction and verification records, including rejected candidates |
| `processing_log.json` | Actual filing statuses, accepted-candidate counts and errors |
| `review_decisions.json` | Acceptance/rejection reasons, corrections and reviewed-evidence hashes |
| `manual_review.json` | Source review trail and final records |
| `summary.json` | Final counts and formatting checks |
| `test_results.json` | Saved synthetic classification results |

To rebuild the submitted CSV from the saved source-review decisions:

```powershell
python review_results.py --evidence evidence.json --decisions review_decisions.json --output-dir reviewed_rebuild
```

The review script requires at least 100 supported rows and checks the evidence hashes. It fails if source passages changed or records remain unreviewed. Old decisions should not be applied blindly to a different extraction run.

## Validation

```powershell
python test_extraction.py
python validate_positive.py
python validate_submission.py
```

Two deterministic tests check hidden-metadata removal and trademark-insensitive grounding. Five synthetic scenarios test reporting-period launches, named future unveilings, ordinary sales mentions, financing/appointments and partnership-only announcements. Real positive pilot results are saved under the `validation_*` filenames. `check_verifier.py` remains as a compatibility entry point for the updated model scenarios.

The final file validator checks the five columns, at least 100 rows, unique ticker/product keys, valid timestamps, descriptions under 180 characters, matching review hashes, final counts and script hash. These tests and Codex-assisted source review are not an independently labeled accuracy benchmark; no precision or recall estimate is claimed.

## Challenges and limitations

The first version rejected reporting-period launches and discarded entire filings after exact quotation mismatches. It returned only three rows, which did not meet the rubric. This revision accepts reporting-period introductions, uses passage IDs for evidence and isolates candidate failures. More filings are processed as necessary to produce at least 100 supported rows after review.

The same model extracts and verifies, so its errors can be correlated. Keyword screening, passage boundaries and NER can miss products. Automatic name normalization does not resolve every alias; review remains necessary. PDF/image exhibits are unsupported. Company selection and the candidate-based stopping rule can bias results. Source quotations establish what a company reported, not independent verification of its marketing claims or future delivery.

AI assistance and support were used for implementation, debugging, source review and report preparation.

## GitHub

https://github.com/Denniswbryant/CAP5619-LLM-Document-Analysis

Sources: [SEC EDGAR APIs](https://www.sec.gov/search-filings/edgar-application-programming-interfaces), [Ollama structured outputs](https://docs.ollama.com/capabilities/structured-outputs), [Qwen3 14B](https://ollama.com/library/qwen3:14b).
