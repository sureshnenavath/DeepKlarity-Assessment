import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const quizAPI = {
  /**
   * Generate a new quiz from a URL
   */
  generateQuiz: async (url, numQuestions = 8) => {
    try {
      const response = await api.post('/quiz/generate', {
        url,
        num_questions: numQuestions,
      });
      return response.data;
    } catch (error) {
      throw error.response?.data?.error || error;
    }
  },

  /**
   * Get quiz history with pagination and search
   */
  getQuizHistory: async (page = 1, limit = 20, search = '') => {
    try {
      const params = { page, limit };
      if (search) params.search = search;
      
      const response = await api.get('/quiz/history', { params });
      return response.data;
    } catch (error) {
      throw error.response?.data?.error || error;
    }
  },

  /**
   * Get a specific quiz by ID
   */
  getQuizById: async (quizId) => {
    try {
      const response = await api.get(`/quiz/${quizId}`);
      return response.data;
    } catch (error) {
      throw error.response?.data?.error || error;
    }
  },

  /**
   * Delete a quiz by ID
   */
  deleteQuiz: async (quizId) => {
    try {
      const response = await api.delete(`/quiz/${quizId}`);
      return response.data;
    } catch (error) {
      throw error.response?.data?.error || error;
    }
  },
};

export default api;
