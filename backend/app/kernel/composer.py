from .models import PromptContext, Intent


class PromptComposer:
    """
    Handles system prompts, few-shot examples, and formatting.
    Converts a PromptContext into a final raw string for the LLM.
    """
    def compose(self, context: PromptContext, max_tokens: int = 4000) -> str:
        if context.intent == Intent.HYBRID_QUERY:
            sys_prompt = (
                "You are an AI Engineering Advisor. You are participating in a hybrid query. "
                "You may use your general public knowledge to explain concepts, but you must apply them "
                "correctly to the provided repository evidence if applicable."
            )
        else:
            sys_prompt = (
                "You are an AI Engineering Advisor. You must answer questions based "
                "exclusively on the provided deterministic artifacts. Do not hallucinate."
            )
        
        # Simple token estimation (approx 4 chars per token)
        current_tokens = len(sys_prompt) // 4
        
        history_str = ""
        if context.history:
            history_str = "History:\n" + "\n".join([f"Q: {h.query}\nA: {h.response}" for h in context.history[-3:]])
            current_tokens += len(history_str) // 4
            
        artifacts_str_list = []
        for a in context.artifacts:
            a_str = f"- {a.id} [{a.confidence}]: {a.summary} (Evidence: {a.evidence_ids})"
            a_tokens = len(a_str) // 4
            if current_tokens + a_tokens > max_tokens:
                artifacts_str_list.append("- [TRUNCATED DUE TO TOKEN BUDGET]")
                break
            artifacts_str_list.append(a_str)
            current_tokens += a_tokens
            
        artifacts_str = "\n".join(artifacts_str_list)
        
        if context.intent == Intent.HYBRID_QUERY:
            final_prompt = f"""
{sys_prompt}

{history_str}

=== PUBLIC KNOWLEDGE ===
(Use your training data to explain general concepts requested by the user)

=== REPOSITORY EVIDENCE ===
{artifacts_str}

=== REASONING INSTRUCTIONS ===
1. Explain the requested concepts using public knowledge.
2. If repository evidence is relevant, apply the public knowledge to the evidence.
3. Clearly separate general theory from repository-specific facts.

=== USER QUESTION ===
{context.user_query}
"""
        else:
            final_prompt = f"""
{sys_prompt}

{history_str}

Deterministic Artifacts:
{artifacts_str}

User Query: {context.user_query}
"""
        
        # We mutate the context safely by returning a new string.
        # The prompt context object is immutable.
        return final_prompt
