import { useState } from 'react';
import { useOperatorState } from '../AdminApp';
import EntityTable from '../components/EntityTable';
import EntityModal from '../components/EntityModal';

export default function NPCsPage() {
  const { fullState, api, campaignId } = useOperatorState();
  const [selectedEntity, setSelectedEntity] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const characters = fullState?.characters || [];
  const playerCharacterId = fullState?.campaign?.player_character_id;

  // Filter out player character
  const npcs = characters.filter((char) => char.id !== playerCharacterId);

  const tableData = npcs.map((npc) => ({
    ...npc,
    hp: `${npc.current_hp}/${npc.max_hp}`,
  }));

  const columns = [
    { key: 'name', label: 'Name', width: '25%' },
    { key: 'disposition', label: 'Disposition', width: '20%' },
    { key: 'level', label: 'Level', width: '15%' },
    { key: 'hp', label: 'HP', width: '20%' },
  ];

  const fields = [
    { key: 'name', label: 'Name', type: 'text' },
    {
      key: 'disposition',
      label: 'Disposition',
      type: 'select',
      options: [
        { value: 'allied', label: 'Allied' },
        { value: 'neutral', label: 'Neutral' },
        { value: 'hostile', label: 'Hostile' },
        { value: 'unknown', label: 'Unknown' },
      ],
    },
    { key: 'level', label: 'Level', type: 'number' },
    { key: 'current_hp', label: 'Current HP', type: 'number' },
    { key: 'max_hp', label: 'Max HP', type: 'number' },
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
        entity_type: 'character',
        entity_id: selectedEntity.id,
        changes,
      });

      // Refresh full state
      const updatedState = await api.getFullState(campaignId);
      const updatedNpc = updatedState.characters.find(
        (char) => char.id === selectedEntity.id
      );
      setSelectedEntity(updatedNpc);

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
      <h1 style={styles.title}>NPCs</h1>
      {error && <div style={styles.pageError}>{error}</div>}
      <EntityTable
        entities={tableData}
        columns={columns}
        onEditRow={handleEditRow}
      />
      <EntityModal
        isOpen={isModalOpen}
        title={selectedEntity ? `Edit: ${selectedEntity.name}` : 'New NPC'}
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
