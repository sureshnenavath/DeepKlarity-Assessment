"""
LLM service for interacting with OpenAI API.
Handles quiz generation, entity extraction, and summary generation.
"""

from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.output_parsers import JsonOutputParser
from typing import Dict, List, Optional
import json
import os
from ..config import settings
from ..utils.helpers import truncate_text


class LLMService:
    """Service for interacting with Google Gemini LLM."""
    
    def __init__(self):
        """Initialize the LLM service with OpenAI model."""
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not found in environment variables")

        model_name = settings.LLM_MODEL
        if model_name in {"gemini-pro", "models/gemini-pro", "gemini-1.5-flash"}:
            # Fallback to GPT-4o mini if old Gemini models are specified
            model_name = "gpt-4o-mini"

        self.llm = ChatOpenAI(
            model=model_name,
            temperature=settings.LLM_TEMPERATURE,
            openai_api_key=settings.OPENAI_API_KEY
        )
        
        # Load prompt templates
        backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.prompts_dir = os.path.join(backend_dir, 'prompts')
        self._load_prompts()
    
    def _load_prompts(self):
        """Load all prompt templates from files."""
        # Main quiz generation prompt
        main_prompt_path = os.path.join(self.prompts_dir, 'main_prompt.txt')
        with open(main_prompt_path, 'r', encoding='utf-8') as f:
            self.quiz_prompt_template = f.read()
        
        # Entity extraction prompt
        entity_prompt_path = os.path.join(
            self.prompts_dir, 'sub_prompts', 'entity_extraction.txt'
        )
        with open(entity_prompt_path, 'r', encoding='utf-8') as f:
            self.entity_prompt_template = f.read()
        
        # Summary generation prompt
        summary_prompt_path = os.path.join(
            self.prompts_dir, 'sub_prompts', 'summary_generation.txt'
        )
        with open(summary_prompt_path, 'r', encoding='utf-8') as f:
            self.summary_prompt_template = f.read()
        
        # Related topics prompt
        topics_prompt_path = os.path.join(
            self.prompts_dir, 'sub_prompts', 'related_topics.txt'
        )
        with open(topics_prompt_path, 'r', encoding='utf-8') as f:
            self.topics_prompt_template = f.read()
    
    def generate_quiz(
        self, 
        title: str, 
        content: str, 
        num_questions: int = 8
    ) -> List[Dict]:
        """
        Generate quiz questions from article content.
        
        Args:
            title: Article title
            content: Article text content
            num_questions: Number of questions to generate
            
        Returns:
            List of question dictionaries
            
        Raises:
            Exception: If generation fails
        """
        # Truncate content to fit context window
        truncated_content = truncate_text(content, max_tokens=3500)
        
        # Create prompt
        prompt = self.quiz_prompt_template.format(
            title=title,
            content=truncated_content,
            num_questions=num_questions
        )
        
        # Invoke LLM with retry logic
        for attempt in range(3):
            try:
                response = self.llm.invoke(prompt)
                
                # Parse JSON response
                result = self._parse_json_response(response.content)
                
                # Validate and return questions
                if 'quiz' in result and isinstance(result['quiz'], list):
                    questions = result['quiz'][:num_questions]
                    
                    # Validate each question
                    for q in questions:
                        self._validate_question(q)
                    
                    return questions
                else:
                    raise ValueError("Invalid quiz format in response")
                    
            except Exception as e:
                if attempt == 2:
                    raise Exception(f"Failed to generate quiz after 3 attempts: {str(e)}")
                continue
        
        raise Exception("Failed to generate quiz")
    
    def extract_entities(self, title: str, content: str) -> Dict[str, List[str]]:
        """
        Extract key entities from article content.
        
        Args:
            title: Article title
            content: Article text content
            
        Returns:
            Dictionary with people, organizations, and locations
        """
        # Truncate content
        truncated_content = truncate_text(content, max_tokens=3500)
        
        # Create prompt
        prompt = self.entity_prompt_template.format(
            title=title,
            content=truncated_content
        )
        
        # Invoke LLM with retry logic
        for attempt in range(3):
            try:
                response = self.llm.invoke(prompt)
                result = self._parse_json_response(response.content)
                
                # Validate structure
                if all(key in result for key in ['people', 'organizations', 'locations']):
                    return {
                        'people': result.get('people', [])[:10],
                        'organizations': result.get('organizations', [])[:10],
                        'locations': result.get('locations', [])[:10]
                    }
                else:
                    raise ValueError("Invalid entity extraction format")
                    
            except Exception as e:
                if attempt == 2:
                    # Return empty structure on failure
                    return {
                        'people': [],
                        'organizations': [],
                        'locations': []
                    }
                continue
        
        return {'people': [], 'organizations': [], 'locations': []}
    
    def generate_summary(self, title: str, content: str) -> str:
        """
        Generate article summary.
        
        Args:
            title: Article title
            content: Article text content
            
        Returns:
            Summary text
        """
        # Truncate content
        truncated_content = truncate_text(content, max_tokens=3500)
        
        # Create prompt
        prompt = self.summary_prompt_template.format(
            title=title,
            content=truncated_content
        )
        
        # Invoke LLM
        for attempt in range(3):
            try:
                response = self.llm.invoke(prompt)
                result = self._parse_json_response(response.content)
                
                if 'summary' in result:
                    return result['summary']
                else:
                    raise ValueError("Invalid summary format")
                    
            except Exception as e:
                if attempt == 2:
                    # Return simple summary on failure
                    return f"An article about {title}."
                continue
        
        return f"An article about {title}."
    
    def generate_related_topics(
        self, 
        title: str, 
        content: str, 
        entities: Dict[str, List[str]]
    ) -> List[str]:
        """
        Generate related topics for further learning.
        
        Args:
            title: Article title
            content: Article text content
            entities: Extracted entities
            
        Returns:
            List of related topic strings
        """
        # Truncate content
        truncated_content = truncate_text(content, max_tokens=2000)
        
        # Format entities for prompt
        entities_str = f"People: {', '.join(entities.get('people', [])[:5])}\n"
        entities_str += f"Organizations: {', '.join(entities.get('organizations', [])[:5])}\n"
        entities_str += f"Locations: {', '.join(entities.get('locations', [])[:5])}"
        
        # Create prompt
        prompt = self.topics_prompt_template.format(
            title=title,
            content=truncated_content,
            entities=entities_str
        )
        
        # Invoke LLM
        for attempt in range(3):
            try:
                response = self.llm.invoke(prompt)
                result = self._parse_json_response(response.content)
                
                if 'related_topics' in result:
                    return result['related_topics'][:8]
                else:
                    raise ValueError("Invalid topics format")
                    
            except Exception as e:
                if attempt == 2:
                    return []
                continue
        
        return []
    
    def _parse_json_response(self, response_text: str) -> Dict:
        """
        Parse JSON from LLM response.
        
        Args:
            response_text: Raw response from LLM
            
        Returns:
            Parsed JSON dictionary
        """
        # Try direct JSON parsing
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            pass
        
        # Try to extract JSON from markdown code blocks
        if '```json' in response_text:
            start = response_text.find('```json') + 7
            end = response_text.find('```', start)
            json_str = response_text[start:end].strip()
            return json.loads(json_str)
        
        # Try to extract JSON between curly braces
        if '{' in response_text and '}' in response_text:
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            json_str = response_text[start:end]
            return json.loads(json_str)
        
        raise ValueError("Could not parse JSON from response")
    
    def _validate_question(self, question: Dict) -> bool:
        """
        Validate question structure.
        
        Args:
            question: Question dictionary
            
        Returns:
            True if valid
            
        Raises:
            ValueError: If invalid
        """
        required_fields = ['question', 'options', 'answer', 'difficulty', 'explanation']
        
        for field in required_fields:
            if field not in question:
                raise ValueError(f"Missing field: {field}")
        
        if not isinstance(question['options'], list) or len(question['options']) != 4:
            raise ValueError("Options must be a list of 4 items")
        
        if question['answer'] not in ['A', 'B', 'C', 'D']:
            raise ValueError("Answer must be A, B, C, or D")
        
        if question['difficulty'] not in ['easy', 'medium', 'hard']:
            raise ValueError("Difficulty must be easy, medium, or hard")
        
        return True


# Create singleton instance
llm_service = LLMService()
