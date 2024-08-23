import React, { useEffect, useState } from 'react';
import { getChatHistory, queryRAG } from '../services/api';


const ChatWindow = ({ sessionId, sessionName }) => {
  const [history, setHistory] = useState([]);
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchHistory = async () => {
      if (sessionId) {
        const response = await getChatHistory(sessionId);
        setHistory(response.data);
      }
    };
    fetchHistory();
  }, [sessionName]);

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Add the user's message to the history state
    setHistory((prev) => [
      ...prev,
      { role: 'user', content: query } // Assuming the role for the user is 'user'
    ]);

    setQuery('');
    setLoading(true);

    try {
      console.log("SESSION NAME FOR QUERY: " + sessionName)
      const response = await queryRAG(query, sessionName);
      const reader = response.body.getReader();
      let text = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        text += new TextDecoder().decode(value);

        setHistory((prev) => {
          const updatedHistory = [...prev];
          if (updatedHistory[updatedHistory.length - 1].role == "assistant") {
            updatedHistory[updatedHistory.length - 1].content = text;
            return updatedHistory;
          }
          return [...prev, { role: 'assistant', content: text }];
        });
      }
    } catch (error) {
      console.error('Error querying RAG:', error);
    }

    setLoading(false);
  };

  return (
    <div className="chat-window">
      <div className="chat-header">
        {sessionName ? sessionName : 'ZeoRAG'}
      </div>
      <div className="chat-history">
        {sessionId ? (
          history.length > 0 ? (
            history.map((msg, index) => (
              <div key={index} className={`chat-message ${msg.role}`}>
                {msg.content}
              </div>
            ))
          ) : (
            <h4>No messages to show</h4>
          )
        ) : (
          <h4>Select a session or create a new one to start</h4>
        )}
        {loading && <div className="loading">Loading...</div>}
      </div>
      {sessionId && (
        <form onSubmit={handleSubmit} className="chat-input">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Enter your query"
            className="form-control me-2" // Bootstrap classes for form control
          />
          <button type="submit" className="btn btn-primary">Send</button>
        </form>
      )}
    </div>
  );
};

export default ChatWindow;
