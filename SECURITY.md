# Security Policy

## Prototype Status

**PIA Industrial is currently a Hackathon / Research Prototype.**
It is NOT yet hardened for production environments containing highly sensitive industrial telemetry (e.g. live SCADA feeds for critical infrastructure).

## Known Security Limitations

- **File Upload Considerations**: The current PDF extraction pipelines do not perform advanced sandboxing of malicious document files.
- **LLM Prompt Injection**: The Knowledge Copilot currently passes raw context to the LLM. While deterministic facts are safe, adversarial user queries could manipulate Copilot output formats.
- **Secrets Management**: Do not hardcode LLM provider keys or database credentials. Ensure they are injected via the `.env` configuration file.
- **Sensitive Industrial Data**: If running on real operational data, ensure the SQLite database and graph cache are stored securely, as they hold unencrypted maintenance facts and failure histories.

## Reporting a Vulnerability

If you discover a potential security issue in this project, please open a standard GitHub issue with the `security` label, or contact the repository owner directly. Do not submit malicious test data to live demo instances.
