"""Create the two-page Word/PDF report from the final reviewed summary."""
import json
from pathlib import Path
from xml.sax.saxutils import escape
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.opc.constants import RELATIONSHIP_TYPE as RT
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, PageBreak

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'submission' if (ROOT / 'submission' / 'summary.json').exists() else ROOT
s = json.loads((OUT / 'summary.json').read_text())
manifest = json.loads((OUT / 'study_manifest.json').read_text(encoding='utf-8'))
dates = sorted(f['filing_time'][:10] for f in manifest)
repo = 'https://github.com/Denniswbryant/CAP5619-LLM-Document-Analysis'
body = [
('title', 'Extracting New Product Announcements from SEC Form 8 K Filings'),
('meta', 'Dennis Bryant | CAP5619 | Revised November 3, 2026'),
('link', repo),
('h', 'Purpose and dataset'),
('p', f'This project uses a local large language model to extract named new products from SEC Form 8-K filings. The revised analysis processed {s["filings_attempted"]} filings from {s["companies_analyzed"]} companies and produced {s["reviewed_product_rows"]} reviewed product records from {s["companies_in_output"]} companies. The five CSV columns are company_name, stock_name, filing_time, new_product and product_description. Each description contains fewer than 180 characters; the longest is {s["maximum_description_characters"]} characters.'),
('p', f'The sample is a purposive selection of technology companies, not a random S&P 500 sample. Up to 15 recent 8-Ks per company were selected in round-robin order from SEC submissions JSON. The processed filings span {dates[0]} to {dates[-1]}. The exact selection and processed manifests are retained. Processing can continue beyond 100 documents to satisfy the rubric\'s separate requirement of at least 100 product entries. The candidate stopping target is 170 unique product names after at least 100 filings, followed by source review; additional filings are required if review leaves fewer than 100 supported records.'),
('h', 'Preprocessing and named entity recognition'),
('p', 'Python downloads the primary filing and HTML/text EX-99 exhibits using an identifying SEC User-Agent, throttling and retries. Downloads are cached, and visible paragraph boundaries are preserved while scripts, styles and hidden inline-XBRL metadata are suppressed. Long paragraphs are split into passages of about 2,200 characters with a 150-character overlap. A keyword screen selects introduction, launch, release, availability and new-product context plus neighboring passages, forming batches of at most 16,000 characters.'),
('p', 'The LLM performs prompted named entity recognition with ORGANIZATION, PRODUCT and PERSON labels, then returns product names, factual descriptions, categories and source passage IDs in JSON. Company name, ticker and acceptance timestamp come from SEC metadata rather than model inference. Named product families, models and versions can form separate records when the source explicitly introduces them; ordinary existing-product mentions, financing, acquisitions, facilities and partnership-only statements do not qualify.'),
('h', 'Model and evidence checks'),
('p', 'The final pipeline uses Ollama qwen3:14b locally: Qwen3 with 14.8 billion parameters and Q4_K_M quantization. Thinking is disabled; temperature is 0, the initial seed is 42, context is 12,288 tokens, and the output cap is 5,000 tokens. Responses use a JSON schema. A separate prompt checks candidate names, descriptions and release evidence using the same model. Unlike the first version, launches summarized in quarterly results qualify, as do named unveilings with future availability; vague development plans do not.'),
('p', 'Python copies evidence directly from cited passage IDs and checks normalized names against those passages. This avoids relying on model-generated verbatim quotations. Invalid candidates are logged individually instead of discarding every product in a filing. Overlong descriptions are shortened at a word boundary and logged. Filing checkpoints and inference caches support resuming an interrupted run.'),
('page', ''),
('h', 'Results and source review'),
('p', f'The model generated {s["raw_unique_product_rows"]} unique accepted candidates before source review. Review retained {s["reviewed_product_rows"]} records in products.csv. Raw results, copied evidence, source URLs, passage IDs and every review decision are provided separately. Global ticker/product normalization removes repeated names across filings; source review also addresses aliases and incomplete version names. The retained timestamp is the earliest observed filing in the analyzed sample, not necessarily the first public announcement date.'),
('p', f'{s["filings_completed"]} filings completed without document-processing errors; {s["filings_with_errors"]} filings had errors or partial processing. Failures and candidate rejections remain visible in the logs. A completed filing with no qualifying product adds no placeholder row. The final CSV meets the rubric\'s 100-entry threshold through distinct supported products, not duplicate or empty rows.'),
('p', 'The original three-row output was inadequate for the rubric. Its restrictive definition rejected reporting-period launches, while quotation mismatches caused 13 filing failures. All 13 now complete successfully. The revision broadens the definition, copies source passages by ID and isolates candidate validation problems. LLaMA 3.1 8B sometimes shortened new model names to existing families. Qwen3 14B was selected after pilot comparisons showed more specific release names.'),
('h', 'Validation and challenges'),
('p', 'Two deterministic checks verify hidden-metadata removal and trademark-insensitive grounding. Five synthetic scenarios test a reporting-quarter launch, a named future-availability unveiling, an existing-product sales mention, financing/appointments and a partnership-only statement. The revised model passed these scenarios. A real positive pilot used AMD, ServiceNow and NVIDIA filings, and final accepted candidates received Codex-assisted source review. These development checks are not an independent labeled benchmark; precision and recall are not claimed.'),
('p', 'The main challenges were distinguishing a launch from ordinary product use, retaining complete version names, handling typography and extracting concise descriptions. Source review rejects unsupported entries and records any name or description correction. The raw LLM output remains unchanged for comparison. A source quotation establishes what a filing says; it does not independently verify corporate marketing claims or future delivery.'),
('h', 'Limitations and reproducibility'),
('p', 'The same model performs extraction and verification, so mistakes can be correlated. Keyword screening, passage boundaries and incomplete NER can miss announcements. Exact normalized-name deduplication cannot resolve every alias automatically. PDF/image exhibits are unsupported. Technology-company selection and stopping after enough candidate records can bias the dataset. AI assistance and support were used for implementation, debugging, source review and report preparation.'),
('p', 'The repository contains the code, tests, raw and reviewed CSVs, evidence, manifests, run metadata and review decisions. The model digest, script hash and settings are recorded. Replaying the processed manifest fixes document selection, but output may vary across model builds or hardware. The GitHub URL appears above and on the revised resume; the repository is private, so instructor access is required.'),
('h', 'Sources'),
('source', 'SEC EDGAR APIs: https://www.sec.gov/search-filings/edgar-application-programming-interfaces'),
('source', 'Ollama structured outputs: https://docs.ollama.com/capabilities/structured-outputs'),
('source', 'Qwen3 model: https://ollama.com/library/qwen3:14b'),
]

def add_link(paragraph, url, size=9):
    link = OxmlElement('w:hyperlink')
    link.set(qn('r:id'), paragraph.part.relate_to(url, RT.HYPERLINK, is_external=True))
    run = OxmlElement('w:r'); properties = OxmlElement('w:rPr')
    color = OxmlElement('w:color'); color.set(qn('w:val'), '16446B'); properties.append(color)
    sz = OxmlElement('w:sz'); sz.set(qn('w:val'), str(int(size * 2))); properties.append(sz)
    run.append(properties); text = OxmlElement('w:t'); text.text = url; run.append(text); link.append(run)
    paragraph._p.append(link)

doc = Document()
section = doc.sections[0]
section.page_width, section.page_height = Inches(8.5), Inches(11)
section.top_margin = Inches(.52); section.bottom_margin = Inches(.55)
section.left_margin = section.right_margin = Inches(.6)
section.footer_distance = Inches(.22)
for name in ['Normal', 'Title', 'Heading 1']:
    style = doc.styles[name]
    style.font.name = 'Arial'; style.font.color.rgb = RGBColor(0, 0, 0)
normal = doc.styles['Normal']; normal.font.size = Pt(10.5)
normal.paragraph_format.line_spacing = Pt(13.2); normal.paragraph_format.space_after = Pt(6)
title = doc.styles['Title']; title.font.size = Pt(16); title.font.bold = True
title.paragraph_format.line_spacing = Pt(18); title.paragraph_format.space_after = Pt(8)
h = doc.styles['Heading 1']; h.font.size = Pt(11); h.font.bold = True
h.paragraph_format.space_before = Pt(7); h.paragraph_format.space_after = Pt(4)
h.paragraph_format.keep_with_next = True
styles = {kind: ParagraphStyle(kind, fontName='Helvetica-Bold' if kind in ('title', 'h') else 'Helvetica',
          fontSize={'title': 16, 'h': 11, 'meta': 9, 'link': 9, 'source': 8.5}.get(kind, 10.5),
          leading={'title': 18, 'h': 14, 'meta': 11, 'link': 11, 'source': 11}.get(kind, 13.2),
          spaceAfter=4 if kind == 'source' else 6, spaceBefore=7 if kind == 'h' else 0)
          for kind in ['title', 'h', 'meta', 'link', 'p', 'source']}
story, markdown = [], []
for kind, text in body:
    if kind == 'page':
        doc.add_page_break(); story.append(PageBreak()); continue
    markdown.append(('# ' if kind == 'title' else '## ' if kind == 'h' else '') + text)
    p = doc.add_paragraph(style='Title' if kind == 'title' else 'Heading 1' if kind == 'h' else 'Normal')
    if kind == 'link':
        add_link(p, text)
        formatted = f'<link href="{repo}" color="#16446B">{repo}</link>'
    else:
        p.add_run(text)
        if kind in ('meta', 'source'):
            p.runs[0].font.size = Pt(9 if kind == 'meta' else 8.5)
            p.paragraph_format.line_spacing = Pt(11)
            p.paragraph_format.space_after = Pt(4)
        formatted = escape(text)
    story.append(Paragraph(formatted, styles[kind]))
# Remove Word theme-font and built-in title-border residue.
for root in [doc._element, doc.styles.element]:
    for border in list(root.iter(qn('w:pBdr'))): border.getparent().remove(border)
    for fonts in root.iter(qn('w:rFonts')):
        for attr in ['asciiTheme', 'hAnsiTheme', 'eastAsiaTheme', 'cstheme', 'csTheme']:
            fonts.attrib.pop(qn('w:' + attr), None)
footer = section.footer.paragraphs[0]
footer.add_run('CAP5619 | Revised SEC product extraction').font.size = Pt(8)
doc.core_properties.author = 'Dennis Bryant'
doc.core_properties.title = 'SEC Form 8-K Product Extraction Methodology'
doc.save(OUT / 'methodology_report.docx')
pdf = SimpleDocTemplate(str(OUT / 'methodology_report.pdf'), pagesize=letter,
                       leftMargin=43.2, rightMargin=43.2, topMargin=37.4, bottomMargin=39.6)
def page_footer(canvas, document):
    canvas.setFont('Helvetica', 8)
    canvas.drawString(43.2, 20, 'CAP5619 | Revised SEC product extraction')
    canvas.drawRightString(568.8, 20, str(document.page))
pdf.build(story, onFirstPage=page_footer, onLaterPages=page_footer)
(OUT / 'methodology_report.md').write_text('\n\n'.join(markdown) + '\n', encoding='utf-8')
print('Created Word, PDF and Markdown methodology reports.')
