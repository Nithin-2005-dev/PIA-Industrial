"""LLM Generator for Industrial Intelligence.

Provides a clean interface for LLM generation. For the hackathon,
this includes a mock generator that formats the retrieved evidence
into a simulated LLM response, allowing end-to-end testing without
requiring API keys.
"""
from __future__ import annotations

import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class LLMGenerator(ABC):
    """Abstract interface for LLM text generation."""

    @abstractmethod
    def generate(self, system_prompt: str, user_prompt: str) -> str:
        """Generate a response based on prompts."""
        ...


class MockLLMGenerator(LLMGenerator):
    """A mock generator for testing and demonstration.

    Simulates an LLM response by extracting facts from the
    provided evidence context and formatting them with citations.
    """

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        # Extract evidence context from system prompt
        context_start = system_prompt.find("--- EVIDENCE CONTEXT ---")
        context_end = system_prompt.find("--- END EVIDENCE CONTEXT ---")
        
        if context_start == -1 or context_end == -1:
            return "Error: Could not find evidence context."

        import re
        findings: list[tuple[str, str]] = []
        seen_normalized: set[str] = set()

        raw_evidence = []
        lines = system_prompt.split("\n")
        current_citation = None
        current_content = []
        in_content = False

        for line in lines:
            if line.startswith("Citation: "):
                if current_citation and current_content:
                    raw_evidence.append((current_citation, " ".join(current_content).strip()))
                current_citation = line.replace("Citation: ", "").strip()
                current_content = []
                in_content = False
            elif line.startswith("Content: ") and current_citation:
                in_content = True
                current_content.append(line.replace("Content: ", "").strip())
            elif line.startswith("----"):
                if current_citation and current_content:
                    raw_evidence.append((current_citation, " ".join(current_content).strip()))
                current_citation = None
                current_content = []
                in_content = False
            elif in_content:
                current_content.append(line.strip())

        findings_pool = []
        
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "from", "of", "is", "are", "was", "were", "this", "that", "it", "its", "with", "for", "by", "as", "be"}
        
        def get_sig_words(text: str) -> set[str]:
            return set(re.findall(r'\b[a-z0-9]+\b', text.lower())) - stop_words

        def sig_overlap(w1: set[str], w2: set[str]) -> float:
            if not w1 or not w2: return 0.0
            return len(w1 & w2) / min(len(w1), len(w2))

        meta_terms = {"monitored indicator", "is a centrifugal", "is a heat exchanger", "is maintained as", "is the upstream", "provides process fluid", "designated as", "asset register", "function:", "appendix", "executive summary", "this report", "disclaimer", "this document", "synthetic report", "demonstration disclaimer", "intended solely as", "conclusion", "maintenance pattern review", "maintenance work order summary"}
        context_terms = {"preventive and does not indicate", "systems processing this report", "where evidence is insufficient", "this designation is provided", "suitable for evidence-based", "automated system analyzing"}
        rec_terms = {"recommend", "ensure", "repair", "establish", "verify", "must", "should", "prevent", "follow-up", "action:", "continue", "review", "perform", "inspect"}

        for tag, content in raw_evidence:
            sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', content) if len(s.strip()) > 15]
            
            for s in sentences:
                if not re.match(r'^[A-Z0-9#\-\*\"\'\[].*[.!?]$', s):
                    continue

                if s.endswith("?"):
                    continue

                norm = s.lower()
                
                if any(term in norm for term in meta_terms):
                    continue
                if any(term in norm for term in context_terms):
                    continue
                    
                is_rec = any(re.search(r'\b' + term + r'\b', norm) for term in rec_terms) or re.search(r'\br\d+\s*[-—]', norm)
                
                score = 0
                if re.search(r'\b\d+(\.\d+)?\s*(mm/s|c|f|psi|bar|hz)\b', norm):
                    score += 5  # Specific measurements are golden
                elif re.search(r'\d+', norm):
                    score += 2
                
                if any(term in norm for term in {"failure", "degrad", "deteriorat", "defect", "root cause"}):
                    score += 4
                if any(term in norm for term in {"vibration", "temperature", "noise", "leak", "abnormal", "elevated", "high"}):
                    score += 3
                if any(term in norm for term in {"replace", "maintenance", "repair", "restor", "intervention"}):
                    score += 3
                if any(term in norm for term in {"trend", "pattern", "progressiv", "increas", "decreas"}):
                    score += 2
                    
                # Penalize short, uninformative sentences
                if len(s.split()) < 6:
                    score -= 3

                findings_pool.append({
                    "text": s,
                    "tag": tag,
                    "score": score,
                    "is_rec": is_rec,
                    "sig_words": get_sig_words(s)
                })

        # Deduplicate
        findings_pool.sort(key=lambda x: x["score"], reverse=True)
        deduped = []
        for f in findings_pool:
            if f["score"] < 0 and not f["is_rec"]:
                continue
                
            is_dup = False
            for d in deduped:
                # Only deduplicate within the same category
                if f["is_rec"] == d["is_rec"]:
                    if sig_overlap(f["sig_words"], d["sig_words"]) > 0.55:
                        is_dup = True
                        break
            if not is_dup:
                deduped.append(f)

        key_findings = [f for f in deduped if not f["is_rec"]]
        recommendations = [f for f in deduped if f["is_rec"]]

        top_findings = key_findings[:6]
        top_recs = recommendations[:4]

        if not top_findings and not top_recs:
            return "I cannot find evidence to answer this question."

        response = ["Based on the available evidence, the key findings are:\n"]
        for f in top_findings:
            response.append(f"• {f['text']} {f['tag']}")
            
        if top_recs:
            response.append("\nRecommended actions:")
            for r in top_recs:
                response.append(f"• {r['text']} {r['tag']}")
                
        return "\n".join(response)
