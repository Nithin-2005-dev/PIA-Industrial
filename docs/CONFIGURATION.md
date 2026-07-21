# Configuration Guide

PIA Industrial uses a `.env` file located in the `backend/` directory for configuration. 

## Environment Variables

| Variable | Required | Default | Description | Example | Sensitive |
|---|---|---|---|---|---|
| `LLM_PROVIDER` | No | `mock` | The LLM provider for the Copilot interface. Use `mock` for deterministic offline testing. | `openai` | No |
| `OPENAI_API_KEY` | Yes (if `LLM_PROVIDER=openai`) | *None* | The API key for OpenAI. | `sk-12345...` | Yes |
| `ANTHROPIC_API_KEY` | Yes (if `LLM_PROVIDER=anthropic`) | *None* | The API key for Anthropic. | `sk-ant-123...` | Yes |
| `DATABASE_URL` | No | `sqlite:///./industrial.db` | Connection string for the Observation Store. | `sqlite:///./demo.db` | No |
| `LOG_LEVEL` | No | `INFO` | The verbosity of system logs. | `DEBUG` | No |

## Example `.env` File

```env
# backend/.env
LLM_PROVIDER=mock
LOG_LEVEL=INFO
DATABASE_URL=sqlite:///./industrial.db
```

*Note: Never commit your `.env` file to version control. An empty template is provided as `.env.example`.*
