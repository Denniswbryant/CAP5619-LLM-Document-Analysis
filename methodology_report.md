# Extracting New Product Announcements from SEC Form 8 K Filings

Dennis Bryant | CAP5619 | November 1, 2026

https://github.com/Denniswbryant/CAP5619-LLM-Document-Analysis

## Purpose and document selection

This project uses a locally hosted large language model to identify new product announcements in SEC Form 8-K filings and produce a five-column CSV. The run attempted 100 filings; 87 completed without a processing error, and 13 were recorded as errors. The reviewed output contains 3 product rows. These are descriptive results for a convenience sample, not an estimate of announcement frequency across public companies.

The sample includes 99 recent filings retrieved from the SEC submissions data for AAPL, MSFT, NVDA, AMD, INTC, IBM, ORCL, CRM, ADBE and CSCO: ten per company except nine for CSCO. One purposefully selected Mitesco filing is included as a known positive test. Filing dates range from 2025-06-12 to 2026-10-29. The explicit manifest fixes the analyzed documents, rather than relying on a changing search result. The Mitesco case must not be interpreted as a randomly discovered positive.

## Preprocessing and named entity recognition

Python downloads the primary 8-K document and linked HTML or text EX-99 exhibits, including press releases. SEC requests carry a user-supplied identifying name and email, are throttled, and are cached. An HTML parser removes scripts, styles and hidden inline-XBRL sections. Text is divided into 8,000-character chunks with a 1,000-character overlap. A keyword screen selects chunks mentioning launches, introductions, new products or services, debuts or general availability. Screened-out chunks remain in the processing audit.

LLaMA performs prompted named entity recognition by returning ORGANIZATION and PRODUCT labels along with candidate product names, descriptions and source quotations. This is LLM-based NER, not a separately trained spaCy or transformer NER model. Company name, ticker and acceptance timestamp come from SEC metadata and are not guessed by the model. Multiple products create separate rows; a completed filing with no accepted announcement creates no product row.

## Extraction and verification

Python queries Ollama over its local HTTP API using llama3.1:8b, a quantized 8-billion-parameter model. JSON schemas constrain response types; temperature is zero and the initial seed is 42. A second prompt classifies each candidate as a current announcement, retrospective launch, existing product, financing or unclear content. Conservative rules reject debt identifiers, unsupported sales mentions and retrospective wording without an explicit current launch. Accepted names and quotations must occur in source text. Descriptions are limited to 179 characters; word-boundary shortening is logged when necessary.

## Results and validation

The unreviewed run produced 6 accepted candidate rows. Source review retained 3 rows in products.csv; the original raw_products.csv and audit.json preserve the model output. Error filings are recorded separately and are never counted as negative examples. Each reviewed output row retains the filing company, ticker, timestamp, product name and a concise description. A pipe-separated version is provided in products_pipe.txt.

The real positive test is Mitesco accession 0001185185-25-001092, filed August 28, 2025. Its EX-99.1 press release announces Centcore Crypto Processing Services, a service for cryptocurrency processing, mining and blockchain hosting. The model extracted the named service and passed the evidence and length checks. The filing acceptance time, rather than the press-release date, is used in the CSV. This project treats newly launched operating services as products, while excluding financing instruments.

Five synthetic verification checks passed: a current launch was accepted, while a retrospective launch, existing-product sales, a bond identifier and a management appointment were rejected. A source check was also conducted for all accepted rows and 10 sampled negative filings, with decisions recorded in manual_review.json. Source review was assisted by Codex. The synthetic checks and one deliberately selected positive case are development validation, not an independent accuracy benchmark; precision and recall are not claimed.

## Limitations and reproducibility

The initial pilot confused bonds and sales mentions with product announcements. Additional rules reduced these errors, but the same model performs both extraction and classification, so their mistakes can be correlated. Entity labeling still occasionally mistakes people or locations for organizations. Keyword screening, chunk boundaries and conservative historical-context rules can miss real announcements. Retrospective earnings summaries are deliberately excluded. PDF and image exhibits are unsupported; duplicates are removed within a filing, not across separate filings.

The repository includes the Python implementation, exact filing manifest, raw and reviewed CSVs, source audit, error log, run metadata, positive test and review decisions. Run metadata records the model digest, script hash and generation settings. Replaying the manifest reproduces document selection, although model output can vary between runs or hardware. No paid model API is used. Assistant support was used for coding, debugging, source review and report preparation; the student should review the implementation and conclusions before submission.

## Sources and project access

SEC EDGAR API documentation: https://www.sec.gov/search-filings/edgar-application-programming-interfaces
Ollama chat API: https://docs.ollama.com/api/chat
Positive exhibit: https://www.sec.gov/Archives/edgar/data/802257/000118518525001092/mitiex99-1.htm

The repository URL appears on page one and near the top of a separate revised resume copy. The repository is private, so the instructor must be granted access. The student should confirm whether the instructor requires a fuller academic CV rather than a resume.
