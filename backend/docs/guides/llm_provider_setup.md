# LLM Provider Setup & Configuration

The Cognitive Runtime connects to Language Models via a standardized `LLMProvider` protocol. This isolates vendor-specific APIs from the core architectural logic, making providers entirely swappable.

## 1. Real Provider Configurations

Here is how you configure each supported provider.

### OpenAI
```python
from app.kernel.provider import OpenAIProvider

provider = OpenAIProvider(
    api_key=os.environ["OPENAI_API_KEY"],
    model="gpt-5"
)
```

### Google Gemini
```python
from app.kernel.provider import GeminiProvider

provider = GeminiProvider(
    api_key=os.environ["GEMINI_API_KEY"],
    model="gemini-2.5-pro"
)
```

### Ollama (Local)
```python
from app.kernel.provider import OllamaProvider

provider = OllamaProvider(
    host="http://localhost:11434",
    model="qwen3:latest"
)
```

## 2. `.env` Configuration

We recommend managing your keys using a standard `.env` file instead of passing them explicitly in code.

```text
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=AIza...
ANTHROPIC_API_KEY=sk-ant-...

OLLAMA_HOST=http://localhost:11434

DEFAULT_PROVIDER=openai
DEFAULT_MODEL=gpt-5
```

The application uses standard libraries (like `python-dotenv`) to load these at startup.

## 3. Advanced Configuration (YAML / TOML)

To avoid hardcoding provider switches in Python, PIA supports structured configuration files. 

Example `config.yaml`:
```yaml
cognitive:
  provider: openai
  model: gpt-5
  temperature: 0.2
  api_key: ${OPENAI_API_KEY}
```

Example `config.toml`:
```toml
[cognitive]
provider = "gemini"
model = "gemini-2.5-pro"
temperature = 0.1
```

This allows operators to swap providers and models easily without code changes.

## 4. Provider Selection Precedence

When initializing the `CognitiveRuntime`, the platform determines which provider to use based on a strict precedence hierarchy:

1. **Explicit Instance**: If a provider is passed explicitly (e.g., `CognitiveRuntime(provider=OpenAIProvider(...))`), use it.
2. **DEFAULT_PROVIDER Config**: If no provider is passed, read `DEFAULT_PROVIDER` from the `.env` or YAML config.
3. **Environment Key Presence**: If no default is specified, inspect the environment for keys (e.g. if `OPENAI_API_KEY` exists, instantiate `OpenAIProvider`).
4. **Fallback to Mock**: If no keys or configs are found, instantiate the `MockLLMProvider` and log a warning.

This precedence ensures that production deployments fail gracefully or fall back to safe mocks during CI testing.
