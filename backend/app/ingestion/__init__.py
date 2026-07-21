"""Document Ingestion Pipeline for PIA Industrial.

This package handles the complete document lifecycle:
1. File detection and adapter routing
2. Text/table extraction (PDF, CSV, XLSX, DOCX, TXT)
3. Semantic chunking with overlap
4. Provenance assignment
5. Duplicate detection
6. Document registration

All extracted content preserves full provenance for
citation-grounded answers.
"""
