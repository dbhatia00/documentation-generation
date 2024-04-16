// frontend/src/App.js
import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route } from "react-router-dom";
import './App.css';
import Home from './Home';
import DocumentPage from './DocumentPage';


function App() {
  
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="docpage" element={<DocumentPage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
