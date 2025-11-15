"""
Database models for quiz application.
Defines SQLAlchemy ORM models for quizzes, questions, entities, and related topics.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base
import enum


class EntityType(str, enum.Enum):
    """Enum for entity types."""
    PEOPLE = "people"
    ORGANIZATIONS = "organizations"
    LOCATIONS = "locations"


class DifficultyLevel(str, enum.Enum):
    """Enum for question difficulty levels."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class Quiz(Base):
    """
    Main quiz table storing scraped article information.
    
    Attributes:
        id: Primary key
        url: Source URL of the article
        title: Title of the article
        summary: AI-generated summary
        sections: JSON array of section titles from the article
        created_at: Timestamp when quiz was created
        updated_at: Timestamp when quiz was last updated
    """
    __tablename__ = "quizzes"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    url = Column(Text, nullable=False, unique=True, index=True)
    title = Column(String(500), nullable=True)
    summary = Column(Text, nullable=True)
    sections = Column(JSON, nullable=True)  # Array of section titles
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    questions = relationship("Question", back_populates="quiz", cascade="all, delete-orphan")
    key_entities = relationship("KeyEntity", back_populates="quiz", cascade="all, delete-orphan")
    related_topics = relationship("RelatedTopic", back_populates="quiz", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Quiz(id={self.id}, title='{self.title}')>"


class Question(Base):
    """
    Questions table storing individual quiz questions.
    
    Attributes:
        id: Primary key
        quiz_id: Foreign key to Quiz
        question_text: The question text
        option_a, option_b, option_c, option_d: Answer options
        correct_answer: Letter of correct answer (A, B, C, or D)
        difficulty: Question difficulty level
        explanation: Explanation of the correct answer
        section_reference: Reference to article section (optional)
    """
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False)
    question_text = Column(Text, nullable=False)
    option_a = Column(Text, nullable=False)
    option_b = Column(Text, nullable=False)
    option_c = Column(Text, nullable=False)
    option_d = Column(Text, nullable=False)
    correct_answer = Column(String(1), nullable=False)  # 'A', 'B', 'C', or 'D'
    difficulty = Column(Enum(DifficultyLevel), nullable=False)
    explanation = Column(Text, nullable=True)
    section_reference = Column(String(255), nullable=True)
    
    # Relationship
    quiz = relationship("Quiz", back_populates="questions")
    
    def __repr__(self):
        return f"<Question(id={self.id}, difficulty='{self.difficulty}')>"


class KeyEntity(Base):
    """
    Key entities extracted from the article.
    
    Attributes:
        id: Primary key
        quiz_id: Foreign key to Quiz
        entity_type: Type of entity (people, organizations, locations)
        entity_name: Name of the entity
    """
    __tablename__ = "key_entities"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False)
    entity_type = Column(Enum(EntityType), nullable=False)
    entity_name = Column(String(255), nullable=False)
    
    # Relationship
    quiz = relationship("Quiz", back_populates="key_entities")
    
    def __repr__(self):
        return f"<KeyEntity(type='{self.entity_type}', name='{self.entity_name}')>"


class RelatedTopic(Base):
    """
    Related topics suggested for further learning.
    
    Attributes:
        id: Primary key
        quiz_id: Foreign key to Quiz
        topic_name: Name of the related topic
        topic_url: Optional URL for the topic
    """
    __tablename__ = "related_topics"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False)
    topic_name = Column(String(255), nullable=False)
    topic_url = Column(Text, nullable=True)
    
    # Relationship
    quiz = relationship("Quiz", back_populates="related_topics")
    
    def __repr__(self):
        return f"<RelatedTopic(name='{self.topic_name}')>"
