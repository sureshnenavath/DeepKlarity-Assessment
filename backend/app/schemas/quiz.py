"""
Pydantic schemas for request/response validation.
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import datetime
from enum import Enum


class DifficultyLevel(str, Enum):
    """Difficulty levels for questions."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class EntityType(str, Enum):
    """Entity types."""
    PEOPLE = "people"
    ORGANIZATIONS = "organizations"
    LOCATIONS = "locations"


# ========== Request Schemas ==========

class QuizGenerateRequest(BaseModel):
    """Request schema for generating a new quiz."""
    url: str = Field(..., description="URL of the article to generate quiz from")
    num_questions: Optional[int] = Field(default=8, ge=5, le=10, description="Number of questions to generate")
    
    @field_validator('url')
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Validate URL format."""
        if not v.startswith(('http://', 'https://')):
            raise ValueError('URL must start with http:// or https://')
        return v


# ========== Response Schemas ==========

class QuestionJSON(BaseModel):
    """JSON response schema for a single question."""
    question: str
    options: List[str]
    answer: str
    difficulty: str
    explanation: Optional[str] = None


class KeyEntitiesJSON(BaseModel):
    """JSON schema grouping key entities by type."""
    people: List[str] = []
    organizations: List[str] = []
    locations: List[str] = []


class QuizResponse(BaseModel):
    """Full JSON response for a generated quiz."""
    id: int
    url: str
    title: Optional[str] = None
    summary: Optional[str] = None
    key_entities: KeyEntitiesJSON = Field(default_factory=KeyEntitiesJSON)
    sections: List[str] = []
    quiz: List[QuestionJSON] = []
    related_topics: List[str] = []
    created_at: datetime

    class Config:
        from_attributes = True


class QuizListItem(BaseModel):
    """Summary metadata for a quiz in the history view."""
    id: int
    url: str
    title: Optional[str] = None
    summary: Optional[str] = None
    created_at: datetime
    question_count: int

    class Config:
        from_attributes = True


class QuizHistoryResponse(BaseModel):
    """Response schema for paginated quiz history."""
    quizzes: List[QuizListItem]
    total: int
    page: int
    limit: int
    total_pages: int

    class Config:
        from_attributes = True


# ========== Legacy Response Schemas (for backward compatibility) ==========

class QuestionResponse(BaseModel):
    """Legacy response schema for a single question."""
    id: int
    question_text: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    correct_answer: str
    difficulty: DifficultyLevel
    explanation: Optional[str] = None
    section_reference: Optional[str] = None

    class Config:
        from_attributes = True


class KeyEntityResponse(BaseModel):
    """Legacy response schema for a key entity."""
    id: int
    entity_type: EntityType
    entity_name: str

    class Config:
        from_attributes = True


class RelatedTopicResponse(BaseModel):
    """Legacy response schema for a related topic."""
    id: int
    topic_name: str
    topic_url: Optional[str] = None

    class Config:
        from_attributes = True


class QuizResponseLegacy(BaseModel):
    """Legacy full response schema for a quiz."""
    id: int
    url: str
    title: Optional[str] = None
    summary: Optional[str] = None
    sections: Optional[List[str]] = None
    created_at: datetime
    questions: List[QuestionResponse] = []
    key_entities: List[KeyEntityResponse] = []
    related_topics: List[RelatedTopicResponse] = []

    class Config:
        from_attributes = True


class QuizListItemLegacy(BaseModel):
    """Legacy schema for quiz list items."""
    id: int
    url: str
    title: Optional[str] = None
    created_at: datetime
    question_count: int

    class Config:
        from_attributes = True


class QuizHistoryResponseLegacy(BaseModel):
    """Legacy response schema for quiz history list."""
    total: int
    page: int
    limit: int
    quizzes: List[QuizListItemLegacy]

    class Config:
        from_attributes = True


# ========== Error Response ==========

class ErrorDetail(BaseModel):
    """Error detail schema."""
    code: str
    message: str
    details: Optional[str] = None
    suggestion: Optional[str] = None


class ErrorResponse(BaseModel):
    """Error response schema."""
    error: ErrorDetail
