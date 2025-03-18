import React, { useState, useRef, useEffect } from 'react';
import './ChatWindow.css';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://crisisline-prod.eba-cgc82pc6.us-east-1.elasticbeanstalk.com';
const formatMessage = (content) => {
  return content
    // Convert newlines to <br> tags
    .split('\n')
    .map((line, i) => (
      <React.Fragment key={i}>
        {/* Handle bullet points and numbered lists */}
        {line.match(/^[•\-\d]+\.?\s/) 
          ? <div className="list-item">{line}</div>
          : line}
        <br />
      </React.Fragment>
    ));
};

const ChatWindow = ({ onClose }) => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [systemPrompt, setSystemPrompt] = useState('');
  const [defaultPrompt, setDefaultPrompt] = useState('');
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    // Fetch both system prompt and default AI prompt
    const fetchPrompts = async () => {
      try {
        const [sysPromptResponse, defaultPromptResponse] = await Promise.all([
          fetch(`${API_BASE_URL}/config?key=system_prompt`),
          fetch(`${API_BASE_URL}/config?key=default_ai_prompt`)
        ]);

        const sysPrompt = await sysPromptResponse.text();
        const defaultPrompt = await defaultPromptResponse.text();

        setSystemPrompt(sysPrompt);
        setDefaultPrompt(defaultPrompt);
        
        // Start with just the welcome message
        setMessages([{
          role: 'assistant',
          msg_type: 'welcome',
          content: defaultPrompt
        }]);
      } catch (error) {
        console.error('Error fetching prompts:', error);
        // If error,  show harcoded welcome message
        setMessages([{
          role: 'assistant',
          msg_type: 'welcome',
          content: 'Hello! How can I help you today?'
        }]);
      }
    };

    fetchPrompts();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    console.log("API URL:", process.env.REACT_APP_API_URL);
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!inputMessage.trim()) return;

    console.log("Messages before adding user message:", messages);
    // Add user's message to UI
   // const updatedMessages = [
     // ...messages,
      //{ role: 'user', content: inputMessage }
    //];
    const updatedMessages = [
      ...messages];
    setMessages(updatedMessages);
    
    setIsLoading(true);

    try {
      // Filter out welcome message for API call
      const apiMessages = [
        { role: 'system', content: systemPrompt },
        ...updatedMessages.filter(msg => msg.msg_type !== 'welcome')
      ];

      console.log('Messages being sent to API:', apiMessages);

      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_input: inputMessage,
          messages: apiMessages,
        }),
      });

     
      const jsondata = await response.json();
      console.log("Response data from API:", jsondata.messages);
      
      // Preserve welcome message when updating UI with API response
      if (jsondata.messages) {
        // Get all messages except system prompt
        const newMessages = jsondata.messages.filter(msg => msg.role !== 'system');
        console.log("New messages from API:", newMessages);
        console.log("Messages before updating:", messages);
        // If we have a welcome message, make sure it's preserved
        if (messages.length > 0 && 
            messages[0].msg_type === 'welcome') {
          // Include welcome message at beginning + all other messages
          setMessages([messages[0], ...newMessages]);
          console.log("Messages after updating:", messages);
        } else {
          // No welcome message to preserve
          setMessages(newMessages);
        }
      }
      
      setInputMessage('');
    } catch (error) {
      console.error('Error:', error);
      setMessages([...updatedMessages, {
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
            {formatMessage(message.content)}
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