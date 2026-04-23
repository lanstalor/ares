import { useEffect, useState } from "react";

import { CampaignConsole } from "./components/CampaignConsole";
import { PlayerInput } from "./components/PlayerInput";
import { StatusPanel } from "./components/StatusPanel";
import { TurnFeed } from "./components/TurnFeed";
import {
  API_BASE_URL,
  createCampaign,
  getCampaignState,
  getHealth,
  getSystemStatus,
  listTurns,
  listCampaigns,
  seedWorldBible,
  submitTurn,
} from "./lib/api";

const createEmptyCampaignForm = () => ({
  name: "",
  tagline: "",
});

function createOpeningNotice(selectedCampaign) {
  if (!selectedCampaign) {
    return [];
  }

  return [
    {
      id: `system-${selectedCampaign.id}`,
      speaker: "system",
      label: "System",
      meta: "Link primed",
      text: `Campaign uplink established for ${selectedCampaign.name}. Submit Davan's next move when ready.`,
    },
  ];
}

function normalizeRecentTurns(recentTurns = []) {
  return recentTurns.map((entry, index) => ({
    id: `recent-${index}`,
    speaker: "system",
    label: "Archive",
    meta: "State snapshot",
    text: entry,
  }));
}

function buildCampaignTurns(selectedCampaign, campaignState, turnHistoryByCampaign) {
  if (!selectedCampaign) {
    return [];
  }

  const recentTurns = normalizeRecentTurns(campaignState?.recent_turns);
  const liveTurns = turnHistoryByCampaign[selectedCampaign.id] ?? [];

  return [
    ...createOpeningNotice(selectedCampaign),
    ...(liveTurns.length ? liveTurns : recentTurns),
  ];
}

function normalizePersistedTurns(turns = []) {
  return turns.flatMap((turn) => [
    {
      id: `${turn.id}-player`,
      speaker: "player",
      label: "Player",
      meta: "Persisted",
      text: turn.player_input,
      timestamp: turn.created_at,
    },
    {
      id: `${turn.id}-gm`,
      speaker: "gm",
      label: "GM",
      meta: turn.player_safe_summary ?? "Player-safe",
      text: turn.gm_response,
      timestamp: turn.updated_at ?? turn.created_at,
    },
  ]);
}

export default function App() {
  const [healthStatus, setHealthStatus] = useState(null);
  const [systemStatus, setSystemStatus] = useState(null);
  const [campaigns, setCampaigns] = useState([]);
  const [selectedCampaignId, setSelectedCampaignId] = useState("");
  const [campaignState, setCampaignState] = useState(null);
  const [turnHistoryByCampaign, setTurnHistoryByCampaign] = useState({});
  const [createForm, setCreateForm] = useState(createEmptyCampaignForm);
  const [loadingShell, setLoadingShell] = useState(true);
  const [loadingCampaigns, setLoadingCampaigns] = useState(false);
  const [loadingState, setLoadingState] = useState(false);
  const [creatingCampaign, setCreatingCampaign] = useState(false);
  const [seedingWorldBible, setSeedingWorldBible] = useState(false);
  const [isSubmittingTurn, setIsSubmittingTurn] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  useEffect(() => {
    let isMounted = true;

    async function loadShell() {
      setLoadingShell(true);
      setErrorMessage("");

      try {
        const [health, system, campaignList] = await Promise.all([
          getHealth(),
          getSystemStatus(),
          listCampaigns(),
        ]);

        if (!isMounted) return;

        setHealthStatus(health);
        setSystemStatus(system);
        setCampaigns(campaignList);
        setSelectedCampaignId((current) => current || campaignList[0]?.id || "");
      } catch (error) {
        if (!isMounted) return;

        setHealthStatus({ status: "offline" });
        setSystemStatus(null);
        setCampaigns([]);
        setErrorMessage(error.message);
      } finally {
        if (isMounted) {
          setLoadingShell(false);
        }
      }
    }

    loadShell();

    return () => {
      isMounted = false;
    };
  }, []);

  useEffect(() => {
    let isMounted = true;

    async function loadCampaignState() {
      if (!selectedCampaignId) {
        setCampaignState(null);
        setTurnHistoryByCampaign((current) => ({ ...current, [selectedCampaignId]: [] }));
        setLoadingState(false);
        return;
      }

      setLoadingState(true);

      try {
        const [state, turnHistory] = await Promise.all([
          getCampaignState(selectedCampaignId),
          listTurns(selectedCampaignId),
        ]);
        if (isMounted) {
          setCampaignState(state);
          setTurnHistoryByCampaign((current) => ({
            ...current,
            [selectedCampaignId]: normalizePersistedTurns(turnHistory),
          }));
          setErrorMessage("");
        }
      } catch (error) {
        if (isMounted) {
          setCampaignState(null);
          setErrorMessage(error.message);
        }
      } finally {
        if (isMounted) {
          setLoadingState(false);
        }
      }
    }

    loadCampaignState();

    return () => {
      isMounted = false;
    };
  }, [selectedCampaignId]);

  const selectedCampaign = campaigns.find((campaign) => campaign.id === selectedCampaignId) ?? null;
  const turns = buildCampaignTurns(selectedCampaign, campaignState, turnHistoryByCampaign);

  async function refreshCampaigns(nextSelectedCampaignId = selectedCampaignId) {
    setLoadingCampaigns(true);

    try {
      const nextCampaigns = await listCampaigns();
      setCampaigns(nextCampaigns);
      setSelectedCampaignId(nextSelectedCampaignId || nextCampaigns[0]?.id || "");
    } catch (error) {
      setErrorMessage(error.message);
    } finally {
      setLoadingCampaigns(false);
    }
  }

  function handleCreateFormChange(event) {
    const { name, value } = event.target;
    setCreateForm((current) => ({
      ...current,
      [name]: value,
    }));
  }

  async function handleCreateCampaign(event) {
    event.preventDefault();
    if (!createForm.name.trim()) return;

    setCreatingCampaign(true);
    setErrorMessage("");

    try {
      const createdCampaign = await createCampaign({
        name: createForm.name.trim(),
        tagline: createForm.tagline.trim() || null,
        current_date_pce: 728,
      });

      setCreateForm(createEmptyCampaignForm());
      await refreshCampaigns(createdCampaign.id);
    } catch (error) {
      setErrorMessage(error.message);
    } finally {
      setCreatingCampaign(false);
    }
  }

  async function handleSubmitTurn(playerInput) {
    if (!selectedCampaign) return;

    setIsSubmittingTurn(true);
    setErrorMessage("");

    const optimisticPlayerTurn = {
      id: `player-${selectedCampaign.id}-${Date.now()}`,
      speaker: "player",
      label: "Player",
      meta: selectedCampaign.name,
      text: playerInput,
      timestamp: new Date().toISOString(),
    };

    setTurnHistoryByCampaign((current) => ({
      ...current,
      [selectedCampaign.id]: [...(current[selectedCampaign.id] ?? []), optimisticPlayerTurn],
    }));

    try {
      const resolution = await submitTurn(selectedCampaign.id, { player_input: playerInput });
      const turnHistory = await listTurns(selectedCampaign.id);
      setTurnHistoryByCampaign((current) => ({
        ...current,
        [selectedCampaign.id]: normalizePersistedTurns(turnHistory).map((turn) =>
          turn.id === `${resolution.turn.id}-gm`
            ? {
                ...turn,
                label: resolution.canon_guard_passed ? "GM" : "Canon Guard",
                location: resolution.context_excerpt,
                meta: resolution.canon_guard_passed ? turn.meta : resolution.canon_guard_message,
              }
            : turn,
        ),
      }));
    } catch (error) {
      setTurnHistoryByCampaign((current) => ({
        ...current,
        [selectedCampaign.id]: (current[selectedCampaign.id] ?? []).filter(
          (turn) => turn.id !== optimisticPlayerTurn.id,
        ),
      }));
      setErrorMessage(error.message);
    } finally {
      setIsSubmittingTurn(false);
    }
  }

  async function handleSeedWorldBible() {
    setSeedingWorldBible(true);
    setErrorMessage("");

    try {
      const seeded = await seedWorldBible({});
      await refreshCampaigns(seeded.campaign_id);
    } catch (error) {
      setErrorMessage(error.message);
    } finally {
      setSeedingWorldBible(false);
    }
  }

  return (
    <div className="app-shell">
      <header className="masthead">
        <div>
          <p className="eyebrow">Project Ares</p>
          <h1>The Solar Society, 728 PCE</h1>
          <p className="masthead-copy">
            CLI-built hidden-state RPG shell. Frontend uplink targeting <span>{API_BASE_URL}</span>.
          </p>
        </div>
        <div className="masthead-badges">
          <div className="system-badge">{loadingShell ? "Booting shell" : "UI shell online"}</div>
          <div className="system-badge">Phase 0/1 live play</div>
        </div>
      </header>

      {errorMessage ? (
        <section className="alert-banner" role="alert">
          {errorMessage}
        </section>
      ) : null}

      <main className="layout">
        <section className="play-column">
          <TurnFeed
            campaignName={selectedCampaign?.name}
            statusText={loadingState ? "Syncing state" : selectedCampaign ? "Live channel" : "Idle"}
            turns={turns}
          />
          <PlayerInput
            disabled={!selectedCampaign}
            isSubmitting={isSubmittingTurn}
            onSubmit={handleSubmitTurn}
            placeholder={
              selectedCampaign
                ? "Describe what Davan does next..."
                : "Create or select a campaign to unlock transmission."
            }
          />
        </section>

        <section className="side-column">
          <CampaignConsole
            campaigns={campaigns}
            createForm={createForm}
            creatingCampaign={creatingCampaign}
            loadingCampaigns={loadingCampaigns}
            onSeedWorldBible={handleSeedWorldBible}
            onCreateCampaign={handleCreateCampaign}
            onFormChange={handleCreateFormChange}
            onSelectCampaign={setSelectedCampaignId}
            seedingWorldBible={seedingWorldBible}
            selectedCampaignId={selectedCampaignId}
            worldBibleReady={Boolean(systemStatus?.world_bible_exists)}
          />
          <StatusPanel
            campaignState={campaignState}
            healthStatus={healthStatus}
            selectedCampaign={selectedCampaign}
            systemStatus={systemStatus}
          />
        </section>
      </main>
    </div>
  );
}
