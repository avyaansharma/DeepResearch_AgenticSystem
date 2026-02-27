from pydantic import BaseModel, Field
from typing import List, Optional

class QueryMetadata(BaseModel):
    query: str
    depth: str = "deep"
    domain: Optional[str] = None
    timestamp: str

class ResearchAgentPlan(BaseModel):
    role: str
    focus: str
    description: str

class ResearchStrategy(BaseModel):
    search_queries: List[str]
    agent_plan: List[ResearchAgentPlan]

class Source(BaseModel):
    url: str
    title: Optional[str] = None
    snippet: Optional[str] = None
    content: Optional[str] = None
    metadata: Optional[dict] = Field(default_factory=dict) # e.g. author, date, domain

class ResearchFinding(BaseModel):
    role: str
    focus: str
    findings: str
    citations: List[str] = Field(default_factory=list) # List of source URLs or IDs
    technical_points: List[str] = Field(default_factory=list)

class VerifiedFinding(BaseModel):
    original_finding: ResearchFinding
    is_verified: bool
    confidence: float
    reasoning: str
    corrected_findings: Optional[str] = None

