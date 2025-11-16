"""
Database models for quiz application.
Uses JSON storage for complete quiz data instead of relational tables.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base
import json
from typing import Dict, List, Optional
from datetime import datetime


class Quiz(Base):
    """
    Quiz table storing complete quiz data as JSON.

    The quiz_data JSON field contains:
    {
        "id": int,
        "url": str,
        "title": str,
        "summary": str,
        "key_entities": {
            "people": [str],
            "organizations": [str],
            "locations": [str]
        },
        "sections": [str],
        "quiz": [
            {
                "question": str,
                "options": [str],
                "answer": str,
                "difficulty": str,
                "explanation": str
            }
        ],
        "related_topics": [str]
    }
    """
    __tablename__ = "quizzes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    url = Column(Text, nullable=False, unique=True, index=True)
    title = Column(String(500), nullable=True)
    quiz_data = Column(JSON, nullable=False)  # Complete quiz data as JSON
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Quiz(id={self.id}, title='{self.title}')>"

    @property
    def summary(self) -> Optional[str]:
        """Get summary from quiz_data."""
        return self.quiz_data.get('summary')

    @property
    def sections(self) -> Optional[List[str]]:
        """Get sections from quiz_data."""
        return self.quiz_data.get('sections', [])

    @property
    def key_entities(self) -> Dict[str, List[str]]:
        """Get key entities from quiz_data."""
        return self.quiz_data.get('key_entities', {})

    @property
    def questions(self) -> List[Dict]:
        """Get questions from quiz_data."""
        return self.quiz_data.get('quiz', [])

    @property
    def related_topics(self) -> List[str]:
        """Get related topics from quiz_data."""
        return self.quiz_data.get('related_topics', [])
