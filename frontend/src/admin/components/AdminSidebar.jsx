export default function AdminSidebar({ activePage, onPageChange, onLogout }) {
  const pages = [
    { id: 'Campaign', label: 'Campaign' },
    { id: 'Objectives', label: 'Objectives' },
    { id: 'Clocks', label: 'Clocks' },
    { id: 'Secrets', label: 'Secrets' },
    { id: 'NPCs', label: 'NPCs' },
  ];

  return (
    <aside style={styles.sidebar}>
      <div style={styles.header}>
        <h2 style={styles.title}>Operator</h2>
        <p style={styles.subtitle}>Admin Console</p>
      </div>

      <nav style={styles.nav}>
        {pages.map((page) => (
          <button
            key={page.id}
            onClick={() => onPageChange(page.id)}
            style={{
              ...styles.navButton,
              ...(activePage === page.id ? styles.navButtonActive : {}),
            }}
          >
            {page.label}
          </button>
        ))}
      </nav>

      <div style={styles.footer}>
        <button onClick={onLogout} style={styles.logoutButton}>
          Logout
        </button>
      </div>
    </aside>
  );
}

const styles = {
  sidebar: {
    width: '200px',
    backgroundColor: '#1a1f3a',
    borderRight: '2px solid #ff6b35',
    display: 'flex',
    flexDirection: 'column',
    padding: '1.5rem 0',
    fontFamily: '"VT323", monospace',
    height: '100vh',
    overflow: 'hidden',
  },
  header: {
    padding: '0 1.5rem 2rem',
    borderBottom: '1px solid #2a3050',
  },
  title: {
    margin: '0 0 0.5rem 0',
    color: '#ff6b35',
    fontSize: '1.25rem',
    fontWeight: 'bold',
    letterSpacing: '1px',
  },
  subtitle: {
    margin: 0,
    color: '#8793a0',
    fontSize: '0.75rem',
    textTransform: 'uppercase',
    letterSpacing: '1px',
  },
  nav: {
    flex: 1,
    padding: '1.5rem 0',
    display: 'flex',
    flexDirection: 'column',
    gap: '0.25rem',
    overflow: 'auto',
  },
  navButton: {
    padding: '0.75rem 1.5rem',
    backgroundColor: 'transparent',
    border: 'none',
    color: '#b0c4e4',
    fontSize: '0.875rem',
    textAlign: 'left',
    cursor: 'pointer',
    transition: 'all 0.2s',
    borderLeft: '3px solid transparent',
    fontFamily: '"VT323", monospace',
    textTransform: 'uppercase',
    letterSpacing: '0.5px',
    ':hover': {
      backgroundColor: 'rgba(255, 107, 53, 0.1)',
    },
  },
  navButtonActive: {
    color: '#ff6b35',
    backgroundColor: 'rgba(255, 107, 53, 0.15)',
    borderLeft: '3px solid #ff6b35',
  },
  footer: {
    padding: '1.5rem',
    borderTop: '1px solid #2a3050',
  },
  logoutButton: {
    width: '100%',
    padding: '0.75rem',
    backgroundColor: 'rgba(255, 107, 53, 0.2)',
    border: '1px solid #ff6b35',
    color: '#ff6b35',
    fontSize: '0.875rem',
    fontFamily: '"VT323", monospace',
    cursor: 'pointer',
    textTransform: 'uppercase',
    letterSpacing: '1px',
    borderRadius: '2px',
    transition: 'all 0.2s',
  },
};
