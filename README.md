# DeepKlarity AI Quiz Generator

An AI-powered quiz generator that creates educational quizzes from web articles using OpenAI GPT-4o mini.

## 🚀 Features

- **Automatic Quiz Generation**: Generate multiple-choice quizzes from any Wikipedia article or web page
- **AI-Powered Content Analysis**: Uses OpenAI GPT-4o mini to create meaningful questions
- **Entity Extraction**: Automatically identifies key people, organizations, and locations
- **Smart Difficulty Levels**: Questions categorized as Easy, Medium, or Hard
- **Quiz History**: Browse and search previously generated quizzes
- **Related Topics**: Suggests topics for further learning
- **Responsive UI**: Clean, modern interface built with React and Tailwind CSS

## 🛠️ Technology Stack

### Backend
- **FastAPI** (Python 3.11+)
- **SQLAlchemy** with SQLite database
- **OpenAI GPT-4o mini API** (via LangChain)
- **BeautifulSoup4** for web scraping

### Frontend
- **React.js** with Vite
- **Tailwind CSS** for styling
- **Axios** for API communication

## 📋 Prerequisites

- Python 3.11 or higher
- Node.js 18 or higher
- OpenAI API Key ([Get it here](https://platform.openai.com/account/api-keys))

## 🔧 Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/sureshnennavath/DeepKwality-Assessment.git
cd DeepKwality-Assessment
```

### 2. Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate virtual environment**
   - Windows:
     ```bash
     .\venv\Scripts\activate
     ```
   - Linux/Mac:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure environment variables**
   - Copy `.env.example` to `.env` (if it exists) or create a new `.env` file
   - Add your OpenAI API key:
     ```env
     # Database Configuration
     DATABASE_URL=sqlite:///./deepklarity_quiz.db

     # OpenAI API
     OPENAI_API_KEY=your_openai_api_key_here

     # Server Configuration
     HOST=0.0.0.0
     PORT=8000
     DEBUG=True
     ```

6. **Start the backend server**
   ```bash
   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

   Server will run at: `http://localhost:8000`

### 3. Frontend Setup

1. **Navigate to frontend directory** (open a new terminal)
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start the development server**
   ```bash
   npm run dev
   ```

   Frontend will run at: `http://localhost:5173`

## 📖 Usage

### Generate a Quiz

1. Open the application at `http://localhost:5173`
2. Navigate to the "Quiz Generator" tab
3. Enter a URL (Wikipedia articles work best)
4. Select the number of questions (5-10)
5. Click "Generate Quiz"
6. Wait for the AI to process the article and generate questions

### View Quiz History

1. Navigate to the "Quiz History" tab
2. Browse all previously generated quizzes
3. Use the search bar to filter by title or URL
4. Click "View Details" to see a specific quiz

## 🌐 API Endpoints

### Generate Quiz
```http
POST /api/quiz/generate
Content-Type: application/json

{
  "url": "https://en.wikipedia.org/wiki/Python_(programming_language)",
  "num_questions": 8
}
```

### Get Quiz History
```http
GET /api/quiz/history?page=1&limit=20&search=python
```

### Get Specific Quiz
```http
GET /api/quiz/{quiz_id}
```

### Delete Quiz
```http
DELETE /api/quiz/{quiz_id}
```

## 🎯 Prompt Engineering

The application uses carefully crafted prompts for:

1. **Quiz Generation**: Ensures factual accuracy and diverse difficulty levels
2. **Entity Extraction**: Identifies people, organizations, and locations
3. **Summary Generation**: Creates concise article summaries
4. **Related Topics**: Suggests relevant topics for further learning

All prompts are located in `backend/app/services/` directory.

## 📁 Project Structure

```
DeepKwality-Assessment/
├── backend/
│   ├── app/
│   │   ├── models/          # SQLAlchemy models
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── services/        # Business logic (LLM, scraper)
│   │   ├── routes/          # API endpoints
│   │   ├── config.py        # Configuration
│   │   ├── database.py      # Database setup
│   │   └── main.py          # FastAPI app
│   ├── requirements.txt
│   ├── .env                 # Environment variables
│   └── deepklarity_quiz.db  # SQLite database (created automatically)
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── services/        # API service
│   │   ├── App.jsx          # Main app component
│   │   └── main.jsx         # Entry point
│   ├── package.json
│   ├── tailwind.config.js
│   └── vite.config.js
├── sample_data/             # Sample quiz outputs
└── README.md
```

## 🧪 Testing

### Test URLs

Here are some recommended URLs for testing:

- https://en.wikipedia.org/wiki/Python_(programming_language)
- https://en.wikipedia.org/wiki/Artificial_intelligence
- https://en.wikipedia.org/wiki/Machine_learning
- https://en.wikipedia.org/wiki/Climate_change
- https://en.wikipedia.org/wiki/Samsung
- https://en.wikipedia.org/wiki/Apple

### Minimum Requirements

- Articles should have at least 300 words
- URLs must be publicly accessible
- Best results with well-structured educational content

## 🔒 Security Features

- URL validation to prevent SSRF attacks
- Input sanitization for all user inputs
- CORS configuration for frontend-backend communication
- Environment variable protection for API keys

## ⚠️ Known Limitations

- Maximum article length: ~4000 tokens (truncated if longer)
- Supported URL patterns: HTTP/HTTPS only
- Rate limits depend on OpenAI API tier
- Best performance with English-language content

## 🤝 Contributing

This project was built as an assessment for DeepKlarity. Future improvements could include:

- Support for more languages
- Interactive quiz-taking mode
- Export quizzes to PDF
- Difficulty level customization
- Batch quiz generation

## 📝 License

This project is for educational and assessment purposes.

## 👤 Author

Created for DeepKlarity Assessment

---

**Built with FastAPI, React, and OpenAI GPT-4o mini** 🚀
