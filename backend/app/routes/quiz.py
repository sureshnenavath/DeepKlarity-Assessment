"""
FastAPI routes for quiz operations.
"""

import math

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from ..database import get_db
from ..schemas.quiz import (
    QuizGenerateRequest,
    QuizResponse,
    QuizHistoryResponse,
    QuizListItem,
    ErrorResponse,
    ErrorDetail
)
from ..services.quiz_generator import quiz_service, QuizGenerationError
from ..services.scraper import ScraperError

router = APIRouter()


@router.post("/quiz/generate", response_model=QuizResponse)
async def generate_quiz(
    request: QuizGenerateRequest,
    db: Session = Depends(get_db)
):
    """
    Generate a new quiz from a URL.

    Args:
        request: Quiz generation request with URL and optional num_questions
        db: Database session

    Returns:
        Complete quiz with questions, entities, and related topics in JSON format

    Raises:
        HTTPException: If generation fails
    """
    try:
        # Generate quiz
        quiz = quiz_service.generate_quiz(
            db=db,
            url=request.url,
            num_questions=request.num_questions
        )

        # Format response using the JSON structure
        response_data = {
            "id": quiz.id,
            "url": quiz.url,
            "title": quiz.title,
            "summary": quiz.quiz_data.get("summary", ""),
            "key_entities": quiz.quiz_data.get("key_entities", {}),
            "sections": quiz.quiz_data.get("sections", []),
            "quiz": quiz.quiz_data.get("quiz", []),
            "related_topics": quiz.quiz_data.get("related_topics", []),
            "created_at": quiz.created_at
        }

        return response_data
        
    except ScraperError as e:
        print(f"ScraperError: {str(e)}")  # Debug logging
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "code": "SCRAPING_FAILED",
                    "message": "Failed to scrape the article",
                    "details": str(e),
                    "suggestion": "Please verify the URL is correct and accessible"
                }
            }
        )
    except QuizGenerationError as e:
        error_msg = str(e)
        print(f"QuizGenerationError: {error_msg}")  # Debug logging
        
        if "too short" in error_msg.lower():
            code = "CONTENT_TOO_SHORT"
        elif "quiz generation failed" in error_msg.lower():
            code = "LLM_GENERATION_FAILED"
        else:
            code = "GENERATION_ERROR"
        
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "code": code,
                    "message": "Failed to generate quiz",
                    "details": error_msg,
                    "suggestion": "Try a different article or check if it has sufficient content"
                }
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred",
                    "details": str(e),
                    "suggestion": "Please try again later"
                }
            }
        )


@router.get("/quiz/history", response_model=QuizHistoryResponse)
async def get_quiz_history(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    search: Optional[str] = Query(default=None),
    db: Session = Depends(get_db)
):
    """
    Get paginated quiz history.
    
    Args:
        page: Page number (1-indexed)
        limit: Items per page
        search: Optional search query for title/URL
        db: Database session
        
    Returns:
        Paginated list of quizzes with metadata
    """
    try:
        quizzes, total = quiz_service.get_all_quizzes(
            db=db,
            page=page,
            limit=limit,
            search=search
        )
        
        # Format quiz list items
        quiz_items = []
        for quiz in quizzes:
            quiz_items.append(
                QuizListItem(
                    id=quiz.id,
                    url=quiz.url,
                    title=quiz.title,
                    summary=quiz.quiz_data.get("summary", ""),
                    question_count=len(quiz.quiz_data.get("quiz", [])),
                    created_at=quiz.created_at
                )
            )
        
        total_pages = math.ceil(total / limit) if total else 0
        return QuizHistoryResponse(
            total=total,
            page=page,
            limit=limit,
            total_pages=total_pages,
            quizzes=quiz_items
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "Failed to fetch quiz history",
                    "details": str(e)
                }
            }
        )


@router.get("/quiz/{quiz_id}", response_model=QuizResponse)
async def get_quiz_by_id(
    quiz_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific quiz by ID.
    
    Args:
        quiz_id: Quiz ID
        db: Database session
        
    Returns:
        Complete quiz details
        
    Raises:
        HTTPException: If quiz not found
    """
    quiz = quiz_service.get_quiz_by_id(db, quiz_id)

    if not quiz:
        raise HTTPException(
            status_code=404,
            detail={
                "error": {
                    "code": "QUIZ_NOT_FOUND",
                    "message": f"Quiz with ID {quiz_id} not found",
                    "suggestion": "Please check the quiz ID"
                }
            }
        )

    # Format response using the JSON structure
    response_data = {
        "id": quiz.id,
        "url": quiz.url,
        "title": quiz.title,
        "summary": quiz.quiz_data.get("summary", ""),
        "key_entities": quiz.quiz_data.get("key_entities", {}),
        "sections": quiz.quiz_data.get("sections", []),
        "quiz": quiz.quiz_data.get("quiz", []),
        "related_topics": quiz.quiz_data.get("related_topics", []),
        "created_at": quiz.created_at
    }

    return response_data


@router.delete("/quiz/{quiz_id}")
async def delete_quiz(
    quiz_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a quiz by ID.
    
    Args:
        quiz_id: Quiz ID
        db: Database session
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If quiz not found
    """
    quiz = quiz_service.get_quiz_by_id(db, quiz_id)
    
    if not quiz:
        raise HTTPException(
            status_code=404,
            detail={
                "error": {
                    "code": "QUIZ_NOT_FOUND",
                    "message": f"Quiz with ID {quiz_id} not found"
                }
            }
        )
    
    try:
        db.delete(quiz)
        db.commit()
        
        return {
            "message": f"Quiz {quiz_id} deleted successfully"
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "code": "DELETE_FAILED",
                    "message": "Failed to delete quiz",
                    "details": str(e)
                }
            }
        )
