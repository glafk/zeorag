import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export const getSessions = () => axios.get(`${API_URL}/sessions`);
export const getChatHistory = (sessionId) => axios.get(`${API_URL}/sessions/${sessionId}`);
export const queryRAG = async (question, session_name) => {
  const response = await fetch(`${API_URL}/query`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ question, session_name }),
  });

  return response;
};
export const getFiles = () => axios.get(`${API_URL}/list_documents`);
export const uploadFile = (formData) => axios.post(`${API_URL}/upload_document/`, formData, {
  headers: {
    'Content-Type': 'multipart/form-data'
  }
});
export const deleteSession = (sessionId) => axios.delete(`${API_URL}/sessions/${sessionId}`);
