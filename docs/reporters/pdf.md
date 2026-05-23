# PDF Reporter

The **PDF reporter** produces a self-contained PDF document summarising all
outdated dependencies found across every manifest in the repository.

## Usage

```yaml
- uses: your-org/depcheck-action@v1
  with:
    reporters: pdf
    pdf_output: depcheck-report.pdf
```

The reporter writes raw PDF bytes to the path specified by `pdf_output`
(default: `depcheck-report.pdf` in the workspace root).

## Output format

The generated PDF contains:

| Section | Content |
|---|---|
| Header | Report title and UTC timestamp |
| Summary | Total dependencies scanned and total outdated count |
| Per-ecosystem table | Manifest path, outdated count, and a list of `name: current → latest` entries |

## Notes

- The reporter has **no runtime dependencies** — it builds a minimal but
  spec-compliant PDF-1.4 file using only the Python standard library.
- Long reports are capped at **70 lines per page**. For repositories with a
  very large number of outdated packages consider the HTML reporter piped
  through a headless browser for multi-page output.
- Special characters `(`, `)`, and `\\` in package names or version strings are
  automatically escaped per the PDF specification.

## Programmatic use

```python
from src.reporters.pdf_reporter import PdfReporter

reporter = PdfReporter()
pdf_bytes = reporter.render(results)  # List[DetectionResult]

with open("report.pdf", "wb") as fh:
    fh.write(pdf_bytes)
```

## Comparison with other reporters

| Reporter | Format | Human-readable | Machine-readable |
|---|---|---|---|
| `markdown` | `.md` | ✅ | ⚠️ |
| `html` | `.html` | ✅ | ❌ |
| `pdf` | `.pdf` | ✅ | ❌ |
| `json` | `.json` | ❌ | ✅ |
| `csv` | `.csv` | ⚠️ | ✅ |
