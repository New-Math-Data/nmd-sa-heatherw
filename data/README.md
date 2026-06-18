# Sample Data — IRS Tax Form Metadata

Simplified JSON documents representing IRS tax form metadata. These files are used to test the document ingestion and search API without requiring PDF parsing.

## Usage

POST any file to the documents endpoint to test ingestion:

```bash
curl -X POST http://localhost:8080/api/v1/documents \
  -H "Content-Type: application/json" \
  -d @data/w9.json
```

After ingesting documents, test vector search:

```bash
curl -X POST http://localhost:8080/api/v1/search \
  -H "Content-Type: application/json" \
  -d '{"query": "tax withholding for employees"}'
```

## Files

| File | Description |
|------|-------------|
| w9.json | Request for Taxpayer Identification Number and Certification |
| w4.json | Employee's Withholding Certificate |
| 1040.json | U.S. Individual Income Tax Return |
| 1099-misc.json | Miscellaneous Information (freelance/contract income) |
| schedule-c.json | Profit or Loss From Business (Sole Proprietorship) |

## Schema

Each JSON file contains:

- **title** — official form name
- **content** — plain-text description of the form's purpose and usage
- **category** — classification grouping (e.g., "income_tax", "employment", "business")

These fields map directly to the `DocumentCreate` schema accepted by `POST /api/v1/documents`.
