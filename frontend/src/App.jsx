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
  listCampaigns,
  listTurns,
  seedWorldBible,
  submitTurn,
} from "./lib/api";
import { deriveShellReadiness } from "./lib/readiness";

const DEFAULT_CAMPAIGN_DATE_PCE = 728;

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

function selectCampaignId(campaigns, preferredCampaignId) {
  if (preferredCampaignId && campaigns.some((campaign) => campaign.id === preferredCampaignId)) {
    return preferredCampaignId;
  }

  return campaigns[0]?.id ?? "";
}

function buildConsequenceEvents(resolution) {
  const id = resolution.turn.id;
  const events = [];

  if (resolution.location_changed_to) {
    events.push({
      id: `${id}-loc`,
      speaker: "system-location",
      label: "Location",
      meta: "Area change",
      text: resolution.location_changed_to,
      timestamp: null,
    });
  }

  for (const label of resolution.clocks_fired ?? []) {
    events.push({
      id: `${id}-clock-${label}`,
      speaker: "system-clock",
      label: "Clock",
      meta: "Fired",
      text: `${label} — consequence triggered`,
      timestamp: null,
    });
  }

  return events;
}

function patchTurnHistoryWithResolution(turnHistory, resolution) {
  const normalized = normalizePersistedTurns(turnHistory).map((turn) =>
    turn.id === `${resolution.turn.id}-gm`
      ? {
          ...turn,
          label: resolution.canon_guard_passed ? "GM" : "Canon Guard",
          location: resolution.context_excerpt,
          meta: resolution.canon_guard_passed ? turn.meta : resolution.canon_guard_message,
        }
      : turn,
  );
  return [...normalized, ...buildConsequenceEvents(resolution)];
}

async function fetchShellSnapshot() {
  return Promise.all([getHealth(), getSystemStatus(), listCampaigns()]);
}

async function fetchCampaignSnapshot(campaignId) {
  return Promise.all([getCampaignState(campaignId), listTurns(campaignId)]);
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
  const [lastSeedResult, setLastSeedResult] = useState(null);
  const [errorMessage, setErrorMessage] = useState("");

  useEffect(() => {
    let isMounted = true;

    async function loadShell() {
      setLoadingShell(true);
      setErrorMessage("");

      try {
        const [health, system, campaignList] = await fetchShellSnapshot();

        if (!isMounted) return;

        setHealthStatus(health);
        setSystemStatus(system);
        setCampaigns(campaignList);
        setSelectedCampaignId((current) => selectCampaignId(campaignList, current));
      } catch (error) {
        if (!isMounted) return;

        setHealthStatus({ status: "offline" });
        setSystemStatus(null);
        setCampaigns([]);
        setCampaignState(null);
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
        setLoadingState(false);
        return;
      }

      setLoadingState(true);

      try {
        const [state, turnHistory] = await fetchCampaignSnapshot(selectedCampaignId);

        if (!isMounted) return;

        setCampaignState(state);
        setTurnHistoryByCampaign((current) => ({
          ...current,
          [selectedCampaignId]: normalizePersistedTurns(turnHistory),
        }));
        setErrorMessage("");
      } catch (error) {
        if (!isMounted) return;

        setCampaignState(null);
        setErrorMessage(error.message);
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
  const shellReadiness = deriveShellReadiness({
    healthStatus,
    systemStatus,
    campaigns,
    lastSeedResult,
  });

  async function refreshShell(preferredCampaignId = selectedCampaignId) {
    setLoadingCampaigns(true);
    setErrorMessage("");

    try {
      const [health, system, nextCampaigns] = await fetchShellSnapshot();
      setHealthStatus(health);
      setSystemStatus(system);
      setCampaigns(nextCampaigns);
      setSelectedCampaignId((current) => selectCampaignId(nextCampaigns, preferredCampaignId || current));
    } catch (error) {
      setErrorMessage(error.message);
    } finally {
      setLoadingCampaigns(false);
    }
  }

  async function refreshActiveCampaign(campaignId = selectedCampaignId) {
    if (!campaignId) {
      return;
    }

    setLoadingState(true);
    setErrorMessage("");

    try {
      const [state, turnHistory] = await fetchCampaignSnapshot(campaignId);
      setCampaignState(state);
      setTurnHistoryByCampaign((current) => ({
        ...current,
        [campaignId]: normalizePersistedTurns(turnHistory),
      }));
    } catch (error) {
      setErrorMessage(error.message);
    } finally {
      setLoadingState(false);
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
        current_date_pce: DEFAULT_CAMPAIGN_DATE_PCE,
      });

      setCreateForm(createEmptyCampaignForm());
      await refreshShell(createdCampaign.id);
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
      const [state, turnHistory] = await fetchCampaignSnapshot(selectedCampaign.id);

      setCampaignState(state);
      setTurnHistoryByCampaign((current) => ({
        ...current,
        [selectedCampaign.id]: patchTurnHistoryWithResolution(turnHistory, resolution),
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
      setLastSeedResult(seeded);
      await refreshShell(seeded.campaign_id);
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
            Retro operator shell targeting <span>{API_BASE_URL}</span> with live backend readiness checks.
          </p>
        </div>
        <div className="masthead-badges">
          <div className="system-badge">{loadingShell ? "Booting shell" : "UI shell online"}</div>
          <div className={`system-badge is-${shellReadiness.provider.tone}`}>
            Provider: {shellReadiness.provider.label}
          </div>
          <div className={`system-badge is-${shellReadiness.worldBible.tone}`}>
            world_bible.md: {shellReadiness.worldBible.label}
          </div>
          <div className={`system-badge is-${shellReadiness.campaignSeed.tone}`}>
            Campaign: {shellReadiness.campaignSeed.label}
          </div>
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
            lastSeedResult={lastSeedResult}
            loadingCampaigns={loadingCampaigns}
            loadingShell={loadingShell}
            loadingState={loadingState}
            onCreateCampaign={handleCreateCampaign}
            onFormChange={handleCreateFormChange}
            onRefreshActiveCampaign={refreshActiveCampaign}
            onRefreshShell={refreshShell}
            onSeedWorldBible={handleSeedWorldBible}
            onSelectCampaign={setSelectedCampaignId}
            seedingWorldBible={seedingWorldBible}
            selectedCampaignId={selectedCampaignId}
            shellReadiness={shellReadiness}
            worldBibleReady={Boolean(systemStatus?.world_bible_exists)}
          />
          <StatusPanel
            campaignState={campaignState}
            healthStatus={healthStatus}
            selectedCampaign={selectedCampaign}
            shellReadiness={shellReadiness}
            systemStatus={systemStatus}
          />
        </section>
      </main>
    </div>
  );
}
