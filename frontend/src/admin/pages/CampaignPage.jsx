import { useState, useEffect } from 'react';
import { useOperatorState } from '../AdminApp';

export default function CampaignPage() {
  const { fullState, api, campaignId } = useOperatorState();
  const [isEditing, setIsEditing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    tagline: '',
    current_date_pce: '',
    current_location_label: '',
  });

  // Initialize form data from fullState
  useEffect(() => {
    if (fullState) {
      setFormData({
        name: fullState.name || '',
        tagline: fullState.tagline || '',
        current_date_pce: fullState.current_date_pce || '',
        current_location_label: fullState.current_location_label || '',
      });
    }
  }, [fullState]);

  async function handleSave() {
    setIsSaving(true);
    setError(null);

    try {
      const updates = {
        name: formData.name,
        tagline: formData.tagline,
        current_date_pce: formData.current_date_pce,
        current_location_label: formData.current_location_label,
      };

      await api.patchState(campaignId, updates);

      // Refresh the full state
      const updatedState = await api.getFullState(campaignId);
      setFormData({
        name: updatedState.name || '',
        tagline: updatedState.tagline || '',
        current_date_pce: updatedState.current_date_pce || '',
        current_location_label: updatedState.current_location_label || '',
      });

      setIsEditing(false);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsSaving(false);
    }
  }

  if (!fullState) {
    return (
      <div style={styles.container}>
        <p>Loading campaign data...</p>
      </div>
    );
  }

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h1 style={styles.title}>Campaign Editor</h1>
        <button
          onClick={() => {
            if (isEditing) {
              // Reset form
              setFormData({
                name: fullState.name || '',
                tagline: fullState.tagline || '',
                current_date_pce: fullState.current_date_pce || '',
                current_location_label: fullState.current_location_label || '',
              });
            }
            setIsEditing(!isEditing);
          }}
          style={{
            ...styles.button,
            ...(isEditing ? styles.buttonDanger : styles.buttonPrimary),
          }}
        >
          {isEditing ? 'Cancel' : 'Edit'}
        </button>
      </div>

      {error && <div style={styles.error}>{error}</div>}

      <div style={styles.card}>
        {!isEditing ? (
          // Display mode
          <div style={styles.displayMode}>
            <div style={styles.field}>
              <label style={styles.label}>Campaign Name</label>
              <p style={styles.value}>{fullState.name || '—'}</p>
            </div>
            <div style={styles.field}>
              <label style={styles.label}>Tagline</label>
              <p style={styles.value}>{fullState.tagline || '—'}</p>
            </div>
            <div style={styles.field}>
              <label style={styles.label}>Current Date (PCE)</label>
              <p style={styles.value}>{fullState.current_date_pce || '—'}</p>
            </div>
            <div style={styles.field}>
              <label style={styles.label}>Current Location Label</label>
              <p style={styles.value}>{fullState.current_location_label || '—'}</p>
            </div>
          </div>
        ) : (
          // Edit mode
          <form style={styles.form}>
            <div style={styles.formGroup}>
              <label htmlFor="name" style={styles.label}>
                Campaign Name
              </label>
              <input
                id="name"
                type="text"
                value={formData.name}
                onChange={(e) =>
                  setFormData({ ...formData, name: e.target.value })
                }
                style={styles.input}
              />
            </div>

            <div style={styles.formGroup}>
              <label htmlFor="tagline" style={styles.label}>
                Tagline
              </label>
              <textarea
                id="tagline"
                value={formData.tagline}
                onChange={(e) =>
                  setFormData({ ...formData, tagline: e.target.value })
                }
                style={styles.textarea}
                rows={3}
              />
            </div>

            <div style={styles.formGroup}>
              <label htmlFor="date" style={styles.label}>
                Current Date (PCE)
              </label>
              <input
                id="date"
                type="text"
                value={formData.current_date_pce}
                onChange={(e) =>
                  setFormData({ ...formData, current_date_pce: e.target.value })
                }
                style={styles.input}
              />
            </div>

            <div style={styles.formGroup}>
              <label htmlFor="location" style={styles.label}>
                Current Location Label
              </label>
              <input
                id="location"
                type="text"
                value={formData.current_location_label}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    current_location_label: e.target.value,
                  })
                }
                style={styles.input}
              />
            </div>

            <button
              type="button"
              onClick={handleSave}
              disabled={isSaving}
              style={{
                ...styles.button,
                ...styles.buttonPrimary,
                opacity: isSaving ? 0.6 : 1,
              }}
            >
              {isSaving ? 'Saving...' : 'Save Changes'}
            </button>
          </form>
        )}
      </div>
    </div>
  );
}

const styles = {
  container: {
    maxWidth: '600px',
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '2rem',
    borderBottom: '1px solid #2a3050',
    paddingBottom: '1rem',
  },
  title: {
    margin: 0,
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
  displayMode: {
    display: 'flex',
    flexDirection: 'column',
    gap: '1.5rem',
  },
  field: {
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
  value: {
    margin: 0,
    color: '#e5eaf1',
    fontSize: '1rem',
  },
  form: {
    display: 'flex',
    flexDirection: 'column',
    gap: '1.5rem',
  },
  formGroup: {
    display: 'flex',
    flexDirection: 'column',
    gap: '0.5rem',
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
  buttonDanger: {
    backgroundColor: 'transparent',
    border: '1px solid #ff6b35',
    color: '#ff6b35',
  },
  error: {
    padding: '1rem',
    backgroundColor: 'rgba(255, 107, 53, 0.1)',
    border: '1px solid #ff6b35',
    borderRadius: '2px',
    color: '#ff8b92',
    marginBottom: '1.5rem',
  },
};
