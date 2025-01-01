import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './css/ChatComponent.css'; // Import the CSS file

const ChatComponent = () => {
  const [messages, setMessages] = useState([]);
  const [userInput, setUserInput] = useState('');
  const [initialPromptFetched, setInitialPromptFetched] = useState(false);

  useEffect(() => {
    const fetchInitialPrompt = async () => {
      try {
        const response = await axios.get('http://127.0.0.1:5001/config?key=initial_prompt');
        const initialPrompt = response.data;
        console.log('Initial prompt response:', initialPrompt);
        const initialMessages = [{ role: 'system', content: initialPrompt }];
        console.log('initialMessages :', initialMessages);

        // Call the /chat service with the initial prompt
        const chatResponse = await axios.post('http://127.0.0.1:5001/chat', {
          //user_input: '',
          messages: initialMessages,
        });

        console.log('Initial chat response:', chatResponse.data);

        const { response: aiResponse, messages: updatedMessages } = chatResponse.data;
        //console.log('response is:', aiResponse);
        //console.log('messages is:', updatedMessages);
        setMessages(updatedMessages.filter(msg => msg.role !== 'system'));
        //console.log('messages after filter:', updatedMessages);

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
      //console.log('Sending message:', userInput);
      //console.log('Sending messages:', messages);
      const response = await axios.post('http://127.0.0.1:5001/chat', {
        user_input: userInput,
        messages: messages,
      });

      //console.log('----Before Adding  to messages --- 2 ', messages.length);
      const { response: aiResponse, messages: updatedMessages } = response.data;
      //console.log('Messages from response.data:----2', updatedMessages);
      setMessages(updatedMessages.filter(msg => msg.role !== 'system'));
      //console.log('----After Adding  to messages --- 2 ', messages.length);
      //console.log('Messages after filtering:', messages);
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