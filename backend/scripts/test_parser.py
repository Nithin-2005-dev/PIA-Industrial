import sys
import os
sys.path.append('.')
from app.kernel.semantic_parser import SemanticQueryParser
from app.kernel.provider import LLMProvider, LLMResponse
from app.kernel.models import Intent

class DummyProvider(LLMProvider):
    def generate(self, prompt, **kwargs):
        print(f"Fallback LLM invoked!")
        return LLMResponse(content='```json\n{"goals": ["SIMULATE_DEPARTURE"], "confidence": 0.9}\n```')

parser = SemanticQueryParser(DummyProvider())

sq = parser.parse("when will be the project gets risky when top contributor leaves?", Intent.REPOSITORY_QUERY)
print("Parsed Goals:", [g.name for g in sq.goals])
