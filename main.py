import asyncio
import sys
from src.graph import create_research_graph

async def run_deep_research(user_query: str):
    print(f"Starting Research-Centric Deep Research for: {user_query}")

    
    app = create_research_graph()
    
    initial_state = {
        "original_query": user_query,
        "query_metadata": None,
        "strategy": None,
        "sources": [],
        "findings": [],
        "verified_findings": [],
        "ideator_output": "",
        "final_report": "",
        "errors": []
    }

    
    # Run the graph
    final_state = await app.ainvoke(initial_state)
    
    # Output Report
    report = final_state.get("final_report", "Research failed to generate a report.")
    
    with open("final_report.md", "w", encoding="utf-8") as f:
        f.write(report)
    
    print("\n✨ Research Complete! Report saved to final_report.md")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        query = "Advancements in Multimodal Large Language Models 2024-2025"
    else:
        query = " ".join(sys.argv[1:])
    
    asyncio.run(run_deep_research(query))
