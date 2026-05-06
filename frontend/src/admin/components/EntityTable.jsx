export default function EntityTable({
  entities = [],
  columns = [],
  onEditRow,
  onDeleteRow,
}) {
  if (!entities || entities.length === 0) {
    return (
      <div style={styles.emptyState}>
        <p>No entities found</p>
      </div>
    );
  }

  return (
    <div style={styles.tableContainer}>
      <table style={styles.table}>
        <thead>
          <tr style={styles.headerRow}>
            {columns.map((col) => (
              <th key={col.key} style={{
                ...styles.headerCell,
                width: col.width || 'auto',
              }}>
                {col.label}
              </th>
            ))}
            <th style={styles.headerCell}>Actions</th>
          </tr>
        </thead>
        <tbody>
          {entities.map((entity, index) => (
            <tr key={entity.id || index} style={styles.row}>
              {columns.map((col) => (
                <td key={col.key} style={styles.cell}>
                  {renderCellValue(entity[col.key], col.type)}
                </td>
              ))}
              <td style={styles.actionsCell}>
                {onEditRow && (
                  <button
                    onClick={() => onEditRow(entity)}
                    style={styles.actionButton}
                  >
                    Edit
                  </button>
                )}
                {onDeleteRow && (
                  <button
                    onClick={() => onDeleteRow(entity.id)}
                    style={{...styles.actionButton, ...styles.deleteButton}}
                  >
                    Delete
                  </button>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function renderCellValue(value, type) {
  if (value === null || value === undefined) {
    return <span style={styles.muted}>—</span>;
  }

  if (type === 'boolean') {
    return <span style={styles.boolean}>{value ? 'Yes' : 'No'}</span>;
  }

  if (type === 'json' && typeof value === 'object') {
    return <span style={styles.muted}>{JSON.stringify(value)}</span>;
  }

  if (typeof value === 'string' && value.length > 50) {
    return <span>{value.substring(0, 50)}...</span>;
  }

  return <span>{String(value)}</span>;
}

const styles = {
  tableContainer: {
    overflowX: 'auto',
    marginTop: '1.5rem',
  },
  table: {
    width: '100%',
    borderCollapse: 'collapse',
    fontFamily: '"VT323", monospace',
    fontSize: '0.875rem',
  },
  headerRow: {
    backgroundColor: '#0f1428',
    borderBottom: '2px solid #ff6b35',
  },
  headerCell: {
    padding: '1rem',
    textAlign: 'left',
    color: '#ff6b35',
    fontWeight: 'bold',
    textTransform: 'uppercase',
    letterSpacing: '0.5px',
  },
  row: {
    borderBottom: '1px solid #2a3050',
  },
  cell: {
    padding: '0.875rem 1rem',
    color: '#e5eaf1',
  },
  muted: {
    color: '#8793a0',
  },
  boolean: {
    color: '#78c89e',
  },
  actionsCell: {
    padding: '0.875rem 1rem',
    display: 'flex',
    gap: '0.5rem',
  },
  actionButton: {
    padding: '0.5rem 0.75rem',
    backgroundColor: 'transparent',
    border: '1px solid #ff6b35',
    color: '#ff6b35',
    fontFamily: '"VT323", monospace',
    fontSize: '0.75rem',
    cursor: 'pointer',
    borderRadius: '2px',
    textTransform: 'uppercase',
    letterSpacing: '0.5px',
  },
  deleteButton: {
    borderColor: '#ff8b92',
    color: '#ff8b92',
  },
  emptyState: {
    padding: '2rem',
    textAlign: 'center',
    color: '#8793a0',
    backgroundColor: '#1a1f3a',
    border: '1px solid #2a3050',
    borderRadius: '4px',
  },
};
