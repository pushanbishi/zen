import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './css/ChatComponent.css'; // Import the CSS file

const ChatWindow = () => {
  const [messages, setMessages] = useState([]);
  const [userInput, setUserInput] = useState('');
  const [initialPromptFetched, setInitialPromptFetched] = useState(false);

  useEffect(() => {
    const fetchInitialPrompt = async () => {
      try {
        const sysPromptResponse = await axios.get('http://127.0.0.1:5001/config?key=system_prompt');
        const userPromptResponse = await axios.get('http://127.0.0.1:5001/config?key=user_prompt');
        const sysPrompt = sysPromptResponse.data;
        const userPrompt = userPromptResponse.data;

        const initialMessage = [{ role: 'system', content: sysPrompt }];
        const chatResponse = await axios.post('http://127.0.0.1:5001/chat', {
          user_input: userPrompt,
          messages: initialMessage,
        });

        const { response: aiResponse, messages: updatedMessages } = chatResponse.data;
        setMessages(updatedMessages);
        setInitialPromptFetched(true);
      } catch (error) {
        console.error('Error fetching initial prompt:', error);
      }
    };

    if (!initialPromptFetched) {
      fetchInitialPrompt();
    }
  }, [initialPromptFetched]);

  const handleSend = async () => {
    if (userInput.toLowerCase() === 'exit') {
      alert('Ending the conversation. Take care!');
      return;
    }

    try {
      const response = await axios.post('http://127.0.0.1:5001/chat', {
        user_input: userInput,
        messages: messages,
      });

      const { response: aiResponse, messages: updatedMessages } = response.data;
      setMessages(updatedMessages);
      setUserInput('');
    } catch (error) {
      console.error('Error sending message:', error);
    }
  };

  return (
    <div className="chat-container">
      <div>
        {messages.slice(2).map((msg, index) => (
          <div key={index} className={`message ${msg.role}`}>
            <strong>{msg.role}:</strong> {msg.content}
          </div>
        ))}
      </div>
      <div className="input-container">
        <input
          type="text"
          value={userInput}
          onChange={(e) => setUserInput(e.target.value)}
          placeholder="Type your message..."
        />
        <button onClick={handleSend}>Send</button>
      </div>
    </div>
  );
};

export default ChatWindow;