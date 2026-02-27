from typing import List, Dict, TypedDict, Annotated, Union, Optional

from langgraph.graph import StateGraph, END
from .models import (
    ResearchStrategy, 
    Source, 
    ResearchFinding, 
    VerifiedFinding, 
    QueryMetadata
)
from .agents.planner import PlannerAgent
from .agents.research_orchestrator import ResearchOrchestrator
from .agents.query_controller import QueryController
from .agents.verifier import VerifierAgent

from .agents.synthesizer import SynthesizerAgent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

from .agents.research_orchestrator import ResearchOrchestrator
from .tools.search_orchestrator import SearchOrchestrator
from .tools.crawler import CrawlerLayer

class ResearchState(TypedDict):
    original_query: str
    query_metadata: Optional[QueryMetadata]
    strategy: Optional[ResearchStrategy]
    sources: List[Source]
    findings: List[ResearchFinding]
    verified_findings: List[VerifiedFinding]
    ideator_output: str
    final_report: str
    errors: List[str]

async def planning_node(state: ResearchState) -> Dict:
    print("---NODE: PLANNING---")
    controller = QueryController()
    planner = PlannerAgent()
    
    metadata = await controller.process_query(state["original_query"])
    strategy = await planner.generate_strategy(metadata.query)
    
    return {"query_metadata": metadata, "strategy": strategy}

async def search_node(state: ResearchState) -> Dict:
    print("---NODE: SEARCHING---")
    searcher = SearchOrchestrator()
    sources = await searcher.search(state["strategy"].search_queries)
    return {"sources": sources}

async def crawl_node(state: ResearchState) -> Dict:
    print("---NODE: CRAWLING---")
    crawler = CrawlerLayer()
    # Deep crawl the sources found
    updated_sources = await crawler.crawl_multiple(state["sources"])
    return {"sources": updated_sources}

async def research_node(state: ResearchState) -> Dict:
    print("---NODE: RESEARCHING---")
    orchestrator = ResearchOrchestrator()
    findings = await orchestrator.run_research(state["strategy"], state["sources"])
    return {"findings": findings}

async def verify_node(state: ResearchState) -> ResearchState:
    print("---NODE: VERIFYING---")
    verifier = VerifierAgent()
    state['verified_findings'] = await verifier.verify(state['findings'])
    return state

async def ideator_node(state: ResearchState) -> ResearchState:
    print("---NODE: IDEATING---")
    from .utils.llm_manager import llm_manager
    from .config import DEFAULT_MODEL
    
    api_key = llm_manager.get_gemini_key()
    llm = ChatGoogleGenerativeAI(
        model=DEFAULT_MODEL,
        google_api_key=api_key,
        temperature=0.8
    )

    # Gather full context for the expert ideator
    context = (
        f"Original Query: {state['original_query']}\n"
        f"Research Strategy: {state['strategy'].search_queries if state['strategy'] else 'N/A'}\n"
        "Key Findings:\n"
    )
    for f in state['verified_findings']:
        context += f"- Role: {f.original_finding.role}, Focus: {f.original_finding.focus}\n"
        context += f"  Content: {f.original_finding.findings[:2000]}\n"

    system_prompt = (
        "You are an Elite Research Architect and Visionary. Your task is to observe the entire research flow "
        "including the initial constraints, the search strategy employed, and the verified technical findings. "
        "Do not just summarize. You must synthesis a novel perspective. Identify deep research gaps, "
        "potential contradictions between findings, and propose 3-5 groundbreaking new research topics or "
        "hypotheses that could be explored next. Act as an expert watching the entire process from above."
    )

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Comprehensive Research Context:\n{context}\n\nPropose novel research ideas/topics in markdown format.")
    ]

    response = await llm.ainvoke(messages)
    state['ideator_output'] = str(response.content)
    return state


async def synthesize_node(state: ResearchState) -> ResearchState:
    print("---NODE: SYNTHESIZING---")
    synthesizer = SynthesizerAgent()
    state['final_report'] = await synthesizer.synthesize(state['verified_findings'], state.get('ideator_output', ""))
    return state

def create_research_graph():
    workflow = StateGraph(ResearchState)
    
    workflow.add_node("planner", planning_node)
    workflow.add_node("searcher", search_node)
    workflow.add_node("crawler", crawl_node)
    workflow.add_node("researcher", research_node)
    workflow.add_node("verifier", verify_node)
    workflow.add_node("ideator", ideator_node)
    workflow.add_node("synthesizer", synthesize_node)

    
    workflow.set_entry_point("planner")
    workflow.add_edge("planner", "searcher")
    workflow.add_edge("searcher", "crawler")
    workflow.add_edge("crawler", "researcher")
    workflow.add_edge("researcher", "verifier")
    workflow.add_edge("verifier", "ideator")
    workflow.add_edge("ideator", "synthesizer")
    workflow.add_edge("synthesizer", END)

    
    return workflow.compile()
