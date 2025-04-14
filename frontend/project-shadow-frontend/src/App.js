import React, { useState } from 'react';
import './styles/App.css';
import QueryForm from './components/QueryForm';
import ResponseDisplay from './components/ResponseDisplay';
import Header from './components/Header';
import Footer from './components/Footer';

function App() {
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleQuerySubmit = async (query, agentLevel) => {
    setLoading(true);
    setError(null);
    
    try {
      const res = await fetch('http://localhost:5000/api/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query, agentLevel }),
      });
      
      const data = await res.json();
      
      if (!res.ok) {
        throw new Error(data.message || 'An error occurred');
      }
      
      setResponse(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <Header />
      <main className="main-content">
        <QueryForm onSubmit={handleQuerySubmit} loading={loading} />
        <ResponseDisplay 
          response={response} 
          loading={loading} 
          error={error}
        />
      </main>
      <Footer />
    </div>
  );
}

export default App;