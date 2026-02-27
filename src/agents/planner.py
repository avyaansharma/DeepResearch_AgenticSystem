import json
from ..models import ResearchStrategy, ResearchAgentPlan
from ..config import DEFAULT_MODEL
# Assume an LLM client utility is available or use a mocked one for now

class PlannerAgent:
    def __init__(self, model: str = None):
        from ..config import DEFAULT_MODEL
        self.model = model or DEFAULT_MODEL


    async def generate_strategy(self, query: str) -> ResearchStrategy:
        # Better query generation to include various sources
        return ResearchStrategy(
            search_queries=[
                f"latest research papers on {query}",
                f"technical architecture of {query}",
                f"SOTA analysis {query}",
                f"{query} conference proceedings IEEE ACM",
                f"systematic review {query}",
                f"{query} performance benchmarks"
            ],
            agent_plan=[
                ResearchAgentPlan(role="Literature Reviewer", focus="Technical Foundations", description="Extracts core concepts and methodologies from papers."),
                ResearchAgentPlan(role="Academic Critic", focus="Limitations and Gaps", description="Evaluates the rigor and identifies missing links in the field.")
            ]
        )


