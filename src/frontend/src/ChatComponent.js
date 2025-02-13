import React from 'react';
import './css/ChatComponent.css'; // Import the CSS file

const ChatComponent = () => {
  const openChatWindow = () => {
    window.open('/chat', 'ChatWindow', 'width=600,height=400');
  };

  return (
    <div>
      <button onClick={openChatWindow}>Open Chat</button>
    </div>
  );
};

export default ChatComponent;