from crewai import Agent, Task, Crew, Process
from ..models import ResearchStrategy, Source, ResearchFinding
from typing import List
from ..utils.llm_manager import llm_manager
from langchain_google_genai import ChatGoogleGenerativeAI
import os

class ResearchOrchestrator:
    def __init__(self, model: str = None): 
        from ..config import DEFAULT_MODEL
        self.model_name = model or DEFAULT_MODEL

    def _create_agents(self) -> List[Agent]:
        # Get a rotated Gemini API key
        api_key = llm_manager.get_gemini_key()
        
        # Initialize Gemini via LangChain
        llm = ChatGoogleGenerativeAI(
            model=self.model_name,
            google_api_key=api_key,
            temperature=0.2
        )
        
        literature_reviewer = Agent(
            role='Senior Literature Reviewer',
            goal='Extract key technical findings and evidence from research papers and articles.',
            backstory='You are an expert at parsing academic papers and technical blogs. You focus on methodology, results, and citations.',
            verbose=True,
            allow_delegation=False,
            llm=llm
        )
        
        academic_critic = Agent(
            role='Academic Critic',
            goal='Evaluate the validity and limitations of the research findings.',
            backstory='You have a PhD and are known for identifying research gaps and potential biases in technical literature.',
            verbose=True,
            allow_delegation=False,
            llm=llm
        )

        return [literature_reviewer, academic_critic]

    async def run_research(self, strategy: ResearchStrategy, sources: List[Source]) -> List[ResearchFinding]:
        # Throttling to avoid rate limits
        await llm_manager.throttle()
        
        # Prepare context from sources
        context_str = "\n\n".join([f"Source: {s.url}\nTitle: {s.title}\nContent: {s.content[:5000]}..." for s in sources])
        
        agents = self._create_agents()
        tasks = []

        for agent in agents:
            task = Task(
                description=f"Analyze the following research context and provide findings for the role {agent.role} focus area: {strategy.agent_plan[0].focus if strategy.agent_plan else 'general'}.\n\nContext:\n{context_str}",
                expected_output="A structured report of findings with specific citations (URLs) for each claim.",
                agent=agent
            )
            tasks.append(task)

        crew = Crew(
            agents=agents,
            tasks=tasks,
            process=Process.sequential,
            verbose=True
        )

        result = crew.kickoff()
        
        findings = []
        for agent in agents:
            findings.append(ResearchFinding(
                role=agent.role,
                focus="Technical Literature",
                findings=str(result),
                citations=[s.url for s in sources],
                technical_points=["..."]
            ))
        
        return findings


