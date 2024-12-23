import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './css/ChatComponent.css'; // Import the CSS file

const ChatComponent = () => {
  const [messages, setMessages] = useState([]);
  const [userInput, setUserInput] = useState('');
  const [initialPromptFetched, setInitialPromptFetched] =
  (false);

  useEffect(() => {
    const fetchInitialPrompt = async () => {
      try {
        const response = await axios.get('http://127.0.0.1:5001/config?key=initial_prompt');
        const initialPrompt = response.data;
        const initialMessages = [{ role: 'system', content: initialPrompt }];
        setMessages(initialMessages);
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
    if (userInput.trim() === '') {
      return;
    }

    if (userInput.toLowerCase() === 'exit') {
      alert('Ending the conversation. Take care!');
      return;
    }

    const newMessages = [...messages, { role: 'user', content: userInput }];
    setMessages(newMessages);

    try {
      const response = await axios.post('http://127.0.0.1:5001/chat', {
        user_input: userInput,
        messages: newMessages,
      });

      const { response: aiResponse, messages: updatedMessages } = response.data;
      setMessages(updatedMessages);
      setUserInput('');
    } catch (error) {
      console.error('Error sending message:', error);
    }
  };

  return (
    <div>
      <div>
        {messages.map((msg, index) => (
          <div key={index} className={msg.role}>
            <strong>{msg.role}:</strong> {msg.content}
          </div>
        ))}
      </div>
      <input
        type="text"
        value={userInput}
        onChange={(e) => setUserInput(e.target.value)}
        placeholder="Type your message..."
      />
      <button onClick={handleSend}>Send</button>
    </div>
  );
};

export default ChatComponent;