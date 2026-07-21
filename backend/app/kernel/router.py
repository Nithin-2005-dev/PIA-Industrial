import json
import re
from typing import List, Optional

from .models import IntentClassification, Intent, CognitiveTopic
from .provider import LLMProvider

LLM_ROUTING_THRESHOLD = 0.90
HYBRID_THRESHOLD = 0.75

class IntentRouter:
    """
    Routes incoming user queries to the appropriate cognitive path.
    Uses fast deterministic heuristics first, falling back to LLM for ambiguity.
    """
    def __init__(self, provider: LLMProvider):
        self.provider = provider

    def route(self, query: str) -> IntentClassification:
        query_lower = query.strip().lower()

        # 1. Regex: General Chat
        if re.search(r'^(hello|hi|hey|thanks|thank you|who are you|how are you)(\s.*)?$', query_lower):
            return IntentClassification(
                intent=Intent.GENERAL_CHAT,
                confidence=1.0,
                reason="Regex match: Greeting/Chat pattern.",
                requires_repository=False
            )

        # 2. Regex: System Platform
        if re.search(r'(what models|what tools|what providers|platform state|help)', query_lower):
            return IntentClassification(
                intent=Intent.SYSTEM_PLATFORM,
                confidence=0.98,
                reason="Regex match: System Platform request.",
                requires_repository=False
            )
            
        # 3. Regex: System Runtime
        if re.search(r'(what repository|which branch|how many commits|show planner|show retrieved)', query_lower):
            return IntentClassification(
                intent=Intent.SYSTEM_RUNTIME,
                confidence=0.98,
                reason="Regex match: System Runtime request.",
                requires_repository=False
            )

        # 4. Dictionary / Regex: Repository Query & Semantic Vocabulary Mapping
        semantic_vocab = {
            r'(best|top) (developer|dev|contributor|coder|author|programmer)': [CognitiveTopic.EXPERTISE, CognitiveTopic.ORGANIZATION],
            r'(who|which).*(contributed|contributor|developer|author|expert|commits?)': [CognitiveTopic.EXPERTISE, CognitiveTopic.ORGANIZATION],
            r'(critical|weak|weakest) (module|subsystem|component|file)': [CognitiveTopic.ORGANIZATION, CognitiveTopic.KNOWLEDGE_GRAPH],
            r'(risky|riskiest|risk|highest risk|knowledge risk|future risk)': [CognitiveTopic.FORECAST, CognitiveTopic.SIMULATION, CognitiveTopic.CAUSAL, CognitiveTopic.KNOWLEDGE_GRAPH, CognitiveTopic.ORGANIZATION],
            r'(key )?maintainer': [CognitiveTopic.ORGANIZATION],
            r'(ownership|owner|owns|owned|maintainer|authorship|highest ownership|most concentrated ownership|who owns)': [CognitiveTopic.ORGANIZATION, CognitiveTopic.EXPERTISE],
            r'(technical debt|health|quality|unstable|instability|hotspot|hotspots|without tests|coverage)': [CognitiveTopic.ORGANIZATION, CognitiveTopic.FORECAST],
            r'documentation quality': [CognitiveTopic.KNOWLEDGE_GRAPH],
            r'(review bottleneck|reviews? most|reviewer)': [CognitiveTopic.ORGANIZATION, CognitiveTopic.OPTIMIZATION, CognitiveTopic.EXPERTISE],
            r'(high risk file|risk file)': [CognitiveTopic.FORECAST, CognitiveTopic.CAUSAL],
            r'(executive summary|summarize repository|repo summary|analyze)': [CognitiveTopic.EXECUTIVE, CognitiveTopic.REPOSITORY],
            r'(forecast|future|trend|next month|next quarter)': [CognitiveTopic.FORECAST],
            r'(simulate|what if|leaves|leaving|departure|biggest gap)': [CognitiveTopic.SIMULATION],
            r'(why|root cause|causal|cause)': [CognitiveTopic.CAUSAL],
            r'(optimize|portfolio|recommend)': [CognitiveTopic.OPTIMIZATION],
            r'(bus factor|key person|single point)': [CognitiveTopic.ORGANIZATION],
            r'(graph|dependency|dependencies|relationship|relationships|topology|architecture)': [CognitiveTopic.KNOWLEDGE_GRAPH],
            r'(compare|versus| vs )': [CognitiveTopic.ORGANIZATION, CognitiveTopic.REPOSITORY],
        }
        
        matched_topics = set()
        for pattern, topics in semantic_vocab.items():
            if re.search(pattern, query_lower):
                matched_topics.update(topics)
                
        if matched_topics:
            return IntentClassification(
                intent=Intent.REPOSITORY_QUERY,
                confidence=0.98,
                reason="Regex match: Semantic Vocabulary.",
                requires_repository=True,
                topics=tuple(matched_topics)
            )

        # 5. Heuristic: Hybrid Query
        if re.search(r'^(explain|teach me|what is|how does|theory|concept)\b', query_lower):
            return IntentClassification(
                intent=Intent.HYBRID_QUERY,
                confidence=0.90,
                reason="Regex match: Explanation request.",
                requires_repository=True,
                topics=(CognitiveTopic.GENERAL_KNOWLEDGE,)
            )

        # 6. Fallback: LLM Classification
        return self._llm_classify(query)

    def _llm_classify(self, query: str) -> IntentClassification:
        prompt = f"""
        Classify the following user query into one of these intents:
        - GENERAL_CHAT: Greetings or casual chat.
        - SYSTEM_PLATFORM: Asking about AI models, tools, or configuration.
        - SYSTEM_RUNTIME: Asking about current loaded repository, branches, or state.
        - REPOSITORY_QUERY: Asking for data, analytics, forecasts, or summaries about the analyzed codebase.
        - HYBRID_QUERY: Asking for an explanation of a concept, optionally applied to the codebase.

        Query: "{query}"

        Respond ONLY with a JSON object in this format:
        {{
            "intent": "GENERAL_CHAT",
            "confidence": 0.0 to 1.0,
            "reason": "...",
            "requires_repository": true/false,
            "topics": ["ORGANIZATION", "FORECAST", "CAUSAL", "SIMULATION", "REPOSITORY", "GENERAL_KNOWLEDGE"]
        }}
        """
        response = self.provider.generate(prompt)
        
        try:
            content = response.content
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].strip()
                
            data = json.loads(content)
            
            intent_map = {
                "GENERAL_CHAT": Intent.GENERAL_CHAT,
                "SYSTEM_PLATFORM": Intent.SYSTEM_PLATFORM,
                "SYSTEM_RUNTIME": Intent.SYSTEM_RUNTIME,
                "REPOSITORY_QUERY": Intent.REPOSITORY_QUERY,
                "HYBRID_QUERY": Intent.HYBRID_QUERY
            }
            
            topic_map = {
                "ORGANIZATION": CognitiveTopic.ORGANIZATION,
                "FORECAST": CognitiveTopic.FORECAST,
                "SIMULATION": CognitiveTopic.SIMULATION,
                "CAUSAL": CognitiveTopic.CAUSAL,
                "REPOSITORY": CognitiveTopic.REPOSITORY,
                "GENERAL_KNOWLEDGE": CognitiveTopic.GENERAL_KNOWLEDGE
            }
            
            raw_intent = data.get("intent", "REPOSITORY_QUERY")
            intent = intent_map.get(raw_intent, Intent.REPOSITORY_QUERY)
            
            raw_topics = data.get("topics", [])
            topics = [topic_map.get(t) for t in raw_topics if topic_map.get(t)]
            
            requires_repo = data.get("requires_repository", True)
            if intent in (Intent.REPOSITORY_QUERY, Intent.HYBRID_QUERY):
                requires_repo = True
                
            return IntentClassification(
                intent=intent,
                confidence=data.get("confidence", 0.5),
                reason=data.get("reason", "LLM fallback classification."),
                requires_repository=requires_repo,
                topics=tuple(topics)
            )
        except Exception:
            return IntentClassification(
                intent=Intent.REPOSITORY_QUERY,
                confidence=0.1,
                reason="LLM parsing failed. Failsafe default.",
                requires_repository=True,
                topics=(CognitiveTopic.REPOSITORY,)
            )
