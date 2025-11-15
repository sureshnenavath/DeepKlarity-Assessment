"""
Utility functions for common operations.
"""

import re
from typing import List


def truncate_text(text: str, max_tokens: int = 4000) -> str:
    """
    Truncate text to approximate token limit.
    Rough estimate: 1 token ≈ 4 characters.
    
    Args:
        text: Text to truncate
        max_tokens: Maximum number of tokens
        
    Returns:
        Truncated text
    """
    max_chars = max_tokens * 4
    if len(text) <= max_chars:
        return text
    
    # Truncate and try to end at a sentence
    truncated = text[:max_chars]
    last_period = truncated.rfind('.')
    
    if last_period > max_chars * 0.8:  # If we can find a period in the last 20%
        return truncated[:last_period + 1]
    
    return truncated + "..."


def extract_sections_list(sections: List[dict]) -> List[str]:
    """
    Extract list of section headings from sections data.
    
    Args:
        sections: List of section dictionaries
        
    Returns:
        List of section heading strings
    """
    return [section['heading'] for section in sections if section.get('heading')]


def validate_question_format(question_data: dict) -> bool:
    """
    Validate that question data has the correct format.
    
    Args:
        question_data: Dictionary containing question information
        
    Returns:
        True if valid
        
    Raises:
        ValueError: If format is invalid
    """
    required_fields = ['question', 'options', 'answer', 'difficulty', 'explanation']
    
    for field in required_fields:
        if field not in question_data:
            raise ValueError(f"Missing required field: {field}")
    
    # Validate options
    if not isinstance(question_data['options'], list) or len(question_data['options']) != 4:
        raise ValueError("Options must be a list of exactly 4 items")
    
    # Validate answer
    if question_data['answer'] not in ['A', 'B', 'C', 'D']:
        raise ValueError("Answer must be A, B, C, or D")
    
    # Validate difficulty
    if question_data['difficulty'] not in ['easy', 'medium', 'hard']:
        raise ValueError("Difficulty must be easy, medium, or hard")
    
    return True


def format_options_for_storage(options: List[str]) -> dict:
    """
    Convert options list to dictionary format for database storage.
    
    Args:
        options: List of 4 option strings
        
    Returns:
        Dictionary with keys option_a, option_b, option_c, option_d
    """
    if len(options) != 4:
        raise ValueError("Must provide exactly 4 options")
    
    return {
        'option_a': options[0],
        'option_b': options[1],
        'option_c': options[2],
        'option_d': options[3]
    }


def sanitize_url(url: str) -> str:
    """
    Sanitize and normalize URL.
    
    Args:
        url: URL to sanitize
        
    Returns:
        Sanitized URL
    """
    # Remove trailing slash
    url = url.rstrip('/')
    
    # Remove fragment
    if '#' in url:
        url = url.split('#')[0]
    
    return url.strip()
