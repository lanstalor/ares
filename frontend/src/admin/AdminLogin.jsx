import { useState } from 'react';

export default function AdminLogin({ onTokenSubmit, isLoading, error }) {
  const [token, setToken] = useState('');

  function handleSubmit(e) {
    e.preventDefault();
    if (token.trim()) {
      onTokenSubmit(token);
    }
  }

  return (
    <div style={styles.container}>
      <div style={styles.panel}>
        <h1 style={styles.heading}>Operator Access</h1>

        <form onSubmit={handleSubmit} style={styles.form}>
          <div style={styles.inputGroup}>
            <label htmlFor="token-input" style={styles.label}>
              Authentication Token
            </label>
            <input
              id="token-input"
              type="password"
              value={token}
              onChange={(e) => setToken(e.target.value)}
              placeholder="Enter operator token"
              style={styles.input}
              disabled={isLoading}
              autoFocus
            />
          </div>

          {error && (
            <div style={styles.error}>
              {error}
            </div>
          )}

          <button
            type="submit"
            style={{
              ...styles.button,
              opacity: isLoading ? 0.6 : 1,
              cursor: isLoading ? 'not-allowed' : 'pointer',
            }}
            disabled={isLoading}
          >
            {isLoading ? 'Authenticating...' : 'Submit'}
          </button>
        </form>

        <p style={styles.hint}>
          Enter your operator authentication token to access the admin interface.
        </p>
      </div>
    </div>
  );
}

const styles = {
  container: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: '100vh',
    padding: '2rem',
    backgroundColor: '#0a0e27',
    fontFamily: '"VT323", monospace',
  },
  panel: {
    backgroundColor: '#1a1f3a',
    border: '2px solid #ff6b35',
    borderRadius: '4px',
    padding: '3rem',
    maxWidth: '400px',
    width: '100%',
    boxShadow: '0 8px 32px rgba(255, 107, 53, 0.15)',
  },
  heading: {
    margin: '0 0 2rem 0',
    color: '#ff6b35',
    fontSize: '1.75rem',
    fontWeight: 'bold',
    textAlign: 'center',
    letterSpacing: '2px',
  },
  form: {
    display: 'flex',
    flexDirection: 'column',
    gap: '1.5rem',
  },
  inputGroup: {
    display: 'flex',
    flexDirection: 'column',
    gap: '0.75rem',
  },
  label: {
    color: '#b0c4e4',
    fontSize: '0.875rem',
    fontWeight: '500',
    textTransform: 'uppercase',
    letterSpacing: '1px',
  },
  input: {
    padding: '0.875rem',
    backgroundColor: '#0f1428',
    border: '1px solid #ff6b35',
    borderRadius: '2px',
    color: '#e5eaf1',
    fontFamily: '"VT323", monospace',
    fontSize: '1rem',
    transition: 'border-color 0.2s, box-shadow 0.2s',
    outline: 'none',
  },
  error: {
    padding: '1rem',
    backgroundColor: 'rgba(255, 107, 53, 0.1)',
    border: '1px solid #ff6b35',
    borderRadius: '2px',
    color: '#ff8b92',
    fontSize: '0.875rem',
    textAlign: 'center',
  },
  button: {
    padding: '0.875rem',
    backgroundColor: '#ff6b35',
    border: 'none',
    borderRadius: '2px',
    color: '#0a0e27',
    fontSize: '1rem',
    fontWeight: 'bold',
    textTransform: 'uppercase',
    letterSpacing: '1px',
    fontFamily: '"VT323", monospace',
    transition: 'background-color 0.2s, transform 0.1s',
    marginTop: '0.5rem',
  },
  hint: {
    marginTop: '1.5rem',
    color: '#8793a0',
    fontSize: '0.75rem',
    textAlign: 'center',
    lineHeight: '1.5',
  },
};
