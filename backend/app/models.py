from pydantic import BaseModel, Field

class PRRequest(BaseModel):
    pr_url: str = Field(min_length=20, max_length=2048)
    model: str = "gemini"


class PRInfo(BaseModel):
    owner:str
    repo:str
    pr_number:int


class RepositoryChatRequest(BaseModel):
    repo_url: str = Field(min_length=19, max_length=2048)
    question: str = Field(min_length=1, max_length=4000)
    model: str = "gemini"


class RepositoryChatResponse(BaseModel):
    question: str = Field(min_length=1, max_length=4000)
    answer: str
    error: str | None = None