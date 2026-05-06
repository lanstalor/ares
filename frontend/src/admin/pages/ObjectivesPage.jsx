import { useState } from 'react';
import { useOperatorState } from '../AdminApp';
import EntityTable from '../components/EntityTable';
import EntityModal from '../components/EntityModal';

export default function ObjectivesPage() {
  const { fullState, api, campaignId } = useOperatorState();
  const [selectedEntity, setSelectedEntity] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const objectives = fullState?.objectives || [];

  const tableData = objectives.map((obj) => ({
    ...obj,
    is_active: obj.is_active ? 'Yes' : 'No',
    is_complete: obj.is_complete ? 'Yes' : 'No',
  }));

  const columns = [
    { key: 'title', label: 'Title', width: '40%' },
    { key: 'is_active', label: 'Active', type: 'boolean', width: '15%' },
    { key: 'is_complete', label: 'Complete', type: 'boolean', width: '15%' },
  ];

  const fields = [
    { key: 'title', label: 'Title', type: 'text' },
    { key: 'description', label: 'Description', type: 'textarea', rows: 3 },
    { key: 'gm_instructions', label: 'GM Instructions', type: 'textarea', rows: 4 },
    { key: 'is_active', label: 'Active', type: 'checkbox' },
    { key: 'is_complete', label: 'Complete', type: 'checkbox' },
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
        entity_type: 'objective',
        entity_id: selectedEntity.id,
        changes,
      });

      // Refresh full state
      const updatedState = await api.getFullState(campaignId);
      const updatedObjective = updatedState.objectives.find(
        (obj) => obj.id === selectedEntity.id
      );
      setSelectedEntity(updatedObjective);

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
      <h1 style={styles.title}>Objectives</h1>
      {error && <div style={styles.pageError}>{error}</div>}
      <EntityTable
        entities={tableData}
        columns={columns}
        onEditRow={handleEditRow}
      />
      <EntityModal
        isOpen={isModalOpen}
        title={selectedEntity ? `Edit: ${selectedEntity.title}` : 'New Objective'}
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
