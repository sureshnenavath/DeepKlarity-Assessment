import { useState } from 'react';
import QuizGenerator from './components/QuizGenerator';
import QuizDisplay from './components/QuizDisplay';
import QuizHistory from './components/QuizHistory';
import './index.css';

function App() {
  const [activeTab, setActiveTab] = useState('generator');
  const [currentQuiz, setCurrentQuiz] = useState(null);

  const handleQuizGenerated = (quiz) => {
    setCurrentQuiz(quiz);
  };

  const handleSelectQuiz = (quiz) => {
    setCurrentQuiz(quiz);
    setActiveTab('generator');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <h1 className="text-3xl font-bold text-gray-900">
            DeepKlarity Quiz Generator
          </h1>
          <p className="mt-2 text-sm text-gray-600">
            AI-powered quiz generation from web articles using Large Language Models
          </p>
        </div>
      </header>

      {/* Tabs */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-6">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            <button
              onClick={() => setActiveTab('generator')}
              className={`${
                activeTab === 'generator'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm transition`}
            >
              Quiz Generator
            </button>
            <button
              onClick={() => setActiveTab('history')}
              className={`${
                activeTab === 'history'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm transition`}
            >
              Quiz History
            </button>
          </nav>
        </div>
      </div>

      {/* Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'generator' ? (
          <div>
            <QuizGenerator onQuizGenerated={handleQuizGenerated} />
            {currentQuiz && <QuizDisplay quiz={currentQuiz} />}
          </div>
        ) : (
          <QuizHistory onSelectQuiz={handleSelectQuiz} />
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <p className="text-center text-sm text-gray-500">
            Built with FastAPI, React, and LLMs
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;
