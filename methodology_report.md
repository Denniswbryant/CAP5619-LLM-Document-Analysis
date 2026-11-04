# Extracting New Product Announcements from SEC Form 8 K Filings

Dennis Bryant | CAP5619 | Revised November 3, 2026

https://github.com/Denniswbryant/CAP5619-LLM-Document-Analysis

## Purpose and dataset

This project uses a local large language model to extract named new products from SEC Form 8-K filings. The revised analysis processed 220 filings from 20 companies and produced 102 reviewed product records from 8 companies. The five CSV columns are company_name, stock_name, filing_time, new_product and product_description. Each description contains fewer than 180 characters; the longest is 114 characters.

The sample is a purposive selection of technology companies, not a random S&P 500 sample. Up to 15 recent 8-Ks per company were selected in round-robin order from SEC submissions JSON. The processed filings span 2025-04-24 to 2026-11-03. The exact selection and processed manifests are retained. Processing can continue beyond 100 documents to satisfy the rubric's separate requirement of at least 100 product entries. The candidate stopping target is 170 unique product names after at least 100 filings, followed by source review; additional filings are required if review leaves fewer than 100 supported records.

## Preprocessing and named entity recognition

Python downloads the primary filing and HTML/text EX-99 exhibits using an identifying SEC User-Agent, throttling and retries. Downloads are cached, and visible paragraph boundaries are preserved while scripts, styles and hidden inline-XBRL metadata are suppressed. Long paragraphs are split into passages of about 2,200 characters with a 150-character overlap. A keyword screen selects introduction, launch, release, availability and new-product context plus neighboring passages, forming batches of at most 16,000 characters.

The LLM performs prompted named entity recognition with ORGANIZATION, PRODUCT and PERSON labels, then returns product names, factual descriptions, categories and source passage IDs in JSON. Company name, ticker and acceptance timestamp come from SEC metadata rather than model inference. Named product families, models and versions can form separate records when the source explicitly introduces them; ordinary existing-product mentions, financing, acquisitions, facilities and partnership-only statements do not qualify.

## Model and evidence checks

The final pipeline uses Ollama qwen3:14b locally: Qwen3 with 14.8 billion parameters and Q4_K_M quantization. Thinking is disabled; temperature is 0, the initial seed is 42, context is 12,288 tokens, and the output cap is 5,000 tokens. Responses use a JSON schema. A separate prompt checks candidate names, descriptions and release evidence using the same model. Unlike the first version, launches summarized in quarterly results qualify, as do named unveilings with future availability; vague development plans do not.

Python copies evidence directly from cited passage IDs and checks normalized names against those passages. This avoids relying on model-generated verbatim quotations. Invalid candidates are logged individually instead of discarding every product in a filing. Overlong descriptions are shortened at a word boundary and logged. Filing checkpoints and inference caches support resuming an interrupted run.

## Results and source review

The model generated 170 unique accepted candidates before source review. Review retained 102 records in products.csv. Raw results, copied evidence, source URLs, passage IDs and every review decision are provided separately. Global ticker/product normalization removes repeated names across filings; source review also addresses aliases and incomplete version names. The retained timestamp is the earliest observed filing in the analyzed sample, not necessarily the first public announcement date.

220 filings completed without document-processing errors; 0 filings had errors or partial processing. Failures and candidate rejections remain visible in the logs. A completed filing with no qualifying product adds no placeholder row. The final CSV meets the rubric's 100-entry threshold through distinct supported products, not duplicate or empty rows.

The original three-row output was inadequate for the rubric. Its restrictive definition rejected reporting-period launches, while quotation mismatches caused 13 filing failures. All 13 now complete successfully. The revision broadens the definition, copies source passages by ID and isolates candidate validation problems. LLaMA 3.1 8B sometimes shortened new model names to existing families. Qwen3 14B was selected after pilot comparisons showed more specific release names.

## Validation and challenges

Two deterministic checks verify hidden-metadata removal and trademark-insensitive grounding. Five synthetic scenarios test a reporting-quarter launch, a named future-availability unveiling, an existing-product sales mention, financing/appointments and a partnership-only statement. The revised model passed these scenarios. A real positive pilot used AMD, ServiceNow and NVIDIA filings, and final accepted candidates received Codex-assisted source review. These development checks are not an independent labeled benchmark; precision and recall are not claimed.

The main challenges were distinguishing a launch from ordinary product use, retaining complete version names, handling typography and extracting concise descriptions. Source review rejects unsupported entries and records any name or description correction. The raw LLM output remains unchanged for comparison. A source quotation establishes what a filing says; it does not independently verify corporate marketing claims or future delivery.

## Limitations and reproducibility

The same model performs extraction and verification, so mistakes can be correlated. Keyword screening, passage boundaries and incomplete NER can miss announcements. Exact normalized-name deduplication cannot resolve every alias automatically. PDF/image exhibits are unsupported. Technology-company selection and stopping after enough candidate records can bias the dataset. AI assistance and support were used for implementation, debugging, source review and report preparation.

The repository contains the code, tests, raw and reviewed CSVs, evidence, manifests, run metadata and review decisions. The model digest, script hash and settings are recorded. Replaying the processed manifest fixes document selection, but output may vary across model builds or hardware. The GitHub URL appears above and on the revised resume; the repository is private, so instructor access is required.

## Sources

SEC EDGAR APIs: https://www.sec.gov/search-filings/edgar-application-programming-interfaces

Ollama structured outputs: https://docs.ollama.com/capabilities/structured-outputs

Qwen3 model: https://ollama.com/library/qwen3:14b
