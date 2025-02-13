import React from 'react';
import ReactDOM from 'react-dom';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import ChatComponent from './ChatComponent';
import ChatWindow from './ChatWindow';
import './css/index.css';

ReactDOM.render(
  <Router>
    <Routes>
      <Route path="/" element={<ChatComponent />} />
      <Route path="/chat" element={<ChatWindow />} />
    </Routes>
  </Router>,
  document.getElementById('root')
);