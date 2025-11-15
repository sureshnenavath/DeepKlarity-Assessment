"""Schemas package initialization."""

from .quiz import (
    QuizGenerateRequest,
    QuizResponse,
    QuestionResponse,
    KeyEntityResponse,
    RelatedTopicResponse,
    QuizListItem,
    QuizHistoryResponse,
    ErrorResponse,
    ErrorDetail,
    DifficultyLevel,
    EntityType
)

__all__ = [
    "QuizGenerateRequest",
    "QuizResponse",
    "QuestionResponse",
    "KeyEntityResponse",
    "RelatedTopicResponse",
    "QuizListItem",
    "QuizHistoryResponse",
    "ErrorResponse",
    "ErrorDetail",
    "DifficultyLevel",
    "EntityType"
]
