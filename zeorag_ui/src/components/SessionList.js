import React, { useEffect, useState } from 'react';
import { getSessions, deleteSession } from '../services/api';

const SessionList = ({ onSelectSession, activeSession, setActiveSession, setSessionName }) => {
  const [sessions, setSessions] = useState([]);
  const [newSessionId, setNewSessionId] = useState('');

  useEffect(() => {
    const fetchSessions = async () => {
      try {
        const response = await getSessions();
        setSessions(response.data);
      } catch (error) {
        console.error('Error fetching sessions:', error);
      }
    };
    fetchSessions();
  }, []);

  const handleCreateSession = async () => {
    if (newSessionId.trim() === '') return;
    try {
      // Assuming there's a create session API method
      setNewSessionId(''); // Clear input field
      setSessions([...sessions, { session_id: newSessionId, session_name: newSessionId }]);
      onSelectSession(newSessionId, newSessionId);
    } catch (error) {
      console.error('Error creating session:', error);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleCreateSession();
    }
  };

  const handleDeleteSession = async (sessionId) => {
    try {
      await deleteSession(sessionId);
      setSessions(sessions.filter(session => session.session_id !== sessionId));

      // If the deleted session was the active one, reset the active session
      if (sessionId === activeSession) {
        setActiveSession(null);
        setSessionName(null);
      }
    } catch (error) {
      console.error('Error deleting session:', error);
    }
  };

  return (
    <div className="session-list container mt-4">
      <h3 className="mb-3">Sessions</h3>
      {sessions.length === 0 ? (
        <div>No sessions available</div>
      ) : (
        <ul className="list-group">
          {sessions.map((session) => (
            <li
              key={session.session_id}
              className={`list-group-item d-flex justify-content-between align-items-center ${activeSession === session.session_id ? 'active' : ''}`}
              onClick={() => onSelectSession(session.session_id, session.session_name)}
            >
              {session.session_name || session.session_id}
              <button
                className="delete-button btn btn-danger btn-sm"
                onClick={(e) => {
                  e.stopPropagation();
                  handleDeleteSession(session.session_id);
                }}
              >
                x
              </button>
            </li>
          ))}
        </ul>
      )}
      <div className="session-creation mt-4">
        <input
          type="text"
          value={newSessionId}
          onChange={(e) => setNewSessionId(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="New session (+hit enter)"
          className="form-control"
        />
        <button
          onClick={handleCreateSession}
          className="btn btn-primary mt-2"
          style={{ display: 'none' }} // Hide the button
        >
          Create New Session
        </button>
      </div>
    </div>
  );
};

export default SessionList;


