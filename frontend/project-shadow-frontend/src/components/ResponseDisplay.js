import React from 'react';
import '../styles/ResponseDisplay.css';

const ResponseDisplay = ({ response, loading, error }) => {
  if (loading) {
    return (
      <div className="response-container loading">
        <div className="loader">
          <div className="circle"></div>
          <div className="circle"></div>
          <div className="circle"></div>
        </div>
        <p>Accessing classified information...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="response-container error">
        <h3>Intelligence Retrieval Error</h3>
        <p>{error}</p>
      </div>
    );
  }

  if (!response) {
    return null;
  }

  // Handle different response statuses
  if (response.status === 'denied') {
    return (
      <div className="response-container denied">
        <h3>Access Denied</h3>
        <p>{response.message}</p>
        <div className="denied-icon">⚠️</div>
      </div>
    );
  }

  if (response.status === 'not_found') {
    return (
      <div className="response-container not-found">
        <h3>No Intelligence Found</h3>
        <p>{response.message}</p>
      </div>
    );
  }

  // Success response
  return (
    <div className="response-container success">
      <h3>Intelligence Retrieval Complete</h3>
      <div className="response-content">
        <pre>{response.response}</pre>
      </div>
      
      {response.sources && response.sources.length > 0 && (
        <div className="sources">
          <h4>Sources:</h4>
          <ul>
            {[...new Set(response.sources)].map((source, index) => (
              <li key={index}>{source}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default ResponseDisplay;