import React, { useState } from 'react';
import '../styles/QueryForm.css';

const QueryForm = ({ onSubmit, loading }) => {
  const [query, setQuery] = useState('');
  const [agentLevel, setAgentLevel] = useState(1);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (query.trim()) {
      onSubmit(query, agentLevel);
    }
  };

  return (
    <div className="query-form-container">
      <div className="form-card">
        <h2>Project SHADOW</h2>
        <p className="subtitle">Intelligence Retrieval System</p>
        
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="agent-level">Agent Level:</label>
            <select 
              id="agent-level" 
              value={agentLevel} 
              onChange={(e) => setAgentLevel(Number(e.target.value))}
              disabled={loading}
              className="agent-level-select"
            >
              <option value={1}>Level 1 - Novice Operative (Shadow Footprint)</option>
              <option value={2}>Level 2 - Tactical Specialist (Iron Claw)</option>
              <option value={3}>Level 3 - Covert Strategist (Phantom Mind)</option>
              <option value={4}>Level 4 - Field Commander (Omega Hawk)</option>
              <option value={5}>Level 5 - Intelligence Overlord (Silent Whisper)</option>
            </select>
          </div>
          
          <div className="form-group">
            <label htmlFor="query">Enter Your Query:</label>
            <textarea
              id="query"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="What is the status of Operation Phantom Veil, and what are the recommended counter-surveillance techniques?"
              rows={4}
              disabled={loading}
              className="query-textarea"
            />
          </div>
          
          <button 
            type="submit" 
            disabled={loading || !query.trim()} 
            className="submit-button"
          >
            {loading ? 'Processing...' : 'Submit Query'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default QueryForm;