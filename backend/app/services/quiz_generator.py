"""
Quiz generation service that orchestrates scraping, LLM, and database operations.
Stores complete quiz data as JSON instead of relational tables.
"""

from sqlalchemy.orm import Session
from typing import Dict, List, Optional

from ..models.quiz import Quiz
from .scraper import scraper, ScraperError
from .llm_service import llm_service
from ..utils.helpers import sanitize_url, extract_sections_list


class QuizGenerationError(Exception):
    """Custom exception for quiz generation errors."""
    pass


class QuizGeneratorService:
    """Service that builds quizzes as JSON blobs from article URLs."""

    def generate_quiz(self, db: Session, url: str, num_questions: int = 8) -> Quiz:
        """Generate a quiz for the URL and persist it."""
        try:
            normalized_url = sanitize_url(url)

            existing_quiz = db.query(Quiz).filter(Quiz.url == normalized_url).first()
            if existing_quiz:
                return existing_quiz

            scraped_data = self._scrape_content(normalized_url)
            questions = self._generate_questions(scraped_data, num_questions)
            entities = self._extract_entities(scraped_data)
            summary = self._generate_summary(scraped_data)
            related_topics = self._generate_related_topics(scraped_data, entities)
            quiz_json = self._build_quiz_json(
                normalized_url,
                scraped_data,
                questions,
                entities,
                summary,
                related_topics
            )

            quiz = Quiz(
                url=normalized_url,
                title=scraped_data.get('title', ''),
                quiz_data=quiz_json
            )
            db.add(quiz)
            db.commit()
            db.refresh(quiz)

            return quiz

        except QuizGenerationError:
            db.rollback()
            raise
        except Exception as exc:
            db.rollback()
            raise QuizGenerationError(f"Quiz generation failed: {str(exc)}")

    def _scrape_content(self, url: str) -> Dict:
        try:
            return scraper.scrape_url(url)
        except ScraperError as exc:
            raise QuizGenerationError(f"Scraping failed: {str(exc)}")
        except Exception as exc:
            raise QuizGenerationError(f"Unexpected scraping error: {str(exc)}")

    def _generate_questions(self, scraped_data: Dict, num_questions: int) -> List[Dict]:
        try:
            return llm_service.generate_quiz(
                title=scraped_data.get('title', ''),
                content=scraped_data.get('full_text', ''),
                num_questions=num_questions
            )
        except Exception as exc:
            raise QuizGenerationError(f"LLM quiz generation failed: {str(exc)}")

    def _extract_entities(self, scraped_data: Dict) -> Dict[str, List[str]]:
        try:
            return llm_service.extract_entities(
                title=scraped_data.get('title', ''),
                content=scraped_data.get('full_text', '')
            )
        except Exception:
            return {
                'people': [],
                'organizations': [],
                'locations': []
            }

    def _generate_summary(self, scraped_data: Dict) -> str:
        try:
            return llm_service.generate_summary(
                title=scraped_data.get('title', ''),
                content=scraped_data.get('full_text', '')
            )
        except Exception:
            return ""

    def _generate_related_topics(self, scraped_data: Dict, entities: Dict[str, List[str]]) -> List[str]:
        try:
            return llm_service.generate_related_topics(
                title=scraped_data.get('title', ''),
                content=scraped_data.get('full_text', ''),
                entities=entities
            )
        except Exception:
            return []

    def _build_quiz_json(
        self,
        url: str,
        scraped_data: Dict,
        questions: List[Dict],
        entities: Dict[str, List[str]],
        summary: str,
        related_topics: List[str]
    ) -> Dict:
        return {
            "url": url,
            "title": scraped_data.get('title', ''),
            "summary": summary,
            "key_entities": entities,
            "sections": extract_sections_list(scraped_data.get('sections', [])),
            "quiz": questions,
            "related_topics": related_topics
        }

    def get_quiz_by_id(self, db: Session, quiz_id: int) -> Optional[Quiz]:
        return db.query(Quiz).filter(Quiz.id == quiz_id).first()

    def get_all_quizzes(
        self,
        db: Session,
        page: int = 1,
        limit: int = 20,
        search: Optional[str] = None
    ) -> tuple[List[Quiz], int]:
        query = db.query(Quiz)
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                (Quiz.title.ilike(search_term)) | (Quiz.url.ilike(search_term))
            )

        total = query.count()
        offset = (page - 1) * limit
        quizzes = query.order_by(Quiz.created_at.desc()).offset(offset).limit(limit).all()

        return quizzes, total


quiz_service = QuizGeneratorService()
