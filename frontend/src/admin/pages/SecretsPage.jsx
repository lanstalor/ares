import { useState } from 'react';
import { useOperatorState } from '../AdminApp';
import EntityTable from '../components/EntityTable';
import EntityModal from '../components/EntityModal';

export default function SecretsPage() {
  const { fullState, api, campaignId } = useOperatorState();
  const [selectedEntity, setSelectedEntity] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const secrets = fullState?.secrets || [];

  const tableData = secrets.map((secret) => ({
    ...secret,
    content_preview:
      secret.content && secret.content.length > 50
        ? secret.content.substring(0, 50) + '...'
        : secret.content || '',
  }));

  const columns = [
    { key: 'label', label: 'Label', width: '25%' },
    { key: 'status', label: 'Status', width: '15%' },
    { key: 'content_preview', label: 'Content Preview', width: '40%' },
  ];

  const fields = [
    { key: 'label', label: 'Label', type: 'text' },
    { key: 'content', label: 'Content', type: 'textarea', rows: 5 },
    {
      key: 'status',
      label: 'Status',
      type: 'select',
      options: [
        { value: 'sealed', label: 'Sealed' },
        { value: 'revealed', label: 'Revealed' },
        { value: 'suspected', label: 'Suspected' },
      ],
    },
    { key: 'reveal_condition', label: 'Reveal Condition', type: 'textarea', rows: 3 },
  ];

  function handleEditRow(entity) {
    setSelectedEntity(entity);
    setIsModalOpen(true);
    setError(null);
  }

  async function handleSave(formData) {
    setIsLoading(true);
    setError(null);

    try {
      const changes = {};
      fields.forEach((field) => {
        if (formData[field.key] !== selectedEntity[field.key]) {
          changes[field.key] = formData[field.key];
        }
      });

      if (Object.keys(changes).length === 0) {
        setIsModalOpen(false);
        setSelectedEntity(null);
        return;
      }

      await api.patchState(campaignId, {
        entity_type: 'secret',
        entity_id: selectedEntity.id,
        changes,
      });

      // Refresh full state
      const updatedState = await api.getFullState(campaignId);
      const updatedSecret = updatedState.secrets.find(
        (secret) => secret.id === selectedEntity.id
      );
      setSelectedEntity(updatedSecret);

      setIsModalOpen(false);
      setSelectedEntity(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div style={styles.container}>
      <h1 style={styles.title}>Secrets</h1>
      {error && <div style={styles.pageError}>{error}</div>}
      <EntityTable
        entities={tableData}
        columns={columns}
        onEditRow={handleEditRow}
      />
      <EntityModal
        isOpen={isModalOpen}
        title={selectedEntity ? `Edit: ${selectedEntity.label}` : 'New Secret'}
        entity={selectedEntity}
        fields={fields}
        onSave={handleSave}
        onCancel={() => {
          setIsModalOpen(false);
          setSelectedEntity(null);
          setError(null);
        }}
        isLoading={isLoading}
        error={error}
      />
    </div>
  );
}

const styles = {
  container: {
    maxWidth: '1000px',
  },
  title: {
    margin: '0 0 2rem 0',
    color: '#ff6b35',
    fontSize: '1.5rem',
    fontWeight: 'bold',
  },
  pageError: {
    marginBottom: '1.5rem',
    padding: '1rem',
    backgroundColor: 'rgba(255, 107, 53, 0.1)',
    border: '1px solid #ff6b35',
    borderRadius: '2px',
    color: '#ff8b92',
  },
};
