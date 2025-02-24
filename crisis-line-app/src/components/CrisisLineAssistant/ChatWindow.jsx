import React, { useState, useRef, useEffect } from 'react';
import './ChatWindow.css';

const ChatWindow = ({ onClose }) => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [systemPrompt, setSystemPrompt] = useState('');
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    // Only fetch and store system prompt, don't show any messages yet
    const fetchSystemPrompt = async () => {
      try {
        const sysPromptResponse = await fetch('http://localhost:5001/config?key=system_prompt');
        const sysPrompt = await sysPromptResponse.text();
        setSystemPrompt(sysPrompt);
        // Start with just the welcome message
        setMessages([{
          role: 'assistant',
          content: 'Hello! How can I help you today?'
        }]);
      } catch (error) {
        console.error('Error fetching system prompt:', error);
        // If error, still show welcome message
        setMessages([{
          role: 'assistant',
          content: 'Hello! How can I help you today?'
        }]);
      }
    };

    fetchSystemPrompt();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!inputMessage.trim()) return;

    setIsLoading(true);

    try {
      // Always include system prompt and all previous messages except initial greeting
      const apiMessages = [
        { role: 'system', content: systemPrompt },
        ...messages.slice(1)  // Skip initial greeting but keep all other messages
      ];

      console.log('Messages being sent to API:', apiMessages);

      const response = await fetch('http://localhost:5001/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_input: inputMessage,
          messages: apiMessages,
        }),
      });

      const data = await response.json();
      // Only add the new messages (user input and assistant response)
      const newMessages = data.messages.slice(-2);
      setMessages(prev => [...prev, ...newMessages]);
      setInputMessage('');
    } catch (error) {
      console.error('Error:', error);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Sorry, there was an error processing your message.'
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="chat-window">
      <div className="chat-header">
        <h3>Help Line Assistant</h3>
        <button className="close-button" onClick={onClose}>×</button>
      </div>
      
      <div className="messages-container">
        {messages.map((message, index) => (
          <div 
            key={index} 
            className={`message ${message.role === 'user' ? 'user-message' : 'assistant-message'}`}
          >
            {message.content}
          </div>
        ))}
        {isLoading && (
          <div className="message assistant-message loading">
            <div className="typing-indicator">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSubmit} className="input-form">
        <input
          type="text"
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          placeholder="Type your message here..."
          disabled={isLoading}
        />
        <button type="submit" disabled={isLoading}>
          Send
        </button>
      </form>
    </div>
  );
};

export default ChatWindow; 