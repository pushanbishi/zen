import React, { useState } from 'react';
import ChatComponent from './ChatComponent';
import './css/App.css'; // Optional: for additional styling

const App = () => {
  const [isChatOpen, setIsChatOpen] = useState(false);

  const handleButtonClick = () => {
    setIsChatOpen(true);
  };

  const handleCloseChat = () => {
    setIsChatOpen(false);
  };

  return (
    <div className="app-container">
      <button onClick={handleButtonClick}>Find Your Zen</button>
      {isChatOpen && (
        <div className="chat-popup">
          <div className="chat-popup-content">
            <button className="close-button" onClick={handleCloseChat}>Close</button>
            <ChatComponent />
          </div>
        </div>
      )}
    </div>
  );
};

export default App;