import re
import json
import uuid
from typing import Optional, List
from .models import (
    SemanticQuery, EntityType, Scope, Entity, 
    ParserConfidence, Intent, Constraint, Goal
)

class SemanticQueryParser:
    def __init__(self, provider):
        self.provider = provider
        self.stop_words = {"what", "is", "the", "of", "this", "in", "for", "to", "how", "are", "do", "we", "can", "you", "tell", "me", "about", "a", "an", "?", "who", "when", "where", "did", "happen", "org", "repo", "repository", "project", "which", "show", "find", "most"}

    def parse(self, query: str, intent: Intent = Intent.REPOSITORY_QUERY) -> SemanticQuery:
        """Parses a query into a SemanticQuery by extracting keywords and topics."""
        semantic_memory_id = str(uuid.uuid4())
        
        keywords = self._extract_keywords(query)
        return self._llm_parse(query, intent, semantic_memory_id, keywords)

    def _extract_keywords(self, query: str) -> List[str]:
        words = re.findall(r'\b\w+\b', query.lower())
        return [w for w in words if w not in self.stop_words]

    def _llm_parse(self, query: str, intent: Intent, memory_id: str, fallback_keywords: List[str]) -> SemanticQuery:
        prompt = f"""
        You are a Semantic Query Normalizer for a software engineering intelligence system.
        Your job is to extract high-level semantic meaning from the user's query into a strict JSON format.
        
        Rules:
        1. Extract the core 'topics' (e.g. 'health', 'ownership', 'risk', 'departure', 'architecture', 'forecast', 'contributors').
        2. Extract any important 'keywords' verbatim from the query.
        3. Identify any 'entities' (e.g., PERSON, MODULE, FILE).
        4. Determine the 'scope' (REPOSITORY, COMPONENT, FILE, ORGANIZATION, PERSON).
        
        User Query: "{query}"
        
        Return ONLY valid JSON matching this schema:
        {{
            "topics": ["risk", "departure"],
            "keywords": ["leaves", "top contributor", "risky"],
            "entities": [{{"type": "PERSON", "value": "John"}}],
            "scope": "REPOSITORY",
            "confidence": 0.9
        }}
        """
        try:
            response = self.provider.generate(prompt=prompt)
            content = response.content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            data = json.loads(content)
            
            topics = [str(t).lower() for t in data.get("topics", [])]
            keywords = [str(k).lower() for k in data.get("keywords", [])]
            
            for fk in fallback_keywords:
                if fk not in keywords:
                    keywords.append(fk)
                
            entities = [Entity(type=EntityType[e["type"]], value=e["value"]) 
                        for e in data.get("entities", []) if e["type"] in EntityType.__members__]
            
            scope = Scope[data.get("scope", "REPOSITORY")] if data.get("scope") in Scope.__members__ else Scope.REPOSITORY
            
            conf = ParserConfidence(
                overall=float(data.get("confidence", 0.5)),
                ambiguity=False,
                requires_clarification=False
            )
            goals = self._infer_goals(topics, keywords)
            
            return SemanticQuery(
                semantic_memory_id=memory_id,
                intent=intent,
                goals=goals,
                topics=topics,
                keywords=keywords,
                entities=entities,
                scope=scope,
                time_horizon="current",
                output_format="text",
                parser_confidence=conf
            )
        except Exception as e:
            print(f"[Semantic Parser Error] {e}")
            return SemanticQuery(
                semantic_memory_id=memory_id,
                intent=intent,
                goals=self._infer_goals([], fallback_keywords),
                topics=[],
                keywords=fallback_keywords,
                parser_confidence=ParserConfidence(overall=0.0, ambiguity=True, requires_clarification=True)
            )

    def _infer_goals(self, topics: List[str], keywords: List[str]) -> List[Goal]:
        """Map semantic meaning to goals without selecting concrete capabilities."""
        terms = {t.lower() for t in topics + keywords}
        goals: List[Goal] = []

        def add(goal: Goal) -> None:
            if goal not in goals:
                goals.append(goal)

        if terms.intersection({"who", "developer", "contributor", "author", "expert", "expertise", "person", "reviewer", "reviews", "commits"}):
            add(Goal.FIND_CONTRIBUTOR)
        if terms.intersection({"owner", "ownership", "owns", "owned", "maintainer", "authorship"}):
            add(Goal.FIND_OWNER)
        if terms.intersection({"leave", "leaves", "leaving", "departure", "quit", "gap", "counterfactual"}):
            add(Goal.SIMULATE_DEPARTURE)
        if terms.intersection({"forecast", "future", "predict", "trend", "month", "quarter"}):
            add(Goal.FORECAST)
        if terms.intersection({"risk", "risky", "riskiest", "bus", "factor", "knowledge", "loss", "concentration"}):
            add(Goal.IDENTIFY_RISK)
        if terms.intersection({"why", "cause", "causal", "root"}):
            add(Goal.DIAGNOSE_CAUSALITY)
        if terms.intersection({"graph", "topology", "relationship", "relationships", "dependency", "dependencies", "architecture"}):
            add(Goal.VISUALIZE_GRAPH)
        if terms.intersection({"health", "quality", "debt", "summary", "summarize", "unstable", "instability", "coverage", "tests", "hotspots"}):
            add(Goal.SUMMARIZE)
        if terms.intersection({"compare", "versus", "vs"}):
            add(Goal.COMPARE)
        if not goals and terms:
            add(Goal.ANALYZE)
        return goals
