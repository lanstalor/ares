import { useState, useEffect } from 'react';

export default function EntityModal({
  isOpen,
  title,
  entity,
  fields = [],
  onSave,
  onCancel,
  isLoading = false,
  error = null,
}) {
  const [formData, setFormData] = useState({});

  useEffect(() => {
    if (entity) {
      const initialData = {};
      fields.forEach((field) => {
        initialData[field.key] = entity[field.key] ?? '';
      });
      setFormData(initialData);
    } else {
      const initialData = {};
      fields.forEach((field) => {
        initialData[field.key] = field.defaultValue ?? '';
      });
      setFormData(initialData);
    }
  }, [entity, fields, isOpen]);

  if (!isOpen) {
    return null;
  }

  function handleSubmit(e) {
    e.preventDefault();
    onSave(formData);
  }

  function handleFieldChange(key, value, fieldType) {
    if (fieldType === 'checkbox') {
      setFormData({ ...formData, [key]: !formData[key] });
    } else if (fieldType === 'number') {
      setFormData({ ...formData, [key]: parseFloat(value) || 0 });
    } else {
      setFormData({ ...formData, [key]: value });
    }
  }

  return (
    <>
      <div style={styles.overlay} onClick={onCancel} />
      <div style={styles.modal}>
        <div style={styles.header}>
          <h2 style={styles.title}>{title}</h2>
          <button
            onClick={onCancel}
            style={styles.closeButton}
            aria-label="Close modal"
          >
            ✕
          </button>
        </div>

        {error && <div style={styles.error}>{error}</div>}

        <form onSubmit={handleSubmit} style={styles.form}>
          {fields.map((field) => (
            <div key={field.key} style={styles.fieldGroup}>
              <label htmlFor={field.key} style={styles.label}>
                {field.label}
              </label>

              {field.type === 'text' && (
                <input
                  id={field.key}
                  type="text"
                  value={formData[field.key] || ''}
                  onChange={(e) =>
                    handleFieldChange(field.key, e.target.value, 'text')
                  }
                  style={styles.input}
                  disabled={isLoading}
                />
              )}

              {field.type === 'number' && (
                <input
                  id={field.key}
                  type="number"
                  value={formData[field.key] || 0}
                  onChange={(e) =>
                    handleFieldChange(field.key, e.target.value, 'number')
                  }
                  style={styles.input}
                  disabled={isLoading}
                />
              )}

              {field.type === 'textarea' && (
                <textarea
                  id={field.key}
                  value={formData[field.key] || ''}
                  onChange={(e) =>
                    handleFieldChange(field.key, e.target.value, 'textarea')
                  }
                  style={styles.textarea}
                  rows={field.rows || 4}
                  disabled={isLoading}
                />
              )}

              {field.type === 'checkbox' && (
                <div style={styles.checkboxContainer}>
                  <input
                    id={field.key}
                    type="checkbox"
                    checked={formData[field.key] || false}
                    onChange={() =>
                      handleFieldChange(field.key, null, 'checkbox')
                    }
                    style={styles.checkbox}
                    disabled={isLoading}
                  />
                  <span style={styles.checkboxLabel}>
                    {field.checkboxLabel || 'Yes'}
                  </span>
                </div>
              )}

              {field.type === 'select' && field.options && (
                <select
                  id={field.key}
                  value={formData[field.key] || ''}
                  onChange={(e) =>
                    handleFieldChange(field.key, e.target.value, 'select')
                  }
                  style={styles.select}
                  disabled={isLoading}
                >
                  <option value="">— Select {field.label} —</option>
                  {field.options.map((opt) => (
                    <option key={opt.value} value={opt.value}>
                      {opt.label}
                    </option>
                  ))}
                </select>
              )}
            </div>
          ))}

          <div style={styles.actions}>
            <button
              type="button"
              onClick={onCancel}
              style={{...styles.button, ...styles.buttonSecondary}}
              disabled={isLoading}
            >
              Cancel
            </button>
            <button
              type="submit"
              style={{...styles.button, ...styles.buttonPrimary}}
              disabled={isLoading}
            >
              {isLoading ? 'Saving...' : 'Save'}
            </button>
          </div>
        </form>
      </div>
    </>
  );
}

const styles = {
  overlay: {
    position: 'fixed',
    inset: 0,
    backgroundColor: 'rgba(0, 0, 0, 0.7)',
    zIndex: 999,
  },
  modal: {
    position: 'fixed',
    top: '50%',
    left: '50%',
    transform: 'translate(-50%, -50%)',
    backgroundColor: '#1a1f3a',
    border: '2px solid #ff6b35',
    borderRadius: '4px',
    maxWidth: '500px',
    width: '90%',
    maxHeight: '90vh',
    overflow: 'auto',
    zIndex: 1000,
    boxShadow: '0 20px 60px rgba(255, 107, 53, 0.2)',
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '1.5rem',
    borderBottom: '1px solid #2a3050',
  },
  title: {
    margin: 0,
    color: '#ff6b35',
    fontSize: '1.25rem',
    fontWeight: 'bold',
  },
  closeButton: {
    backgroundColor: 'transparent',
    border: 'none',
    color: '#ff6b35',
    fontSize: '1.5rem',
    cursor: 'pointer',
    padding: '0',
    width: '2rem',
    height: '2rem',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  },
  form: {
    padding: '1.5rem',
    display: 'flex',
    flexDirection: 'column',
    gap: '1.5rem',
  },
  fieldGroup: {
    display: 'flex',
    flexDirection: 'column',
    gap: '0.5rem',
  },
  label: {
    color: '#b0c4e4',
    fontSize: '0.75rem',
    textTransform: 'uppercase',
    letterSpacing: '1px',
    fontWeight: 'bold',
  },
  input: {
    padding: '0.75rem',
    backgroundColor: '#0f1428',
    border: '1px solid #2a3050',
    borderRadius: '2px',
    color: '#e5eaf1',
    fontFamily: '"VT323", monospace',
    fontSize: '0.9rem',
  },
  textarea: {
    padding: '0.75rem',
    backgroundColor: '#0f1428',
    border: '1px solid #2a3050',
    borderRadius: '2px',
    color: '#e5eaf1',
    fontFamily: '"VT323", monospace',
    fontSize: '0.9rem',
    fontWeight: 'normal',
    resize: 'vertical',
  },
  select: {
    padding: '0.75rem',
    backgroundColor: '#0f1428',
    border: '1px solid #2a3050',
    borderRadius: '2px',
    color: '#e5eaf1',
    fontFamily: '"VT323", monospace',
    fontSize: '0.9rem',
  },
  checkboxContainer: {
    display: 'flex',
    alignItems: 'center',
    gap: '0.75rem',
  },
  checkbox: {
    width: '1.25rem',
    height: '1.25rem',
    cursor: 'pointer',
    accentColor: '#ff6b35',
  },
  checkboxLabel: {
    color: '#e5eaf1',
  },
  actions: {
    display: 'flex',
    gap: '1rem',
    justifyContent: 'flex-end',
    paddingTop: '1rem',
    borderTop: '1px solid #2a3050',
  },
  button: {
    padding: '0.75rem 1.5rem',
    border: 'none',
    borderRadius: '2px',
    fontFamily: '"VT323", monospace',
    fontSize: '0.875rem',
    fontWeight: 'bold',
    cursor: 'pointer',
    textTransform: 'uppercase',
    letterSpacing: '1px',
    transition: 'all 0.2s',
  },
  buttonPrimary: {
    backgroundColor: '#ff6b35',
    color: '#0a0e27',
  },
  buttonSecondary: {
    backgroundColor: 'transparent',
    border: '1px solid #ff6b35',
    color: '#ff6b35',
  },
  error: {
    margin: '1rem',
    padding: '1rem',
    backgroundColor: 'rgba(255, 107, 53, 0.1)',
    border: '1px solid #ff6b35',
    borderRadius: '2px',
    color: '#ff8b92',
    fontSize: '0.875rem',
  },
};
