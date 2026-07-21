from typing import List
from .models import CognitiveAnswer, CognitiveGoal, PromptArtifact, PromptContext, RetrievedEvidence, RepositorySession


class ContextBuilder:
    """
    Bundles the user query, retrieved artifacts, and conversation history.
    """
    def build(
        self,
        goal: CognitiveGoal,
        evidence: RetrievedEvidence,
        history: List[CognitiveAnswer],
        repo_session: RepositorySession = None
    ) -> PromptContext:
        # Build a base system prompt. The Composer may extend this.
        system_prompt = "You are a helpful AI engineering assistant."
        
        if repo_session:
            system_prompt += (
                f"\n\nActive Repository Context:\n"
                f"- Repository: {repo_session.repository}\n"
                f"- Branch: {repo_session.branch}\n"
                f"- Commits: {repo_session.commit_window}\n"
                f"Please ensure all repository-specific claims refer to this active repository."
            )

        return PromptContext(
            system_prompt=system_prompt,
            user_query=goal.query,
            artifacts=evidence.artifacts,
            repository_session=repo_session,
            history=history
        )
