# CAP5619 LLM Document Analysis

SEC Form 8-K new product extraction using Python and local Ollama `llama3.1:8b`.

**Study result:** 100 filings attempted, 87 completed and 13 failed validation. Six raw candidates were reduced to **three reviewed rows**. This is a convenience sample, not an accuracy benchmark. The source review removed a past IBM launch, a planned foundry and a Slack usage metric. The review also rewrote retained descriptions for clarity without adding features.

## Deliverables

| File | Purpose |
| --- | --- |
| `extract.py` | Downloads SEC documents, runs LLM NER/extraction and verifies candidates |
| `products.csv` | Reviewed five-column assignment output |
| `products_pipe.txt` | Same reviewed output separated by pipes |
| `methodology_report.pdf` | Two-page report with this repository URL |
| `methodology_report.md` | Editable report text |
| `raw_products.csv` | Original accepted model candidates before source review |
| `audit.json` | Original entity labels, candidates, quotations, decisions and source URLs |
| `processing_log.json` | Completed filings and errors; errors are not negatives |
| `study_manifest.json` | Exact 100 filings used |
| `run_metadata.json` | Timing, script hash, model digest and run settings |
| `manual_review.json` | Review decisions, final rows and ten negative-source checks |
| `validation_*` | Real positive test manifest and saved results |

## Local setup

Use Python 3.10 or later and Ollama. The extraction requires only Python's standard library. No Python packages, SEC API key or paid LLM API are required.

```powershell
ollama pull llama3.1:8b
python extract.py --smoke-test
python check_verifier.py
```

Ollama must be running at `http://localhost:11434`. Run this locally: an ordinary hosted Google Colab runtime cannot reach your PC's localhost.

## Reproduce the study

Replace the sample contact header with your actual name and email. It is sent to the SEC with requests; do not hardcode private credentials.

```powershell
python extract.py --manifest study_manifest.json --limit 100 --contact "Your Name your-email@example.com" --output-dir rerun
```

This writes `rerun/products.csv`, `rerun/audit.json`, `rerun/processing_log.json`, `rerun/manifest.json` and `rerun/run_metadata.json`. The submitted root-level `products.csv` is the reviewed output. Model output can vary by run/hardware, even with temperature zero. Do not apply old review decisions to a different run without checking the sources again.

To recreate the submitted reviewed CSV from the saved decisions:

```powershell
python review_results.py --output reviewed_copy.csv
```

To rerun the known positive filing, then check the result:

```powershell
python extract.py --manifest validation_manifest.json --limit 1 --contact "Your Name your-email@example.com" --output-dir validation
python validate_positive.py
```

`validate_positive.py` can also check the saved root-level `validation_products.csv` and `validation_processing_log.json` before a rerun.

## Data and methodology

The 100-document manifest contains 99 recent 8-Ks from ten selected technology companies (ten each for AAPL, MSFT, NVDA, AMD, INTC, IBM, ORCL, CRM and ADBE; nine for CSCO), plus one deliberately selected Mitesco positive case. It is not a random S&P 500 sample. Company metadata comes from SEC ticker/submissions JSON, with the positive case's acceptance time checked against its filing index and converted from Eastern time to UTC.

The parser extracts primary filing and HTML/text EX-99 exhibit content, suppresses hidden inline-XBRL sections, and splits text into 8,000-character chunks with 1,000-character overlap. Chunks are screened using launch/introduction/new-product wording. LLaMA performs prompted NER with ORGANIZATION and PRODUCT labels, then returns candidates in structured JSON. A second prompt classifies each candidate. Conservative context rules reject debt identifiers, unsupported sales quotations and retrospective launch summaries. Services count as operating products; financing instruments do not. Explicit new-product headings in a current release can qualify.

Names and quotations must occur in the source. Descriptions must contain fewer than 180 characters. Overlong descriptions are shortened at a word boundary with an ellipsis and the change is logged. Reviewers can rewrite descriptions, with decisions recorded in `manual_review.json`. Duplicate product names are removed within each filing, not across filings. Source downloads are cached locally and throttled; transient SEC errors are retried. Filings that fail validation are excluded from the output and remain visible in the error log.

## Validation and limitations

Five synthetic verification checks passed and the real positive Mitesco case produced a supported product row. All six final model candidates were source-reviewed; three were retained. Ten completed zero-row filings were sampled with seed 42 for focused source review of filing item text and launch context. This is Codex-assisted source review, not an independent human-labeled test set. No precision or recall estimate is claimed. Thirteen filings failed processing and are excluded, which can bias results.

The same model runs both extraction and verification, so errors can be correlated. NER occasionally mislabels people/locations. Screening, chunking, conservative rules and exact-string checks can miss or reject valid announcements. PDF/image exhibits and other exhibit classes are unsupported. Retrospective earnings summaries are deliberately excluded. The targeted positive is disclosed separately because including it changes the sample composition.

Assistant support was used for implementation, debugging, source review and report preparation. The student should understand and review the code and findings before submission.

## GitHub and résumé

Repository: https://github.com/Denniswbryant/CAP5619-LLM-Document-Analysis

This repository is private. Give the instructor access before sharing the URL. The project URL has also been added to a separate résumé copy delivered locally. The résumé is intentionally excluded from this repository; confirm with the instructor if a fuller academic CV is required.

Sources: [SEC EDGAR APIs](https://www.sec.gov/search-filings/edgar-application-programming-interfaces), [Ollama chat API](https://docs.ollama.com/api/chat), [Mitesco positive exhibit](https://www.sec.gov/Archives/edgar/data/802257/000118518525001092/mitiex99-1.htm).
