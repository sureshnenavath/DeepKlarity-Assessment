# DeepKlarity AI Quiz Generator - Complete Implementation Plan

## Table of Contents
1. [Project Overview](#project-overview)
2. [System Architecture](#system-architecture)
3. [Phase 1: Environment Setup](#phase-1-environment-setup)
4. [Phase 2: Database Design](#phase-2-database-design)
5. [Phase 3: Backend Development](#phase-3-backend-development)
6. [Phase 4: LLM Integration & Prompt Engineering](#phase-4-llm-integration--prompt-engineering)
7. [Phase 5: Frontend Development](#phase-5-frontend-development)
8. [Phase 6: Testing & Optimization](#phase-6-testing--optimization)
9. [Phase 7: Documentation & Submission](#phase-7-documentation--submission)

---

## Project Overview

### Technology Stack
- **Backend**: FastAPI (Python 3.9+)
- **Database**: PostgreSQL
- **LLM**: Google Gemini API (Free Tier)
- **Scraping**: BeautifulSoup4, requests
- **LLM Framework**: LangChain
- **Frontend**: React.js with Tailwind CSS
- **API Testing**: Postman/Thunder Client

### Key Features
1. URL-based content scraping (Wikipedia and other websites)
2. AI-powered quiz generation with explanations
3. Entity extraction (people, organizations, locations)
4. Quiz history with searchable database
5. Optional "Take Quiz" interactive mode

---

## System Architecture

### High-Level Flow
```
User Input (URL) 
  → Frontend (React)
    → Backend API (FastAPI)
      → Web Scraper (BeautifulSoup)
        → Content Processing
          → LLM Integration (Gemini via LangChain)
            → Quiz Generation
              → Database Storage (PostgreSQL)
                → Response to Frontend
                  → Display Quiz
```

### API Endpoints Structure
```
POST   /api/quiz/generate        - Generate new quiz from URL
GET    /api/quiz/history         - Get all past quizzes
GET    /api/quiz/{id}            - Get specific quiz details
DELETE /api/quiz/{id}            - Delete quiz (optional)
GET    /api/quiz/validate-url    - Validate URL before processing
```

---

## Phase 1: Environment Setup

### Step 1.1: Backend Environment
1. Create project directory structure:
   ```
   deepklarity-quiz/
   ├── backend/
   │   ├── app/
   │   │   ├── __init__.py
   │   │   ├── main.py
   │   │   ├── config.py
   │   │   ├── database.py
   │   │   ├── models/
   │   │   ├── schemas/
   │   │   ├── services/
   │   │   │   ├── scraper.py
   │   │   │   ├── llm_service.py
   │   │   │   ├── entity_extractor.py
   │   │   │   └── quiz_generator.py
   │   │   ├── routes/
   │   │   └── utils/
   │   ├── prompts/
   │   │   ├── main_prompt.txt
   │   │   └── sub_prompts/
   │   ├── requirements.txt
   │   └── .env
   ├── frontend/
   ├── sample_data/
   └── README.md
   ```

2. Install Python dependencies:
   - fastapi
   - uvicorn[standard]
   - sqlalchemy
   - psycopg2-binary
   - beautifulsoup4
   - requests
   - langchain
   - langchain-google-genai
   - python-dotenv
   - pydantic
   - aiohttp

### Step 1.2: Database Setup
1. Install PostgreSQL locally or use cloud service (ElephantSQL, Neon)
2. Create database: `deepklarity_quiz_db`
3. Create database user with appropriate permissions
4. Store credentials in `.env` file

### Step 1.3: API Keys
1. Get Google Gemini API key from Google AI Studio
2. Store in `.env`:
   ```
   GEMINI_API_KEY=your_key_here
   DATABASE_URL=postgresql://user:pass@localhost/deepklarity_quiz_db
   ```

### Step 1.4: Frontend Environment
1. Initialize React app using Vite
2. Install dependencies:
   - axios
   - react-router-dom
   - tailwindcss
   - lucide-react (icons)
   - react-modal

---

## Phase 2: Database Design

### Step 2.1: Database Schema

#### Table 1: `quizzes`
```sql
- id (PRIMARY KEY, AUTO_INCREMENT)
- url (TEXT, NOT NULL)
- title (VARCHAR(500))
- summary (TEXT)
- raw_html (TEXT) [OPTIONAL for bonus]
- sections (JSON) - Array of section titles
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)
```

#### Table 2: `key_entities`
```sql
- id (PRIMARY KEY, AUTO_INCREMENT)
- quiz_id (FOREIGN KEY → quizzes.id)
- entity_type (ENUM: 'people', 'organizations', 'locations')
- entity_name (VARCHAR(255))
```

#### Table 3: `questions`
```sql
- id (PRIMARY KEY, AUTO_INCREMENT)
- quiz_id (FOREIGN KEY → quizzes.id)
- question_text (TEXT, NOT NULL)
- option_a (TEXT, NOT NULL)
- option_b (TEXT, NOT NULL)
- option_c (TEXT, NOT NULL)
- option_d (TEXT, NOT NULL)
- correct_answer (VARCHAR(1)) - 'A', 'B', 'C', or 'D'
- difficulty (ENUM: 'easy', 'medium', 'hard')
- explanation (TEXT)
- section_reference (VARCHAR(255)) [OPTIONAL]
```

#### Table 4: `related_topics`
```sql
- id (PRIMARY KEY, AUTO_INCREMENT)
- quiz_id (FOREIGN KEY → quizzes.id)
- topic_name (VARCHAR(255))
- topic_url (TEXT) [OPTIONAL]
```

### Step 2.2: SQLAlchemy Models
Create ORM models corresponding to each table with relationships defined.

---

## Phase 3: Backend Development

### Step 3.1: Core Scraper Service (`scraper.py`)

#### Function: `scrape_url(url: str)`
**Process:**
1. Validate URL format using regex
2. Send GET request with proper headers (User-Agent)
3. Handle HTTP errors (404, 403, timeout)
4. Parse HTML with BeautifulSoup
5. Extract:
   - Page title (from `<title>` or `<h1>`)
   - Main content area (identify `<main>`, `<article>`, or content divs)
   - Section headings (`<h2>`, `<h3>`)
   - Paragraphs and clean text
6. Remove unwanted elements:
   - Navigation bars
   - Footers
   - Sidebars
   - Script tags
   - Style tags
   - Reference links
7. Return structured data:
   ```python
   {
     "title": str,
     "full_text": str,
     "sections": [{"heading": str, "content": str}],
     "word_count": int,
     "raw_html": str (optional)
   }
   ```

#### Special Handling for Wikipedia:
- Extract infobox data
- Remove citation brackets [1], [2]
- Handle special Wikipedia formatting

#### Error Handling:
- Invalid URL format
- Network timeout (set 30s timeout)
- Blocked by robots.txt (respect but inform user)
- Non-200 status codes
- Empty content after scraping

---

### Step 3.2: Entity Extraction Service (`entity_extractor.py`)

#### Function: `extract_entities(text: str, title: str)`
**Process:**
1. Use LLM to identify entities OR use spaCy NER
2. Categorize into:
   - People (PERSON)
   - Organizations (ORG)
   - Locations (GPE, LOC)
3. Filter out generic terms
4. Limit to top 10 most mentioned entities per category
5. Return structured dict:
   ```python
   {
     "people": List[str],
     "organizations": List[str],
     "locations": List[str]
   }
   ```

**Alternative Approach (LLM-based):**
Create a sub-prompt for entity extraction (see Phase 4)

---

### Step 3.3: Database Service (`database.py`)

#### Function: `save_quiz_to_db(quiz_data: dict)`
**Process:**
1. Create transaction
2. Insert into `quizzes` table
3. Get quiz_id
4. Batch insert:
   - key_entities
   - questions
   - related_topics
5. Commit or rollback on error
6. Return complete quiz object with ID

#### Function: `get_all_quizzes()`
Return list of quizzes with basic info (id, url, title, created_at)

#### Function: `get_quiz_by_id(quiz_id: int)`
Return complete quiz with all related data (joins)

#### Function: `check_duplicate_url(url: str)`
Check if URL already exists, return existing quiz_id or None

---

### Step 3.4: FastAPI Routes (`routes/quiz.py`)

#### Endpoint 1: POST `/api/quiz/generate`
**Request Body:**
```json
{
  "url": "https://example.com/article"
}
```

**Process Flow:**
1. Validate URL format
2. Check for duplicate in database (optional: return cached)
3. Call `scrape_url()`
4. Check if content meets minimum requirements (>500 words)
5. Call `extract_entities()`
6. Call `generate_quiz()` (LLM service)
7. Call `generate_related_topics()` (LLM service)
8. Save to database
9. Return JSON response

**Response:** Full quiz object (see sample API output)

**Error Responses:**
- 400: Invalid URL
- 404: URL not accessible
- 500: Scraping/LLM error

#### Endpoint 2: GET `/api/quiz/history`
**Query Parameters:**
- `page` (default: 1)
- `limit` (default: 20)
- `search` (optional: filter by title/url)

**Response:**
```json
{
  "total": 45,
  "page": 1,
  "limit": 20,
  "quizzes": [
    {
      "id": 1,
      "url": "...",
      "title": "...",
      "created_at": "2025-01-15T10:30:00Z",
      "question_count": 8
    }
  ]
}
```

#### Endpoint 3: GET `/api/quiz/{id}`
Return complete quiz details (same structure as generate response)

---

## Phase 4: LLM Integration & Prompt Engineering

### Step 4.1: LangChain Setup

#### Initialize Gemini Model
```python
from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(
    model="gemini-pro",
    temperature=0.3,  # Lower for factual accuracy
    google_api_key=GEMINI_API_KEY
)
```

---

### Step 4.2: Main Prompt for Quiz Generation

**Prompt Template:**
```
MAIN_QUIZ_GENERATION_PROMPT:

You are an expert educational content creator tasked with generating a high-quality quiz based on the provided article content.

ARTICLE TITLE: {title}

ARTICLE CONTENT:
{content}

INSTRUCTIONS:
1. Generate exactly {num_questions} questions based ONLY on the information present in the article
2. Questions must be:
   - Factually accurate and verifiable from the article
   - Clear and unambiguous
   - Diverse in difficulty (mix of easy, medium, hard)
   - Covering different sections/topics from the article
   - Testing comprehension, not just memorization

3. For EACH question provide:
   - Question text (clear and concise)
   - Four plausible options (A, B, C, D)
   - Correct answer (letter: A/B/C/D)
   - Difficulty level (easy/medium/hard)
   - Brief explanation (1-2 sentences) citing which section of the article supports the answer

4. Difficulty Guidelines:
   - Easy: Direct facts explicitly stated in the article
   - Medium: Requires understanding of relationships or concepts
   - Hard: Requires synthesis of multiple pieces of information

5. CRITICAL RULES:
   - DO NOT include information not present in the article
   - DO NOT make assumptions or add external knowledge
   - Ensure all four options are plausible but only one is correct
   - Avoid negative questions (e.g., "Which is NOT...")
   - Vary question types: factual, conceptual, analytical

OUTPUT FORMAT (strict JSON):
{
  "quiz": [
    {
      "question": "string",
      "options": ["A text", "B text", "C text", "D text"],
      "answer": "A" | "B" | "C" | "D",
      "difficulty": "easy" | "medium" | "hard",
      "explanation": "string"
    }
  ]
}

Generate {num_questions} questions now.
```

**Variables:**
- `{title}`: Article title
- `{content}`: Scraped article text (truncated to fit context window if needed)
- `{num_questions}`: 5-10 (user configurable)

---

### Step 4.3: Sub-Prompt 1 - Entity Extraction

**Prompt Template:**
```
ENTITY_EXTRACTION_PROMPT:

Analyze the following article and extract key entities mentioned.

ARTICLE TITLE: {title}

ARTICLE CONTENT:
{content}

TASK:
Extract and categorize the most important entities into three categories:
1. PEOPLE: Names of individuals, historical figures, authors, scientists, etc.
2. ORGANIZATIONS: Companies, institutions, universities, government bodies, etc.
3. LOCATIONS: Countries, cities, regions, buildings, landmarks, etc.

RULES:
- Only extract entities explicitly mentioned in the article
- Include the most frequently mentioned or contextually important entities
- Limit to 10 entities per category
- Use proper capitalization
- Avoid generic terms (e.g., "the company", "the country")

OUTPUT FORMAT (strict JSON):
{
  "people": ["Name 1", "Name 2", ...],
  "organizations": ["Org 1", "Org 2", ...],
  "locations": ["Location 1", "Location 2", ...]
}
```

---

### Step 4.4: Sub-Prompt 2 - Summary Generation

**Prompt Template:**
```
SUMMARY_GENERATION_PROMPT:

Create a concise summary of the following article.

ARTICLE TITLE: {title}

ARTICLE CONTENT:
{content}

TASK:
Write a clear, informative summary that:
- Captures the main topic and key points
- Is 2-4 sentences long
- Focuses on the most important information
- Is written in third person
- Avoids personal opinions or external knowledge

OUTPUT FORMAT (strict JSON):
{
  "summary": "string"
}
```

---

### Step 4.5: Sub-Prompt 3 - Related Topics Generation

**Prompt Template:**
```
RELATED_TOPICS_PROMPT:

Based on the following article, suggest related topics for further learning.

ARTICLE TITLE: {title}

ARTICLE CONTENT:
{content}

KEY ENTITIES:
{entities}

TASK:
Generate 5-8 related topics that:
- Are directly connected to the article's subject matter
- Would be valuable for deeper understanding
- Represent natural extensions or related concepts
- Are broad enough to be searchable topics

RULES:
- Focus on concepts, not specific people or events
- Each topic should be 1-5 words
- Prioritize topics that appeared in the article or are closely related
- Avoid overly generic topics (e.g., "History", "Science")

OUTPUT FORMAT (strict JSON):
{
  "related_topics": ["Topic 1", "Topic 2", ...]
}
```

---

### Step 4.6: Sub-Prompt 4 - Difficulty Assessment

**Embedded in Main Prompt, but logic:**
```
DIFFICULTY_ASSESSMENT_CRITERIA:

EASY:
- Direct factual questions
- Information stated explicitly in one sentence
- Simple who/what/when/where questions
- No inference required

MEDIUM:
- Requires connecting 2-3 pieces of information
- Understanding of relationships or processes
- "Why" or "How" questions
- Moderate inference from context

HARD:
- Synthesis of multiple sections
- Requires understanding of complex relationships
- Analytical or comparative questions
- Higher-order thinking (analyze, evaluate, synthesize)
```

---

### Step 4.7: Prompt Optimization Strategies

#### Content Preprocessing:
1. **Truncation Strategy**: If article > 4000 tokens
   - Prioritize: introduction, conclusion, main sections
   - Remove: references, external links, See Also sections
   
2. **Section-wise Processing** (Bonus):
   - Split large articles into sections
   - Generate 1-2 questions per major section
   - Ensures coverage across entire article

#### Hallucination Prevention:
1. **Grounding Instructions**: 
   - Emphasize "ONLY from article" in prompt
   - Include negative examples in few-shot prompts
   
2. **Post-processing Validation**:
   - Check if answer explanations reference article sections
   - Verify entities exist in scraped content
   
3. **Temperature Settings**:
   - Use low temperature (0.3) for factual accuracy
   - Use higher temperature (0.7) only for creative phrasing

#### Output Parsing:
1. Use LangChain's `JsonOutputParser`
2. Implement retry logic (max 3 attempts)
3. Fallback: manual JSON extraction from text response
4. Validate JSON schema before saving to database

---

### Step 4.8: LangChain Implementation Pattern

```python
# Pseudo-code structure:

def generate_quiz(content: str, title: str, num_questions: int = 8):
    # Step 1: Create prompt
    prompt = PromptTemplate(
        template=MAIN_QUIZ_GENERATION_PROMPT,
        input_variables=["title", "content", "num_questions"]
    )
    
    # Step 2: Create chain
    chain = prompt | llm | JsonOutputParser()
    
    # Step 3: Invoke with retry logic
    for attempt in range(3):
        try:
            result = chain.invoke({
                "title": title,
                "content": truncate_content(content),
                "num_questions": num_questions
            })
            validate_quiz_structure(result)
            return result
        except Exception as e:
            if attempt == 2:
                raise
            continue
```

---

## Phase 5: Frontend Development

### Step 5.1: Project Structure
```
frontend/
├── src/
│   ├── components/
│   │   ├── QuizGenerator.jsx
│   │   ├── QuizDisplay.jsx
│   │   ├── QuizHistory.jsx
│   │   ├── QuizModal.jsx
│   │   ├── QuizTaker.jsx (bonus)
│   │   ├── LoadingSpinner.jsx
│   │   └── ErrorMessage.jsx
│   ├── services/
│   │   └── api.js
│   ├── App.jsx
│   └── main.jsx
├── public/
└── package.json
```

---

### Step 5.2: Tab 1 - Quiz Generator

#### Layout Components:

**1. URL Input Section**
- Text input field (full width)
- "Generate Quiz" button
- Loading indicator during processing
- Error display area

**2. Quiz Display Section**
Displayed after successful generation:

**Header Card:**
- Article title (large font)
- Source URL (clickable link)
- Summary paragraph
- Generation timestamp

**Key Entities Card:**
- Three columns: People | Organizations | Locations
- Each entity as a badge/chip
- Optional: click to search related info

**Sections List Card:**
- Display extracted section headings
- Optional: collapsible list

**Questions Section:**
Display each question as a card:
- Question number and text (bold)
- Difficulty badge (color-coded: green=easy, yellow=medium, red=hard)
- Four options (A-D) with radio buttons (disabled, showing correct answer)
- Correct answer highlighted
- Explanation text (light background)
- Optional: Section reference tag

**Related Topics Card:**
- Display as clickable chips/tags
- Optional: link to Wikipedia or generate new quiz

---

### Step 5.3: Tab 2 - Quiz History

#### Table Component:

**Columns:**
1. ID (auto-increment)
2. Article Title (truncated if long)
3. URL (truncated, show full on hover)
4. Created Date (formatted: "Jan 15, 2025 10:30 AM")
5. Questions Count
6. Actions (Details button)

**Features:**
- Pagination (20 items per page)
- Search bar (filter by title/URL)
- Sort by date (newest first)
- Responsive table (mobile: stack columns)

**Details Button:**
- Opens modal with full quiz display
- Reuses QuizDisplay component from Tab 1
- Close button and overlay click to dismiss

---

### Step 5.4: Bonus - Quiz Taker Mode

#### Interactive Quiz Interface:
1. **Start Screen:**
   - Quiz title and info
   - "Start Quiz" button
   - Option to show/hide timer

2. **Question Screen:**
   - Progress indicator (e.g., "Question 3 of 8")
   - Question text
   - Four clickable options (radio buttons)
   - "Submit Answer" button
   - No explanation visible until submitted

3. **Answer Feedback:**
   - Correct: Green highlight with explanation
   - Incorrect: Red highlight, show correct answer + explanation
   - "Next Question" button

4. **Results Screen:**
   - Score display (e.g., "6/8 - 75%")
   - Breakdown by difficulty
   - List of questions with user's answers
   - "Retake Quiz" button
   - "Back to History" button

---

### Step 5.5: API Integration (`services/api.js`)

#### API Functions:

```javascript
// Pseudo-code structure:

export const generateQuiz = async (url) => {
  // POST request to /api/quiz/generate
  // Handle loading state
  // Handle errors (network, validation, server)
  // Return quiz data
}

export const getQuizHistory = async (page, limit, search) => {
  // GET request to /api/quiz/history
  // Handle pagination params
  // Return list of quizzes
}

export const getQuizById = async (id) => {
  // GET request to /api/quiz/{id}
  // Return single quiz data
}
```

#### Error Handling Strategy:
- Network errors: "Unable to connect to server"
- 400 errors: Display specific validation message
- 404 errors: "Article not found or inaccessible"
- 500 errors: "Server error, please try again"
- Timeout: "Request timed out, article may be too large"

---

### Step 5.6: UI/UX Considerations

#### Design Principles:
1. **Minimal and Clean**: White background, ample spacing
2. **Color Coding**:
   - Easy: Green (#10B981)
   - Medium: Yellow (#F59E0B)
   - Hard: Red (#EF4444)
3. **Typography**: Clear hierarchy (headings, body, labels)
4. **Responsive**: Mobile-first design
5. **Accessibility**: Proper ARIA labels, keyboard navigation

#### Loading States:
- Skeleton screens during data fetch
- Progress indicator for quiz generation
- Disable buttons during processing

#### Empty States:
- Tab 1: Instructions and example URLs
- Tab 2: "No quizzes yet" message with CTA

---

## Phase 6: Testing & Optimization

### Step 6.1: Test Article Categories

Test with diverse content types:

1. **Short Article** (500-1000 words)
   - Example: Wikipedia stub articles
   - Test: Minimum content handling

2. **Medium Article** (1000-3000 words)
   - Example: Standard Wikipedia articles
   - Test: Standard processing

3. **Long Article** (5000+ words)
   - Example: Featured Wikipedia articles
   - Test: Content truncation, processing time

4. **Different Domains**:
   - News articles (non-Wikipedia)
   - Blog posts
   - Educational content sites
   - Test: Scraper robustness

5. **Edge Cases**:
   - Articles with heavy formatting
   - Articles with many images/tables
   - Articles with special characters
   - Multi-language content (if supporting)

---

### Step 6.2: Quiz Quality Validation

#### Manual Review Checklist:
For each generated quiz, verify:

1. **Factual Accuracy**:
   - ✓ All information verifiable from article
   - ✓ No external facts introduced
   - ✓ Correct answers are actually correct

2. **Question Quality**:
   - ✓ Clear and unambiguous phrasing
   - ✓ Diverse question types
   - ✓ Appropriate difficulty distribution (30% easy, 50% medium, 20% hard)
   - ✓ Good distractor options (plausible but incorrect)

3. **Explanations**:
   - ✓ References specific article sections
   - ✓ Concise and clear
   - ✓ Helps learning, not just confirming

4. **Coverage**:
   - ✓ Questions span different article sections
   - ✓ Important topics prioritized
   - ✓ No repetitive questions

---

### Step 6.3: Error Scenario Testing

Test each error case:

1. Invalid URL formats
2. Dead/broken links (404)
3. Blocked by robots.txt
4. Paywalled content
5. Very short articles (<300 words)
6. Articles with no text content (image galleries)
7. Network timeouts
8. Database connection failures
9. LLM API failures/rate limits

Ensure graceful error messages for each.

---

### Step 6.4: Performance Optimization

#### Backend Optimizations:
1. **Caching Strategy**:
   - Cache scraped content for 24 hours
   - Check database before re-scraping same URL
   - Implement Redis cache (bonus)

2. **Async Processing**:
   - Use FastAPI's async/await for I/O operations
   - Parallel LLM calls (summary, entities, quiz)

3. **Database Indexing**:
   - Index on `quizzes.url` (for duplicate checks)
   - Index on `quizzes.created_at` (for sorting history)

4. **Content Truncation**:
   - Limit article content to 4000 tokens for LLM
   - Use smart truncation (keep intro + important sections)

#### Frontend Optimizations:
1. Lazy load quiz history (pagination)
2. Debounce search input
3. Cache API responses in memory
4. Optimize re-renders with React.memo

---

### Step 6.5: Sample Data Collection

#### Create `sample_data/` folder:

**1. test_urls.txt**
```
https://en.wikipedia.org/wiki/Alan_Turing
https://en.wikipedia.org/wiki/Quantum_computing
https://www.bbc.com/news/science-environment-12345678
[8-10 diverse URLs]
```

**2. For each URL, create JSON files:**
- `alan_turing_quiz.json` (API response)
- `quantum_computing_quiz.json`
- etc.

**3. screenshots/**
- `tab1_generation.png`
- `tab1_quiz_display.png`
- `tab2_history.png`
- `tab2_modal.png`
- `quiz_taker_mode.png` (if implemented)

---

## Phase 7: Documentation & Submission

### Step 7.1: README.md Structure

```markdown
# DeepKlarity AI Wiki Quiz Generator

## Overview
Brief description of the project and its features.

## Technology Stack
- Backend: FastAPI (Python 3.9+)
- Database: PostgreSQL
- LLM: Google Gemini Pro API
- Frontend: React.js + Tailwind CSS
- Web Scraping: BeautifulSoup4

## Features
- [ ] List all implemented features
- [ ] Mark bonus features

## Setup Instructions

### Prerequisites
- Python 3.9+
- Node.js 18+
- PostgreSQL 14+
- Google Gemini API Key

### Backend Setup
1. Clone repository
2. Create virtual environment
3. Install dependencies: `pip install -r requirements.txt`
4. Create `.env` file with:
   ```
   GEMINI_API_KEY=your_key
   DATABASE_URL=postgresql://...
   ```
5. Run migrations
6. Start server: `uvicorn app.main:app --reload`

### Frontend Setup
1. Navigate to frontend directory
2. Install dependencies: `npm install`
3. Update API base URL in `.env`
4. Start dev server: `npm run dev`

### Database Setup
SQL commands to create database and tables

## API Endpoints

### POST /api/quiz/generate
Request body, response format, example

### GET /api/quiz/history
Query parameters, response format, example

### GET /api/quiz/{id}
Response format, example

## Testing

### Running Tests
Commands to run tests (if implemented)

### Manual Testing
Steps to test with sample URLs

## Prompt Templates

### Main Quiz Generation Prompt
[Full prompt text]

### Entity Extraction Prompt
[Full prompt text]

### Summary Generation Prompt
[Full prompt text]

### Related Topics Prompt
[Full prompt text]

## Sample Data
Location of sample JSON outputs and screenshots

## Project Structure
Detailed directory tree

## Known Limitations
- Maximum article length
- Supported URL patterns
- Rate limits

## Future Improvements
- [ ] List of potential enhancements

## Contributors
Your name and contact
```

---

### Step 7.2: Code Documentation

#### Backend Code Comments:
```python
# Each function should have:
"""
Brief description of what the function does.

Args:
    param1 (type): Description
    param2 (type): Description

Returns:
    type: Description of return value

Raises:
    ExceptionType: When and why
"""
```

#### Frontend Code Comments:
```javascript
/**
 * Component description
 * 
 * @param {Object} props - Component props
 * @param {string} props.quizId - ID of quiz to display
 * @returns {JSX.Element} Rendered component
 */
```

---

### Step 7.3: Prompt Template Documentation

Create `prompts/README.md`:

**Structure:**
1. Overview of prompting strategy
2. Main prompt with annotations explaining each section
3. Sub-prompts with usage context
4. Optimization decisions made
5. Examples of good vs. bad outputs
6. Iterative improvements made during testing

---

### Step 7.4: Final Checklist

#### Code Quality:
- ✓ All functions have docstrings
- ✓ Meaningful variable names
- ✓ No hardcoded values (use config)
- ✓ Consistent code style (PEP 8 for Python)
- ✓ Error handling in all API calls
- ✓ Input validation for all endpoints

#### Functionality:
- ✓ URL input and validation works
- ✓ Web scraping handles various sites
- ✓ Quiz generation produces quality questions
- ✓ Database stores and retrieves correctly
- ✓ History view displays all past quizzes
- ✓ Detail modal shows complete quiz
- ✓ Error messages are user-friendly

#### Documentation:
- ✓ README explains setup clearly
- ✓ API endpoints documented
- ✓ Prompts included with explanations
- ✓ Sample data provided (5+ examples)
- ✓ Screenshots captured

#### Testing Evidence:
- ✓ Tested with 10+ different URLs
- ✓ Tested error scenarios
- ✓ Verified database persistence
- ✓ Checked quiz quality manually

---

## Implementation Timeline

### Week 1:
- **Day 1-2**: Environment setup, database design, initial FastAPI structure
- **Day 3-4**: Web scraping service implementation and testing
- **Day 5-7**: LLM integration, prompt engineering, and quiz generation

### Week 2:
- **Day 1-2**: Complete backend API endpoints and database operations
- **Day 3-4**: Frontend development (Tab 1 - Quiz Generator)
- **Day 5-6**: Frontend development (Tab 2 - History)
- **Day 7**: Integration testing and bug fixes

### Week 3:
- **Day 1-2**: Prompt optimization and quiz quality improvements
- **Day 3-4**: UI/UX refinements and error handling
- **Day 5**: Testing with diverse URLs and edge cases
- **Day 6**: Documentation and sample data collection
- **Day 7**: Final review and submission preparation

---

## Detailed Prompt Engineering Strategy

### Prompt Design Philosophy

The prompt engineering approach follows a **hierarchical structure** with clear separation of concerns:

1. **Main Prompt**: Orchestrates quiz generation
2. **Sub-Prompts**: Handle specific tasks (entities, summary, related topics)
3. **Validation Prompts**: Verify output quality (optional, if budget allows)

### Grounding Techniques

#### 1. Explicit Constraints
Every prompt emphasizes:
- "ONLY use information from the article"
- "DO NOT add external knowledge"
- "Verify all facts against the provided content"

#### 2. Output Structure Enforcement
- Use strict JSON schemas
- Specify exact field names and types
- Provide output examples in prompts

#### 3. Context Windowing
For long articles:
```
Strategy 1: Sliding Window
- Process article in 3000-token chunks
- Generate 2-3 questions per chunk
- Combine results

Strategy 2: Smart Truncation
- Keep: Title, Introduction (first 2 paragraphs), Section headers, First paragraph of each section, Conclusion
- Remove: References, External links, See Also sections
- Target: ~3500 tokens for main content
```

---

## Advanced Implementation Considerations

### Handling Different Content Types

#### Wikipedia Articles
**Special Processing:**
1. Remove citation brackets: `[1]`, `[edit]`, `[citation needed]`
2. Extract infobox data (key-value pairs)
3. Parse section hierarchy (H2, H3, H4)
4. Clean up special formatting (e.g., `{{convert|10|km|mi}}`)

**Infobox Utilization:**
- Use infobox for generating easy factual questions
- Example: "Born: 23 June 1912" → Question about birth year

#### News Articles
**Characteristics:**
- Inverted pyramid structure (key info first)
- Often includes quotes
- May be time-sensitive

**Processing Strategy:**
- Focus on first 50% of content (most important info)
- Generate questions about: Who, What, When, Where, Why
- Handle quoted text carefully (attribute to sources)

#### Blog Posts/Educational Content
**Characteristics:**
- Personal voice/opinions
- May include author's interpretations

**Processing Strategy:**
- Focus on factual information only
- Avoid questions about opinions
- Verify statements that seem subjective

---

### Database Performance Optimization

#### Indexing Strategy
```sql
-- Speed up duplicate URL checks
CREATE INDEX idx_quizzes_url ON quizzes(url);

-- Speed up history pagination
CREATE INDEX idx_quizzes_created_at ON quizzes(created_at DESC);

-- Speed up history search
CREATE INDEX idx_quizzes_title ON quizzes(title);
CREATE INDEX idx_quizzes_url_text ON quizzes USING gin(to_tsvector('english', url));

-- Speed up joins
CREATE INDEX idx_questions_quiz_id ON questions(quiz_id);
CREATE INDEX idx_entities_quiz_id ON key_entities(quiz_id);
CREATE INDEX idx_topics_quiz_id ON related_topics(quiz_id);
```

#### Query Optimization
```python
# Bad: N+1 query problem
def get_all_quizzes():
    quizzes = db.query(Quiz).all()
    for quiz in quizzes:
        quiz.questions  # Triggers separate query for each quiz
    return quizzes

# Good: Eager loading
def get_all_quizzes():
    quizzes = db.query(Quiz).options(
        joinedload(Quiz.questions),
        joinedload(Quiz.key_entities),
        joinedload(Quiz.related_topics)
    ).all()
    return quizzes
```

---

### LLM Response Validation

#### Post-Processing Pipeline

**Step 1: JSON Validation**
```python
def validate_quiz_json(response):
    required_fields = ['quiz']
    quiz_fields = ['question', 'options', 'answer', 'difficulty', 'explanation']
    
    # Check structure
    if 'quiz' not in response:
        raise ValueError("Missing 'quiz' field")
    
    # Check each question
    for i, q in enumerate(response['quiz']):
        for field in quiz_fields:
            if field not in q:
                raise ValueError(f"Question {i} missing '{field}'")
        
        # Validate options format
        if len(q['options']) != 4:
            raise ValueError(f"Question {i} must have exactly 4 options")
        
        # Validate answer
        if q['answer'] not in ['A', 'B', 'C', 'D']:
            raise ValueError(f"Question {i} has invalid answer: {q['answer']}")
        
        # Validate difficulty
        if q['difficulty'] not in ['easy', 'medium', 'hard']:
            raise ValueError(f"Question {i} has invalid difficulty")
    
    return True
```

**Step 2: Content Validation**
```python
def validate_question_grounding(question, article_text):
    """
    Check if question seems grounded in article
    (Basic heuristic - not foolproof)
    """
    # Extract key terms from question
    question_terms = extract_key_terms(question['question'])
    
    # Check if terms appear in article
    grounded_terms = [term for term in question_terms 
                     if term.lower() in article_text.lower()]
    
    # If less than 50% of terms found, flag as suspicious
    if len(grounded_terms) / len(question_terms) < 0.5:
        logger.warning(f"Low grounding score for question: {question['question']}")
    
    return True  # Don't reject, just log warning
```

**Step 3: Duplicate Detection**
```python
def check_duplicate_questions(questions):
    """Remove or flag very similar questions"""
    from difflib import SequenceMatcher
    
    for i, q1 in enumerate(questions):
        for j, q2 in enumerate(questions[i+1:], start=i+1):
            similarity = SequenceMatcher(None, 
                                        q1['question'], 
                                        q2['question']).ratio()
            if similarity > 0.8:
                logger.warning(f"Questions {i} and {j} are very similar")
                # Remove the duplicate
                questions.pop(j)
    
    return questions
```

---

### Error Handling Best Practices

#### Backend Error Response Format
```python
# Standardized error response
{
    "error": {
        "code": "SCRAPING_FAILED",
        "message": "Unable to extract content from the provided URL",
        "details": "The page returned a 404 status code",
        "suggestion": "Please verify the URL is correct and accessible"
    }
}
```

#### Error Categories and Codes
```python
ERROR_CODES = {
    # Input validation
    "INVALID_URL": "The provided URL format is invalid",
    "EMPTY_URL": "URL cannot be empty",
    
    # Scraping errors
    "SCRAPING_FAILED": "Unable to scrape the webpage",
    "CONTENT_TOO_SHORT": "Article content is too short (minimum 300 words)",
    "NO_TEXT_CONTENT": "No readable text found on the page",
    "BLOCKED_BY_ROBOTS": "Access to this URL is blocked by robots.txt",
    
    # LLM errors
    "LLM_GENERATION_FAILED": "Failed to generate quiz questions",
    "LLM_RATE_LIMIT": "API rate limit reached, please try again later",
    "INVALID_LLM_RESPONSE": "Generated content did not meet quality standards",
    
    # Database errors
    "DB_CONNECTION_ERROR": "Database connection failed",
    "DUPLICATE_URL": "This URL has already been processed",
    
    # General errors
    "INTERNAL_ERROR": "An unexpected error occurred",
    "TIMEOUT": "Request timed out"
}
```

#### Retry Logic Implementation
```python
def retry_with_backoff(func, max_attempts=3, backoff_factor=2):
    """
    Retry a function with exponential backoff
    """
    for attempt in range(max_attempts):
        try:
            return func()
        except Exception as e:
            if attempt == max_attempts - 1:
                raise
            wait_time = backoff_factor ** attempt
            logger.warning(f"Attempt {attempt + 1} failed, retrying in {wait_time}s")
            time.sleep(wait_time)
```

---

### Frontend State Management

#### Quiz Generator Component State
```javascript
// State structure for Tab 1
{
  // Input state
  url: "",
  isValidUrl: true,
  
  // Processing state
  isLoading: false,
  progress: 0, // 0-100
  currentStep: "", // "Scraping...", "Generating...", etc.
  
  // Result state
  quizData: null,
  error: null,
  
  // UI state
  showQuiz: false,
  selectedQuestion: null
}
```

#### History Component State
```javascript
// State structure for Tab 2
{
  // Data state
  quizzes: [],
  totalCount: 0,
  
  // Pagination state
  currentPage: 1,
  itemsPerPage: 20,
  
  // Search/Filter state
  searchQuery: "",
  sortBy: "created_at",
  sortOrder: "desc",
  
  // UI state
  isLoading: false,
  selectedQuizId: null,
  showModal: false,
  modalData: null
}
```

---

### Security Considerations

#### Backend Security

**1. URL Validation**
```python
def validate_url(url: str) -> bool:
    """
    Validate URL to prevent SSRF attacks
    """
    # Check format
    if not url.startswith(('http://', 'https://')):
        raise ValueError("URL must start with http:// or https://")
    
    # Parse URL
    parsed = urlparse(url)
    
    # Prevent access to internal networks
    blocked_hosts = [
        'localhost', '127.0.0.1', '0.0.0.0',
        '10.', '172.16.', '192.168.',  # Private IP ranges
        'metadata.google.internal'  # Cloud metadata
    ]
    
    for blocked in blocked_hosts:
        if parsed.netloc.startswith(blocked):
            raise ValueError("Access to internal networks is not allowed")
    
    return True
```

**2. Rate Limiting**
```python
from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/quiz/generate")
@limiter.limit("10/hour")  # 10 requests per hour per IP
async def generate_quiz(request: Request, url: str):
    # Implementation
    pass
```

**3. Input Sanitization**
- Sanitize all user inputs before database insertion
- Use parameterized queries (SQLAlchemy handles this)
- Escape HTML in scraped content before display

**4. API Key Protection**
- Never expose Gemini API key in frontend
- Store in environment variables
- Use backend as proxy for all LLM calls

#### Frontend Security

**1. XSS Prevention**
- React automatically escapes rendered content
- Be cautious with `dangerouslySetInnerHTML`
- Sanitize URLs before displaying as links

**2. CORS Configuration**
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["*"],
)
```

---

### Bonus Features Implementation

#### Feature 1: Quiz Taker Mode

**Backend Changes:**
- No changes needed (same API)

**Frontend Implementation:**
1. Create `QuizTaker` component
2. State management:
   ```javascript
   {
     currentQuestionIndex: 0,
     userAnswers: {},
     showExplanation: false,
     quizCompleted: false,
     score: 0
   }
   ```
3. Logic flow:
   - Hide correct answers initially
   - Track user selections
   - Show explanation after submission
   - Calculate and display final score

#### Feature 2: URL Preview

**Implementation:**
```python
@app.get("/api/quiz/preview")
async def preview_url(url: str):
    """
    Fetch article title without full processing
    """
    response = requests.get(url, timeout=10)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    title = soup.find('h1') or soup.find('title')
    
    return {
        "url": url,
        "title": title.text.strip() if title else "Unknown",
        "status": "accessible"
    }
```

**Frontend Usage:**
- Call preview endpoint on URL input blur
- Display title preview: "Article: {title}"
- Gives user confidence before generating

#### Feature 3: Caching System

**Implementation with Redis:**
```python
import redis
import hashlib

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def get_cached_quiz(url: str):
    """Check if quiz for this URL exists in cache"""
    url_hash = hashlib.md5(url.encode()).hexdigest()
    cached = redis_client.get(f"quiz:{url_hash}")
    
    if cached:
        return json.loads(cached)
    return None

def cache_quiz(url: str, quiz_data: dict, ttl: int = 86400):
    """Cache quiz for 24 hours"""
    url_hash = hashlib.md5(url.encode()).hexdigest()
    redis_client.setex(
        f"quiz:{url_hash}",
        ttl,
        json.dumps(quiz_data)
    )
```

#### Feature 4: Section-wise Question Grouping

**Backend Processing:**
```python
def assign_questions_to_sections(questions, article_sections):
    """
    Match questions to article sections based on content
    """
    for question in questions:
        best_match_section = None
        best_match_score = 0
        
        for section in article_sections:
            # Calculate similarity between question and section content
            score = calculate_similarity(question['question'], section['content'])
            
            if score > best_match_score:
                best_match_score = score
                best_match_section = section['heading']
        
        question['section'] = best_match_section
    
    return questions
```

**Frontend Display:**
Group questions by section in accordion-style layout

---

### Quality Assurance Checklist

#### Pre-Submission Review

**Code Quality:**
- [ ] No commented-out code blocks
- [ ] No console.log statements in production frontend
- [ ] No print statements in production backend
- [ ] All TODO comments resolved
- [ ] No hardcoded secrets or API keys
- [ ] Consistent naming conventions throughout

**Functionality Testing:**
- [ ] Generate quiz from 10+ different URLs
- [ ] Verify all quizzes are factually accurate
- [ ] Test history pagination with 50+ entries
- [ ] Test search functionality
- [ ] Test modal open/close
- [ ] Test all error scenarios
- [ ] Verify database persistence after server restart

**Cross-Browser Testing:**
- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Mobile browsers (iOS Safari, Chrome Mobile)

**Performance Validation:**
- [ ] Quiz generation completes in <30 seconds
- [ ] History page loads in <2 seconds
- [ ] No memory leaks (check with Chrome DevTools)
- [ ] Database queries optimized (check execution plans)

**Documentation Completeness:**
- [ ] README covers all setup steps
- [ ] API endpoints documented with examples
- [ ] Prompts included with explanations
- [ ] 5+ sample JSON outputs provided
- [ ] Screenshots for all major features
- [ ] Known limitations listed
- [ ] Future improvements section included

---

## Troubleshooting Guide

### Common Issues and Solutions

#### Issue 1: LLM generates questions with incorrect information
**Cause:** Hallucination or misinterpretation of article
**Solutions:**
1. Strengthen grounding instructions in prompt
2. Reduce temperature to 0.2 or lower
3. Add negative examples to prompt (few-shot learning)
4. Implement post-generation validation
5. Truncate article more carefully (preserve context)

#### Issue 2: Scraping fails for certain websites
**Cause:** Anti-scraping measures, dynamic content, unusual HTML structure
**Solutions:**
1. Add User-Agent header: `Mozilla/5.0 ...`
2. Add delay between requests (respect rate limits)
3. Handle JavaScript-rendered content (if needed, use Selenium)
4. Implement fallback parsing strategies
5. Provide clear error message to user

#### Issue 3: Database connection errors
**Cause:** Wrong credentials, connection limits, network issues
**Solutions:**
1. Verify DATABASE_URL format
2. Check PostgreSQL is running
3. Increase connection pool size
4. Implement connection retry logic
5. Use connection pooling (SQLAlchemy handles this)

#### Issue 4: Quiz quality is inconsistent
**Cause:** LLM variability, poor prompt design, content quality varies
**Solutions:**
1. Add more examples in prompts (few-shot learning)
2. Implement quality filters (reject low-quality outputs)
3. Generate 12-15 questions, select best 8
4. Add question diversity checks
5. Fine-tune temperature and top_p parameters

#### Issue 5: Frontend-backend CORS errors
**Cause:** Missing or incorrect CORS configuration
**Solutions:**
1. Add CORS middleware to FastAPI
2. Specify correct frontend origin URL
3. Include credentials if needed
4. Check browser console for specific error
5. Test API with Postman first (isolate issue)

---

## Final Deliverables Summary

### 1. Code Repository Structure
```
deepklarity-quiz/
├── backend/
│   ├── app/ (complete Python backend)
│   ├── prompts/ (all prompt templates)
│   ├── requirements.txt
│   ├── .env.example
│   └── README.md
├── frontend/
│   ├── src/ (complete React frontend)
│   ├── package.json
│   └── README.md
├── sample_data/
│   ├── test_urls.txt
│   ├── alan_turing_quiz.json
│   ├── quantum_computing_quiz.json
│   ├── [8+ more examples]
│   └── screenshots/
│       ├── tab1_generation.png
│       ├── tab1_quiz_display.png
│       ├── tab2_history.png
│       ├── tab2_modal.png
│       └── [bonus features]
├── README.md (main project README)
└── SETUP_GUIDE.md (detailed setup instructions)
```

### 2. Documentation Files

**README.md** - Main documentation
**SETUP_GUIDE.md** - Step-by-step setup
**PROMPTS.md** - All prompts with explanations
**API_DOCS.md** - API endpoint reference
**TESTING.md** - Testing procedures and results

### 3. Sample Data

- **Minimum 5 URLs** tested with diverse content
- **JSON outputs** for each test URL
- **Screenshots** of all major features
- **Error case examples** (optional but impressive)

### 4. Presentation Materials (Optional but Recommended)

- Brief video demo (2-3 minutes)
- Architecture diagram
- Prompt engineering decisions document
- Performance benchmarks

---

## Success Metrics

### Evaluation Scoring Guide

Based on assessment criteria, aim for:

**Prompt Design & Optimization (25%)**
- Clear, detailed prompts with grounding instructions
- Effective use of JSON output formatting
- Demonstrated iterative improvement
- **Target: 90%+ score**

**Quiz Quality (20%)**
- 80%+ questions factually accurate
- Good difficulty distribution
- Clear, unambiguous phrasing
- **Target: 85%+ score**

**Extraction Quality (15%)**
- Clean text extraction from diverse sources
- Accurate entity identification
- Proper section parsing
- **Target: 90%+ score**

**Functionality (15%)**
- End-to-end flow works smoothly
- All features implemented
- Database operations correct
- **Target: 95%+ score**

**Code Quality (10%)**
- Clean, modular structure
- Meaningful comments
- Consistent style
- **Target: 90%+ score**

**Error Handling (5%)**
- Graceful failure for all error cases
- Clear user-facing messages
- **Target: 90%+ score**

**UI Design (5%)**
- Clean, minimal interface
- Responsive design
- Good UX
- **Target: 85%+ score**

**Database Accuracy (3%)**
- Data stored correctly
- Efficient queries
- **Target: 95%+ score**

**Testing Evidence (2%)**
- Comprehensive sample data
- Variety of test cases
- **Target: 90%+ score**

---

## Conclusion

This implementation plan provides a comprehensive roadmap for building the DeepKlarity AI Quiz Generator. Key success factors:

1. **Strong Prompt Engineering**: Focus on grounding, clarity, and structure
2. **Robust Error Handling**: Handle all edge cases gracefully
3. **Quality Validation**: Ensure quiz questions are accurate and valuable
4. **Clean Code**: Modular, documented, maintainable
5. **Thorough Testing**: Diverse test cases with evidence
6. **Complete Documentation**: Clear setup and usage instructions

Follow this plan systematically, test frequently, and iterate on prompt quality to achieve the best results.

**Good luck with your implementation!