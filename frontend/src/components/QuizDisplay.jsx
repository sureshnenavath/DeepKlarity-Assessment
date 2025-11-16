const QuizDisplay = ({ quiz }) => {
  if (!quiz) return null;

  const getDifficultyColor = (difficulty) => {
    switch (difficulty) {
      case 'easy':
        return 'bg-green-100 text-green-800';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800';
      case 'hard':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header Card */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">{quiz.title}</h1>
        <a
          href={quiz.url}
          target="_blank"
          rel="noopener noreferrer"
          className="text-blue-600 hover:underline text-sm mb-4 inline-block"
        >
          {quiz.url}
        </a>
        {quiz.summary && (
          <p className="text-gray-700 mt-4 leading-relaxed">{quiz.summary}</p>
        )}
        <div className="mt-4 text-sm text-gray-500">
          Created: {new Date(quiz.created_at).toLocaleString()}
        </div>
      </div>

      {/* Key Entities */}
      {quiz.key_entities && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-bold text-gray-800 mb-4">Key Entities</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {['people', 'organizations', 'locations'].map((type) => {
              const entities = quiz.key_entities?.[type] || [];
              if (!entities.length) return null;
              return (
                <div key={type}>
                  <h3 className="font-semibold text-gray-700 mb-2 capitalize">{type}</h3>
                  <div className="flex flex-wrap gap-2">
                    {entities.map((entity, idx) => (
                      <span
                        key={idx}
                        className="inline-block bg-blue-100 text-blue-800 text-sm px-3 py-1 rounded-full"
                      >
                        {entity}
                      </span>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Sections */}
      {quiz.sections && quiz.sections.length > 0 && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-bold text-gray-800 mb-4">Article Sections</h2>
          <div className="flex flex-wrap gap-2">
            {quiz.sections.map((section, idx) => (
              <span
                key={idx}
                className="inline-block bg-gray-100 text-gray-700 text-sm px-3 py-1 rounded-md"
              >
                {section}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Questions */}
      <div className="space-y-4">
        <h2 className="text-2xl font-bold text-gray-800">Questions ({quiz.quiz?.length || 0})</h2>
        {quiz.quiz && quiz.quiz.map((question, idx) => {
          const optionList = question.options || [];
          const correctAnswerText = question.answer;
          return (
            <div key={`${idx}-${question.question}`} className="bg-white rounded-lg shadow-md p-6">
              <div className="flex items-start justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900 flex-1">
                  {idx + 1}. {question.question}
                </h3>
                <span className={`ml-4 px-3 py-1 rounded-full text-xs font-semibold ${getDifficultyColor(question.difficulty)}`}>
                  {question.difficulty}
                </span>
              </div>

              <div className="space-y-2 mb-4">
                {optionList.map((option, optIdx) => {
                  const letter = String.fromCharCode(65 + optIdx);
                  const isCorrect = option === correctAnswerText;
                  return (
                    <div
                      key={`${optIdx}-${option}`}
                      className={`p-3 rounded-lg border-2 ${
                        isCorrect
                          ? 'border-green-500 bg-green-50'
                          : 'border-gray-200 bg-gray-50'
                      }`}
                    >
                      <span className="font-semibold">{letter}.</span> {option}
                      {isCorrect && (
                        <span className="ml-2 text-green-600 font-semibold">✓ Correct</span>
                      )}
                    </div>
                  );
                })}
              </div>

              {question.explanation && (
                <div className="bg-blue-50 border-l-4 border-blue-500 p-4 rounded">
                  <p className="text-sm text-gray-700">
                    <strong>Explanation:</strong> {question.explanation}
                  </p>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Related Topics */}
      {quiz.related_topics && quiz.related_topics.length > 0 && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-bold text-gray-800 mb-4">Related Topics</h2>
          <div className="flex flex-wrap gap-2">
            {quiz.related_topics.map((topic, idx) => (
              <span
                key={idx}
                className="inline-block bg-purple-100 text-purple-800 text-sm px-4 py-2 rounded-lg cursor-pointer hover:bg-purple-200 transition"
              >
                {typeof topic === 'string' ? topic : topic.topic_name}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default QuizDisplay;
