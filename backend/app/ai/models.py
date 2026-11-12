from pydantic import BaseModel
from typing import List


class ReviewIssue(BaseModel):
    severity: str
    category: str
    file: str
    line: int | None = None
    message: str
    suggestion: str


class ReviewResult(BaseModel):
    summary: str
    overall_assessment: str
    issues: List[ReviewIssue]
    recommendations: List[str]