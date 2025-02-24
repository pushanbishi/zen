import React, { useState } from 'react';
import './CrisisLineAssistant.css';
import ChatWindow from './ChatWindow';

const CrisisLineAssistant = () => {
  const [isOpen, setIsOpen] = useState(false);

  const toggleChat = () => {
    setIsOpen(!isOpen);
  };

  return (
    <div className="crisis-line-container">
      <button 
        className="help-line-button"
        onClick={toggleChat}
      >
        Help Line Assistant
      </button>
      
      {isOpen && <ChatWindow onClose={toggleChat} />}
    </div>
  );
};

export default CrisisLineAssistant; 