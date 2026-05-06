import { useOperatorState } from '../AdminApp';

export default function ObjectivesPage() {
  const { fullState } = useOperatorState();

  return (
    <div style={styles.container}>
      <h1 style={styles.title}>Objectives</h1>
      <div style={styles.card}>
        <p style={styles.placeholder}>
          {fullState?.objectives ? (
            `${fullState.objectives.length} objective(s) found`
          ) : (
            'No objectives data available'
          )}
        </p>
      </div>
    </div>
  );
}

const styles = {
  container: {
    maxWidth: '800px',
  },
  title: {
    margin: '0 0 2rem 0',
    color: '#ff6b35',
    fontSize: '1.5rem',
    fontWeight: 'bold',
  },
  card: {
    backgroundColor: '#1a1f3a',
    border: '1px solid #2a3050',
    borderRadius: '4px',
    padding: '1.5rem',
  },
  placeholder: {
    color: '#b0c4e4',
    margin: 0,
  },
};
