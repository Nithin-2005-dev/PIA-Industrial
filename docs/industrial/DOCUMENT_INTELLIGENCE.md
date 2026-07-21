# Document Intelligence

PIA Industrial ingests documents through `app.ingestion.observation.adapters`.

## Supported Formats

**Currently Implemented:**
- Plain text (`.txt`): e.g., shift logs, digital notes.
- Maximo/SAP structured exports (JSON/CSV).
- *PDF parsing is implemented conceptually in the API but relies on basic text extraction in this prototype.*

**Planned Support (Not Yet Implemented):**
- P&ID Computer Vision (Vision-Language Models).
- Live SCADA historians via MQTT.

## Pipeline Architecture

1. **Parsing:** Raw bytes are parsed into text strings.
2. **Chunking & Metadata:** Text is chunked (if excessively long) and tagged with source metadata (e.g., filename, author, timestamp).
3. **Normalization (`BaseEventSchema`):** Disparate text blobs are cast into a unified internal model.
4. **Extraction (`app.extraction`):** NLP logic searches the text block for specific named entities (P-101, Vibration, Mechanical Wear).
5. **Provenance Tagging:** The original raw text and the exact character indices of the extracted entities are saved. This guarantees that Copilot citations map perfectly back to the ingested document.

## Limitations

- The current OCR capabilities in the prototype are limited to machine-readable PDFs. Scanned image PDFs will require the future CV pipeline integration.
