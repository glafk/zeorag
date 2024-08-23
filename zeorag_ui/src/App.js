import React, { useState } from 'react';
import SessionList from './components/SessionList';
import ChatWindow from './components/ChatWindow';
import FileList from './components/FileList';
import FileUpload from './components/FileUpload';
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css'; // Custom styles

const App = () => {
  const [activeSession, setActiveSession] = useState(null);
  const [sessionName, setSessionName] = useState('');
  const [view, setView] = useState('chat');

  const handleSelectSession = (sessionId, name) => {
    setSessionName(name);
    setActiveSession(sessionId);
  };

    return (
    <div className="app-container">
        <div className="sidebar">
          {view === 'chat' && (
          <SessionList 
            onSelectSession={handleSelectSession} 
            activeSession={activeSession} 
            setActiveSession={setActiveSession}
            setSessionName={setSessionName}
          />)}
          <div className="view-toggle">
            <button
              className="btn button-block btn-outline-light mt-3"
              onClick={() => setView(view === 'chat' ? 'files' : 'chat')}
            >
              {view === 'chat' ? 'Papers' : 'Chat'}
            </button>
          </div>
        </div>
      <div className="main-content">
        {view === 'chat' ? (
          <ChatWindow key={activeSession} sessionId={activeSession} sessionName={sessionName} />
        ) : (
          <div className="files-container">
            <FileList />
            <FileUpload />
          </div>
        )}
      </div>
    </div>
  );
};


export default App;
