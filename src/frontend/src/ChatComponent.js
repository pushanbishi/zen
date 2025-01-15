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
        console.log('Before getting Initial prompt response:');
        const response = await axios.get('http://127.0.0.1:5001/config?key=initial_prompt');
        const initialPrompt = response.data;
        console.log('Initial prompt response:', initialPrompt);
        const initialMessage = [{ role: 'system', content: initialPrompt }];
        console.log('Before initial call to chat:', initialMessage);

        // Call the /chat service with the initial prompt
        const chatResponse = await axios.post('http://127.0.0.1:5001/chat', {
          //user_input: '',
          messages: initialMessage,
        });

        console.log('Initial chat response:', chatResponse.data);

        const { response: aiResponse, messages: updatedMessages } = chatResponse.data;
        console.log('Before filtering in init block after assigning to updatedMessages:', updatedMessages.length);
        //setMessages(updatedMessages.filter(msg => msg.role !== 'system'));
        setMessages(updatedMessages);

        console.log('updatedMessages after filter -- Init Block:', updatedMessages);
        console.log('messages after filter: -- Init Block', messages);


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
      console.log('Sending userInput message to chat end point', userInput);
      console.log('Sending messages to chat end point ', messages);
      const response = await axios.post('http://127.0.0.1:5001/chat', {
        user_input: userInput,
        messages: messages,
      });

      console.log('----assigning  messages to updatedMessages ,  messages:: ', messages);
      const { response: aiResponse, messages: updatedMessages } = response.data;
      console.log('Messages from response.data after assignment :----', updatedMessages);
      setMessages(updatedMessages.filter(msg => msg.role !== 'system'));
      console.log('----After filtering out updated Messages messages is: ', messages.length);
      setUserInput('');
      console.log('----After setting userInput: ', userInput);



    } catch (error) {
      console.error('Error sending message:', error);
    }
  };

  console.log('About to render, messages count ', messages.length);

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
        onChange={(e) => {
          setUserInput(e.target.value);
        }}
        placeholder="Type your message..."
      />
      <button onClick={handleSend}>Send</button>
    </div>
  );
};

export default ChatComponent;