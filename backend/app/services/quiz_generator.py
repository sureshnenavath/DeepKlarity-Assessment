"""
Quiz generation service that orchestrates scraping, LLM, and database operations.
"""

from sqlalchemy.orm import Session
from typing import Dict, List, Optional
from ..models.quiz import Quiz, Question, KeyEntity, RelatedTopic, DifficultyLevel, EntityType
from ..schemas.quiz import QuizResponse
from .scraper import scraper, ScraperError
from .llm_service import llm_service
from ..utils.helpers import extract_sections_list, format_options_for_storage, sanitize_url


class QuizGenerationError(Exception):
    """Custom exception for quiz generation errors."""
    pass


class QuizGeneratorService:
    """Service for generating quizzes from URLs."""
    
    def generate_quiz(self, db: Session, url: str, num_questions: int = 8) -> Quiz:
        """
        Generate a complete quiz from a URL.
        
        Args:
            db: Database session
            url: Article URL
            num_questions: Number of questions to generate
            
        Returns:
            Created Quiz object
            
        Raises:
            QuizGenerationError: If generation fails
        """
        try:
            # Sanitize URL
            url = sanitize_url(url)
            
            # Check for duplicate
            existing_quiz = db.query(Quiz).filter(Quiz.url == url).first()
            if existing_quiz:
                return existing_quiz
            
            # Step 1: Scrape content
            try:
                scraped_data = scraper.scrape_url(url)
            except ScraperError as e:
                raise QuizGenerationError(f"Scraping failed: {str(e)}")
            
            title = scraped_data['title']
            full_text = scraped_data['full_text']
            sections = scraped_data['sections']
            
            # Step 2: Generate summary
            summary = llm_service.generate_summary(title, full_text)
            
            # Step 3: Extract entities
            entities = llm_service.extract_entities(title, full_text)
            
            # Step 4: Generate quiz questions
            try:
                questions_data = llm_service.generate_quiz(title, full_text, num_questions)
            except Exception as e:
                raise QuizGenerationError(f"Quiz generation failed: {str(e)}")
            
            # Step 5: Generate related topics
            related_topics_list = llm_service.generate_related_topics(title, full_text, entities)
            
            # Step 6: Save to database
            quiz = self._save_to_database(
                db=db,
                url=url,
                title=title,
                summary=summary,
                sections=sections,
                questions_data=questions_data,
                entities=entities,
                related_topics=related_topics_list
            )
            
            return quiz
            
        except QuizGenerationError:
            raise
        except Exception as e:
            raise QuizGenerationError(f"Unexpected error: {str(e)}")
    
    def _save_to_database(
        self,
        db: Session,
        url: str,
        title: str,
        summary: str,
        sections: List[Dict],
        questions_data: List[Dict],
        entities: Dict[str, List[str]],
        related_topics: List[str]
    ) -> Quiz:
        """
        Save quiz data to database.
        
        Args:
            db: Database session
            url: Article URL
            title: Article title
            summary: Generated summary
            sections: List of article sections
            questions_data: List of question dictionaries
            entities: Extracted entities dictionary
            related_topics: List of related topic strings
            
        Returns:
            Created Quiz object
        """
        try:
            # Create quiz object
            quiz = Quiz(
                url=url,
                title=title,
                summary=summary,
                sections=extract_sections_list(sections)
            )
            
            db.add(quiz)
            db.flush()  # Get quiz.id without committing
            
            # Add questions
            for q_data in questions_data:
                options = format_options_for_storage(q_data['options'])
                
                question = Question(
                    quiz_id=quiz.id,
                    question_text=q_data['question'],
                    option_a=options['option_a'],
                    option_b=options['option_b'],
                    option_c=options['option_c'],
                    option_d=options['option_d'],
                    correct_answer=q_data['answer'],
                    difficulty=DifficultyLevel(q_data['difficulty']),
                    explanation=q_data.get('explanation', ''),
                    section_reference=q_data.get('section_reference')
                )
                db.add(question)
            
            # Add entities
            for entity_type, entity_names in entities.items():
                for name in entity_names:
                    if name:  # Skip empty names
                        entity = KeyEntity(
                            quiz_id=quiz.id,
                            entity_type=EntityType(entity_type),
                            entity_name=name
                        )
                        db.add(entity)
            
            # Add related topics
            for topic_name in related_topics:
                if topic_name:  # Skip empty topics
                    topic = RelatedTopic(
                        quiz_id=quiz.id,
                        topic_name=topic_name
                    )
                    db.add(topic)
            
            # Commit transaction
            db.commit()
            db.refresh(quiz)
            
            return quiz
            
        except Exception as e:
            db.rollback()
            raise QuizGenerationError(f"Database error: {str(e)}")
    
    def get_quiz_by_id(self, db: Session, quiz_id: int) -> Optional[Quiz]:
        """
        Get quiz by ID with all relationships loaded.
        
        Args:
            db: Database session
            quiz_id: Quiz ID
            
        Returns:
            Quiz object or None
        """
        return db.query(Quiz).filter(Quiz.id == quiz_id).first()
    
    def get_all_quizzes(
        self, 
        db: Session, 
        page: int = 1, 
        limit: int = 20,
        search: Optional[str] = None
    ) -> tuple[List[Quiz], int]:
        """
        Get paginated list of quizzes.
        
        Args:
            db: Database session
            page: Page number (1-indexed)
            limit: Items per page
            search: Optional search query
            
        Returns:
            Tuple of (quiz list, total count)
        """
        query = db.query(Quiz)
        
        # Apply search filter
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                (Quiz.title.ilike(search_term)) | 
                (Quiz.url.ilike(search_term))
            )
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * limit
        quizzes = query.order_by(Quiz.created_at.desc()).offset(offset).limit(limit).all()
        
        return quizzes, total


# Create singleton instance
quiz_service = QuizGeneratorService()
