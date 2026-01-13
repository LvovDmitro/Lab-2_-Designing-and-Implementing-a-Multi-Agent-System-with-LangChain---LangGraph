from typing import List, Optional, Dict, Any, TypedDict
from pydantic import BaseModel, Field
from typing import Literal

# --- Pydantic Models for Data Structures ---

class LiteraturePlan(BaseModel):
    keywords: List[str]
    min_year: int
    need_author_stats: bool

class ArxivResult(BaseModel):
    title: str
    authors: List[str]
    abstract: str
    published_year: int

class AuthorStats(BaseModel):
    h_index: Optional[int] = None
    total_papers: Optional[int] = None

class PaperSummary(BaseModel):
    author: str
    year: int
    title: str
    summary: str

class LiteratureSummary(BaseModel):
    main_trends: str
    notable_papers: List[PaperSummary]
    open_questions: str

# --- State Definition ---

class State(TypedDict):
    query: str
    category: Optional[str]
    plan: Optional[LiteraturePlan]
    papers: Optional[List[ArxivResult]]
    author_stats: Optional[List[AuthorStats]]
    summary: Optional[LiteratureSummary]
    code_response: Optional[str]
    reviewer_feedback: Optional[str]
    final_answer: Optional[str]
    chat_history: List[Dict[str, str]]
    user_profile: Dict[str, Any]