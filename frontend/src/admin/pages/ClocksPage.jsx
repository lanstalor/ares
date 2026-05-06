import { useState } from 'react';
import { useOperatorState } from '../AdminApp';
import EntityTable from '../components/EntityTable';
import EntityModal from '../components/EntityModal';

export default function ClocksPage() {
  const { fullState, api, campaignId } = useOperatorState();
  const [selectedEntity, setSelectedEntity] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const clocks = fullState?.clocks || [];

  const tableData = clocks.map((clock) => ({
    ...clock,
    progress: `${clock.current_value}/${clock.max_value}`,
    hidden_from_player: clock.hidden_from_player ? 'Yes' : 'No',
  }));

  const columns = [
    { key: 'label', label: 'Label', width: '30%' },
    { key: 'clock_type', label: 'Type', width: '20%' },
    { key: 'progress', label: 'Progress', width: '20%' },
    { key: 'hidden_from_player', label: 'Hidden', type: 'boolean', width: '15%' },
  ];

  const fields = [
    { key: 'label', label: 'Label', type: 'text' },
    {
      key: 'clock_type',
      label: 'Type',
      type: 'select',
      options: [
        { value: 'tension', label: 'Tension' },
        { value: 'doom', label: 'Doom' },
        { value: 'progress', label: 'Progress' },
        { value: 'faction', label: 'Faction' },
      ],
    },
    { key: 'current_value', label: 'Current Value', type: 'number' },
    { key: 'max_value', label: 'Max Value', type: 'number' },
    { key: 'hidden_from_player', label: 'Hidden from Player', type: 'checkbox' },
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
        entity_type: 'clock',
        entity_id: selectedEntity.id,
        changes,
      });

      // Refresh full state
      const updatedState = await api.getFullState(campaignId);
      const updatedClock = updatedState.clocks.find(
        (clock) => clock.id === selectedEntity.id
      );
      setSelectedEntity(updatedClock);

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
      <h1 style={styles.title}>Clocks</h1>
      {error && <div style={styles.pageError}>{error}</div>}
      <EntityTable
        entities={tableData}
        columns={columns}
        onEditRow={handleEditRow}
      />
      <EntityModal
        isOpen={isModalOpen}
        title={selectedEntity ? `Edit: ${selectedEntity.label}` : 'New Clock'}
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
