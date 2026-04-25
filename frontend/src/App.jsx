import { useEffect, useRef, useState } from "react";

import { ActionBar } from "./components/ActionBar";
import { CampaignConsole } from "./components/CampaignConsole";
import { IntroOverlay } from "./components/IntroOverlay";
import { ParticipantStrip } from "./components/ParticipantStrip";
import { PlayerInput } from "./components/PlayerInput";
import { SceneBackdrop } from "./components/SceneBackdrop";
import { StatusPanel } from "./components/StatusPanel";
import { TurnFeed } from "./components/TurnFeed";
import {
  createCampaign,
  getCampaignState,
  getHealth,
  getSystemStatus,
  listCampaigns,
  listTurns,
  seedWorldBible,
  submitTurn,
} from "./lib/api";
import { createDevUiSnapshot, DEV_UI_QUERY, DEV_UI_ROUTE, isDevUiMode } from "./lib/devUiFixture";
import { UNIVERSAL_STORY_SCENES } from "./lib/introContent";
import { deriveShellReadiness } from "./lib/readiness";
import { buildActionPresets, buildSceneParticipants, deriveSceneTone } from "./lib/uiTheme";

const DEFAULT_CAMPAIGN_DATE_PCE = 728;
const STORY_SCENE_DURATION_MS = 5400;
const STORY_BLACKOUT_OFFSET_MS = 4500;

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
      text: `Operative channel open — ${selectedCampaign.name}. You are Davan, a HighRed running cells for the Sons of Ares in the Callisto Depot District. The Society is everywhere. Move carefully.`,
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

function getAudioContextConstructor() {
  if (typeof window === "undefined") {
    return null;
  }

  return window.AudioContext || window.webkitAudioContext || null;
}

function setAmbientMasterLevel(audioRuntime, muted) {
  if (!audioRuntime) {
    return;
  }

  const now = audioRuntime.context.currentTime;
  audioRuntime.master.gain.cancelScheduledValues(now);
  audioRuntime.master.gain.setTargetAtTime(muted ? 0 : 0.05, now, 0.6);
}

async function ensureAmbientAudio(audioRuntimeRef, muted) {
  const AudioContextCtor = getAudioContextConstructor();

  if (!AudioContextCtor) {
    return false;
  }

  if (!audioRuntimeRef.current) {
    const context = new AudioContextCtor();
    const master = context.createGain();
    const filter = context.createBiquadFilter();
    const droneOne = context.createOscillator();
    const droneTwo = context.createOscillator();
    const shimmer = context.createOscillator();
    const droneOneGain = context.createGain();
    const droneTwoGain = context.createGain();
    const shimmerGain = context.createGain();
    const filterSweep = context.createOscillator();
    const filterSweepDepth = context.createGain();

    master.gain.value = 0;
    master.connect(context.destination);

    filter.type = "lowpass";
    filter.frequency.value = 780;
    filter.Q.value = 0.35;
    filter.connect(master);

    droneOne.type = "triangle";
    droneOne.frequency.value = 43.65;
    droneOneGain.gain.value = 0.09;
    droneOne.connect(droneOneGain);
    droneOneGain.connect(filter);

    droneTwo.type = "sawtooth";
    droneTwo.frequency.value = 65.41;
    droneTwo.detune.value = -6;
    droneTwoGain.gain.value = 0.03;
    droneTwo.connect(droneTwoGain);
    droneTwoGain.connect(filter);

    shimmer.type = "sine";
    shimmer.frequency.value = 130.81;
    shimmerGain.gain.value = 0.015;
    shimmer.connect(shimmerGain);
    shimmerGain.connect(filter);

    filterSweep.type = "sine";
    filterSweep.frequency.value = 0.045;
    filterSweepDepth.gain.value = 140;
    filterSweep.connect(filterSweepDepth);
    filterSweepDepth.connect(filter.frequency);

    droneOne.start();
    droneTwo.start();
    shimmer.start();
    filterSweep.start();

    audioRuntimeRef.current = {
      context,
      master,
      nodes: [droneOne, droneTwo, shimmer, filterSweep],
    };
  }

  if (audioRuntimeRef.current.context.state === "suspended") {
    await audioRuntimeRef.current.context.resume();
  }

  setAmbientMasterLevel(audioRuntimeRef.current, muted);
  return true;
}

function disposeAmbientAudio(audioRuntimeRef) {
  const audioRuntime = audioRuntimeRef.current;

  if (!audioRuntime) {
    return;
  }

  for (const node of audioRuntime.nodes) {
    try {
      node.stop();
    } catch {
      // Nodes can already be stopped during StrictMode remounts.
    }
  }

  audioRuntime.context.close().catch(() => {});
  audioRuntimeRef.current = null;
}

function buildShellStatusText(loadingShell, healthStatus) {
  if (loadingShell) {
    return "Linking command shell";
  }

  if (healthStatus?.status === "ok") {
    return "Uplink connected";
  }

  return "Uplink degraded";
}

export default function App() {
  const devUiMode = isDevUiMode();
  const [healthStatus, setHealthStatus] = useState(null);
  const [systemStatus, setSystemStatus] = useState(null);
  const [campaigns, setCampaigns] = useState([]);
  const [selectedCampaignId, setSelectedCampaignId] = useState(() => {
    if (!devUiMode) {
      return "";
    }

    return createDevUiSnapshot().selectedCampaignId;
  });
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
  const [presentationStage, setPresentationStage] = useState("boot");
  const [bootProgress, setBootProgress] = useState(0);
  const [storySceneIndex, setStorySceneIndex] = useState(0);
  const [scenePhase, setScenePhase] = useState("steady");
  const [audioMuted, setAudioMuted] = useState(false);
  const [audioReady, setAudioReady] = useState(false);
  const [inputValue, setInputValue] = useState("");
  const [manualSceneTone, setManualSceneTone] = useState("auto");
  const audioRuntimeRef = useRef(null);
  const devUiSnapshotRef = useRef(null);

  useEffect(() => () => disposeAmbientAudio(audioRuntimeRef), []);

  useEffect(() => {
    if (devUiMode) {
      return undefined;
    }

    if (presentationStage !== "boot") {
      return undefined;
    }

    let progress = 0;
    let advanceTimer = null;

    const intervalId = window.setInterval(() => {
      progress = Math.min(progress + (progress < 60 ? 6 : progress < 88 ? 3 : 2), 100);
      setBootProgress(progress);

      if (progress >= 100) {
        window.clearInterval(intervalId);
        advanceTimer = window.setTimeout(() => {
          setPresentationStage("title");
        }, 800);
      }
    }, 85);

    return () => {
      window.clearInterval(intervalId);
      if (advanceTimer) {
        window.clearTimeout(advanceTimer);
      }
    };
  }, [devUiMode, presentationStage]);

  useEffect(() => {
    if (devUiMode) {
      return undefined;
    }

    if (presentationStage !== "story") {
      return undefined;
    }

    setScenePhase("steady");

    const blackoutTimer = window.setTimeout(() => {
      setScenePhase("flash");
    }, STORY_BLACKOUT_OFFSET_MS);

    const advanceTimer = window.setTimeout(() => {
      setScenePhase("steady");

      if (storySceneIndex >= UNIVERSAL_STORY_SCENES.length - 1) {
        setPresentationStage("game");
        return;
      }

      setStorySceneIndex((current) => current + 1);
    }, STORY_SCENE_DURATION_MS);

    return () => {
      window.clearTimeout(blackoutTimer);
      window.clearTimeout(advanceTimer);
    };
  }, [devUiMode, presentationStage, storySceneIndex]);

  useEffect(() => {
    if (devUiMode) {
      return undefined;
    }

    function handleKeydown(event) {
      if (event.repeat) {
        return;
      }

      if (presentationStage === "title" && (event.key === "Enter" || event.key === " ")) {
        event.preventDefault();
        handlePressStart();
      }

      if (presentationStage === "story" && event.key === "Escape") {
        event.preventDefault();
        handleSkipIntro();
      }
    }

    window.addEventListener("keydown", handleKeydown);
    return () => window.removeEventListener("keydown", handleKeydown);
  }, [devUiMode, presentationStage, audioMuted]);

  useEffect(() => {
    if (!devUiMode) {
      return;
    }

    const snapshot = createDevUiSnapshot();
    devUiSnapshotRef.current = snapshot;
    setHealthStatus(snapshot.healthStatus);
    setSystemStatus(snapshot.systemStatus);
    setCampaigns(snapshot.campaigns);
    setSelectedCampaignId(snapshot.selectedCampaignId);
    setCampaignState(snapshot.campaignStateById[snapshot.selectedCampaignId]);
    setTurnHistoryByCampaign(snapshot.turnHistoryByCampaign);
    setLastSeedResult(snapshot.lastSeedResult);
    setLoadingShell(false);
    setLoadingCampaigns(false);
    setLoadingState(false);
    setPresentationStage("game");
    setBootProgress(100);
  }, [devUiMode]);

  useEffect(() => {
    if (devUiMode) {
      return undefined;
    }

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
  }, [devUiMode]);

  useEffect(() => {
    if (devUiMode) {
      const nextState = devUiSnapshotRef.current?.campaignStateById?.[selectedCampaignId] ?? null;
      setCampaignState(nextState);
      setLoadingState(false);
      return undefined;
    }

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
  }, [devUiMode, selectedCampaignId]);

  const selectedCampaign = campaigns.find((campaign) => campaign.id === selectedCampaignId) ?? null;
  const turns = buildCampaignTurns(selectedCampaign, campaignState, turnHistoryByCampaign);
  const shellReadiness = deriveShellReadiness({
    healthStatus,
    systemStatus,
    campaigns,
    lastSeedResult,
  });
  const shellStatusText = buildShellStatusText(loadingShell, healthStatus);
  const inferredSceneTone = deriveSceneTone({ campaignState, selectedCampaign, turns });
  const sceneTone = manualSceneTone === "auto" ? inferredSceneTone : manualSceneTone;
  const participants = buildSceneParticipants({ campaignState, selectedCampaign, sceneTone });
  const actionPresets = buildActionPresets(sceneTone);

  async function refreshShell(preferredCampaignId = selectedCampaignId) {
    if (devUiMode) {
      const snapshot = createDevUiSnapshot();
      devUiSnapshotRef.current = snapshot;
      setHealthStatus(snapshot.healthStatus);
      setSystemStatus(snapshot.systemStatus);
      setCampaigns(snapshot.campaigns);
      setSelectedCampaignId(snapshot.selectedCampaignId);
      setCampaignState(snapshot.campaignStateById[snapshot.selectedCampaignId]);
      setTurnHistoryByCampaign(snapshot.turnHistoryByCampaign);
      setLastSeedResult(snapshot.lastSeedResult);
      return;
    }

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
    if (devUiMode) {
      const nextState = devUiSnapshotRef.current?.campaignStateById?.[campaignId] ?? null;
      setCampaignState(nextState);
      return;
    }

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

    if (devUiMode) {
      const now = new Date().toISOString();
      const newCampaign = {
        id: `dev-${Date.now()}`,
        name: createForm.name.trim(),
        tagline: createForm.tagline.trim() || "Mock UI-only campaign",
        current_date_pce: DEFAULT_CAMPAIGN_DATE_PCE,
        hidden_state_enabled: true,
        current_location_label: "Crescent Block / Callisto Depot District",
        created_at: now,
        updated_at: now,
      };
      const nextState = {
        campaign: newCampaign,
        current_location: newCampaign.current_location_label,
        active_objective: "Sketch the scene rhythm and pressure using local mock data.",
        recent_turns: ["Mock campaign created for UI iteration."],
        player_character: {
          id: `dev-character-${Date.now()}`,
          campaign_id: newCampaign.id,
          name: "Davan of Tharsis",
          race: "HighRed",
          character_class: "Operative",
          cover_identity: "Dav of Vashti",
          current_hp: 38,
          max_hp: 38,
          cover_integrity: 8,
          inventory_summary: "Forged sigil, ledger, relay wafer.",
          notes: "Local mock character",
          created_at: now,
          updated_at: now,
        },
        hidden_state_summary: "Hidden state remains server-only.",
      };
      const nextCampaigns = [newCampaign];
      devUiSnapshotRef.current = {
        ...(devUiSnapshotRef.current ?? createDevUiSnapshot()),
        campaigns: nextCampaigns,
        selectedCampaignId: newCampaign.id,
        campaignStateById: { [newCampaign.id]: nextState },
        turnHistoryByCampaign: {
          [newCampaign.id]: [
            {
              id: `system-${newCampaign.id}`,
              speaker: "system",
              label: "System",
              meta: "Mock scene",
              text: "UI dev campaign created locally.",
              timestamp: now,
            },
          ],
        },
      };
      setCampaigns(nextCampaigns);
      setSelectedCampaignId(newCampaign.id);
      setCampaignState(nextState);
      setTurnHistoryByCampaign(devUiSnapshotRef.current.turnHistoryByCampaign);
      setCreateForm(createEmptyCampaignForm());
      return;
    }

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

    if (devUiMode) {
      const now = new Date().toISOString();
      const playerTurn = {
        id: `dev-player-${Date.now()}`,
        speaker: "player",
        label: "Player",
        meta: selectedCampaign.name,
        text: playerInput,
        timestamp: now,
      };
      const gmTurn = {
        id: `dev-gm-${Date.now() + 1}`,
        speaker: "gm",
        label: "GM",
        meta: "UI dev response",
        text:
          sceneTone === "gold"
            ? "The room tightens around the formality of your move. Gold eyes do not soften, but they do recalculate."
            : "The district answers in small tells: a glance, a hiss of steam, a hand pausing over contraband it suddenly wants hidden.",
        timestamp: new Date(Date.now() + 500).toISOString(),
      };

      setTurnHistoryByCampaign((current) => ({
        ...current,
        [selectedCampaign.id]: [...(current[selectedCampaign.id] ?? []), playerTurn, gmTurn],
      }));
      setInputValue("");
      return;
    }

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
      setInputValue("");
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
    if (devUiMode) {
      setLastSeedResult({
        campaign_id: selectedCampaignId,
        campaign_name: selectedCampaign?.name ?? "Mock campaign",
        source_path: "/home/lans/ares/world_bible.md",
      });
      return;
    }

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

  async function handlePressStart() {
    if (devUiMode) {
      setPresentationStage("game");
      return;
    }

    const started = await ensureAmbientAudio(audioRuntimeRef, audioMuted);
    if (started) {
      setAudioReady(true);
    }

    setStorySceneIndex(0);
    setScenePhase("steady");
    setPresentationStage("story");
  }

  function handleAdvanceStory() {
    if (storySceneIndex >= UNIVERSAL_STORY_SCENES.length - 1) {
      setScenePhase("steady");
      setPresentationStage("game");
      return;
    }

    setScenePhase("steady");
    setStorySceneIndex((current) => current + 1);
  }

  function handleSkipIntro() {
    setScenePhase("steady");
    setPresentationStage("game");
  }

  function handleReplayIntro() {
    if (devUiMode) {
      const snapshot = createDevUiSnapshot();
      devUiSnapshotRef.current = snapshot;
      setHealthStatus(snapshot.healthStatus);
      setSystemStatus(snapshot.systemStatus);
      setCampaigns(snapshot.campaigns);
      setSelectedCampaignId(snapshot.selectedCampaignId);
      setCampaignState(snapshot.campaignStateById[snapshot.selectedCampaignId]);
      setTurnHistoryByCampaign(snapshot.turnHistoryByCampaign);
      setLastSeedResult(snapshot.lastSeedResult);
      setInputValue("");
      setManualSceneTone("auto");
      return;
    }

    setStorySceneIndex(0);
    setScenePhase("steady");
    setPresentationStage("title");
  }

  function handleToggleAudio() {
    setAudioMuted((current) => {
      const next = !current;
      setAmbientMasterLevel(audioRuntimeRef.current, next);
      return next;
    });
  }

  function handleSelectAction(prompt) {
    setInputValue(prompt);
  }

  function handleCycleSceneTone() {
    setManualSceneTone((current) => {
      if (current === "auto") return "friendly";
      if (current === "friendly") return "gold";
      return "auto";
    });
  }

  const shellMode = devUiMode ? "live" : selectedCampaign ? "live" : "staging";

  return (
    <div className={`app-shell scene-theme-${sceneTone} mode-${shellMode} ${devUiMode ? "dev-ui-mode" : ""}`}>
      {devUiMode ? null : (
        <IntroOverlay
          activeSceneIndex={storySceneIndex}
          audioMuted={audioMuted}
          audioReady={audioReady}
          bootProgress={bootProgress}
          onAdvanceStory={handleAdvanceStory}
          onPressStart={handlePressStart}
          onSkipIntro={handleSkipIntro}
          onToggleAudio={handleToggleAudio}
          scenePhase={scenePhase}
          shellStatusText={shellStatusText}
          stage={presentationStage}
        />
      )}

      <div className="shell-atmosphere" />

      <header className="topbar">
        <div className="topbar-brand">
          <p className="eyebrow">Live narrative shell</p>
          <h1>ARES</h1>
        </div>

        <div className="topbar-center">
          <span className="topbar-breadcrumb">Ganymede / {campaignState?.current_location ?? selectedCampaign?.current_location_label ?? "Command link"}</span>
          <p className="topbar-tagline">
            {selectedCampaign?.tagline ??
              "Text-first Red Rising campaign interface with a pre-authored frame and live LLM GM handoff."}
          </p>
        </div>

        <div className="topbar-stats">
          {devUiMode ? (
            <div className="topbar-stat">
              <span>Mode</span>
              <strong>UI Dev</strong>
            </div>
          ) : null}
          <div className="topbar-stat">
            <span>Time</span>
            <strong>{selectedCampaign ? `${selectedCampaign.current_date_pce} PCE` : "728 PCE"}</strong>
          </div>
          <div className="topbar-stat">
            <span>Signal</span>
            <strong>{healthStatus?.status === "ok" ? "Stable" : "Degraded"}</strong>
          </div>
          <div className="topbar-stat">
            <span>Runtime</span>
            <strong>{selectedCampaign ? "Live" : "Standby"}</strong>
          </div>
          <button className="secondary-button scene-tone-button" onClick={handleCycleSceneTone} type="button">
            Tone: {manualSceneTone}
          </button>
        </div>
      </header>

      {devUiMode ? null : (
        <section className="hud-ribbon">
          <article className="hud-card">
            <span className="panel-label">Campaign</span>
            <strong>{selectedCampaign?.name ?? "No active cell"}</strong>
          </article>
          <article className="hud-card">
            <span className="panel-label">Objective</span>
            <strong>{campaignState?.active_objective ?? "Load or seed the canonical campaign"}</strong>
          </article>
          <article className="hud-card">
            <span className="panel-label">AI core</span>
            <strong>{shellReadiness.provider.label}</strong>
          </article>
          <article className="hud-card">
            <span className="panel-label">Canon frame</span>
            <strong>{shellReadiness.campaignSeed.label}</strong>
          </article>
        </section>
      )}

      {errorMessage ? (
        <section className="alert-banner" role="alert">
          {errorMessage}
        </section>
      ) : null}

      <main className="layout">
        <section className="play-column">
          <section className="story-grid">
            <TurnFeed
              campaignName={selectedCampaign?.name}
              speakerCaste={campaignState?.player_character?.race}
              speakerName={campaignState?.player_character?.name}
              speakerRole={campaignState?.player_character?.character_class}
              statusText={
                loadingState ? "Synchronizing feed" : selectedCampaign ? "LLM GM live" : "Awaiting campaign"
              }
              turns={turns}
            />
            <SceneBackdrop
              currentLocation={campaignState?.current_location ?? selectedCampaign?.current_location_label}
              objective={campaignState?.active_objective}
              sceneTone={sceneTone}
              selectedCampaign={selectedCampaign}
            />
          </section>
          <ParticipantStrip participants={participants} sceneTone={sceneTone} />
          <PlayerInput
            disabled={!selectedCampaign}
            isSubmitting={isSubmittingTurn}
            onSubmit={handleSubmitTurn}
            onValueChange={setInputValue}
            placeholder={
              selectedCampaign
                ? "State what the cell does next. The hidden state remains server-side."
                : "Select or seed a campaign to open the live narrative feed."
            }
            value={inputValue}
          />
        </section>

        {devUiMode ? null : (
          <section className="side-column">
            <section className="status-panel topbar-panel-tools">
              <div className="panel-chrome">
                <div>
                  <p className="eyebrow">Shell controls</p>
                  <h2>Session</h2>
                </div>
                <span className={`panel-chip is-${shellReadiness.provider.tone}`}>{shellStatusText}</span>
              </div>
              <div className="control-cluster">
                <button className="secondary-button" onClick={handleReplayIntro} type="button">
                  Replay intro
                </button>
                <button className="secondary-button" onClick={handleToggleAudio} type="button">
                  {audioMuted ? "Audio muted" : "Audio live"}
                </button>
                <button className="secondary-button" onClick={() => refreshShell()} type="button">
                  Refresh shell
                </button>
              </div>
            </section>
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
        )}
      </main>

      <ActionBar
        actions={actionPresets}
        disabled={!selectedCampaign}
        onSelectAction={handleSelectAction}
        sceneTone={sceneTone}
      />

      {devUiMode ? (
        <section className="dev-ui-helper">
          <span>UI Dev Mode</span>
          <span>{DEV_UI_ROUTE}</span>
          <span>?{DEV_UI_QUERY}=1</span>
        </section>
      ) : null}
    </div>
  );
}
