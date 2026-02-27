from typing import List

from ..models import VerifiedFinding

class SynthesizerAgent:
    async def synthesize(self, verified_findings: List[VerifiedFinding], query: str) -> str:
        report = f"# Research Report: {query}\n\n"
    async def synthesize(self, verified_findings: List[VerifiedFinding], ideator_output: str = "") -> str:
        # Use LLM to create a cohesive report from verified findings
        # For now, we'll format it as markdown
        report_sections = []
        for finding in verified_findings:
            report_sections.append(f"### {finding.original_finding.role}: {finding.original_finding.focus}\n{finding.original_finding.findings}")
        
        # Add Research Ideas Section
        ideator_section = ""
        if ideator_output:
            ideator_section = f"## Potential Research Areas & Future Directions\n{ideator_output}\n"

        # Collect unique sources for the references section
        unique_sources = set()
        for f in verified_findings:
            for c in f.original_finding.citations:
                unique_sources.add(c)
        
        references_section = "## References\n"
        for i, source in enumerate(sorted(list(unique_sources)), 1):
            references_section += f"[{i}] {source}\n"

        report = f"# Research Report\n\n## Abstract\nThis report synthesizes findings from a multi-agent deep research process, focusing on academic and verified technical sources.\n\n## Key Findings\n" + "\n".join(report_sections) + f"\n\n{ideator_section}\n" + references_section
        return report
