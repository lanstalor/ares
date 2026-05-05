import { useEffect, useRef, useState } from "react";

import { ClarifySidebar } from "./components/ClarifySidebar";
import { IntroOverlay } from "./components/IntroOverlay";
import { ParticipantStrip } from "./components/ParticipantStrip";
import { PlayerInput } from "./components/PlayerInput";
import { SceneBackdrop } from "./components/SceneBackdrop";
import { StatusPanel } from "./components/StatusPanel";
import { TurnFeed } from "./components/TurnFeed";
import {
  fetchMemories,
  getCampaignState,
  getHealth,
  getSystemStatus,
  listCampaigns,
  listTurns,
  submitClarification,
  submitTurn,
} from "./lib/api";
import { createDevUiSnapshot, DEV_UI_QUERY, DEV_UI_ROUTE, isDevUiMode } from "./lib/devUiFixture";
import { UNIVERSAL_STORY_SCENES } from "./lib/introContent";
import { deriveShellReadiness } from "./lib/readiness";
import { buildActionPresets, buildSceneParticipants, deriveSceneTone } from "./lib/uiTheme";

const STORY_SCENE_DURATION_MS = 5400;
const STORY_BLACKOUT_OFFSET_MS = 4500;

function buildCampaignTurns(selectedCampaign, campaignState, turnHistoryByCampaign) {
  if (!selectedCampaign) {
    return [];
  }

  return turnHistoryByCampaign[selectedCampaign.id] ?? [];
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

function mergeParticipants(existing, incoming) {
  const roster = existing.map((p) => ({ ...p }));
  for (const np of incoming) {
    const firstName = np.name.split(/\s+/)[0].toLowerCase();
    const match = roster.find(
      (p) => p.name === np.name || p.name.toLowerCase().startsWith(firstName)
    );
    if (match) {
      match.disposition = np.disposition;
      match.role = np.role;
      if (np.level != null) match.level = np.level;
      if (np.current_hp != null) match.current_hp = np.current_hp;
      if (np.max_hp != null) match.max_hp = np.max_hp;
    } else {
      roster.push(np);
    }
  }
  // keep only participants seen in this turn's incoming list (by canonical name match)
  return roster.filter((p) =>
    incoming.some((np) => np.name === p.name || p.name.toLowerCase().startsWith(np.name.split(/\s+/)[0].toLowerCase()))
  );
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

  for (const secret of resolution.revealed_secrets ?? []) {
    events.push({
      id: `${id}-secret-${secret.label}`,
      speaker: "system-secret",
      label: "Revealed",
      meta: secret.label,
      text: secret.content,
      timestamp: null,
    });
  }

  for (const roll of resolution.rolls ?? []) {
    events.push({
      id: `${id}-roll-${roll.attribute}-${events.length}`,
      speaker: "system-roll",
      label: "Roll",
      meta: `${roll.attribute} vs ${roll.target}`,
      text: `${roll.dice_total} -> ${roll.outcome.replace("_", " ")} - ${roll.narration}`,
      timestamp: null,
      roll,
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

async function fetchCampaignMemories(campaignId) {
  try {
    return await fetchMemories(campaignId, 10);
  } catch {
    return [];
  }
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
  const [loadingShell, setLoadingShell] = useState(true);
  const [loadingState, setLoadingState] = useState(false);
  const [isSubmittingTurn, setIsSubmittingTurn] = useState(false);
  const [suggestedActions, setSuggestedActions] = useState(() => {
    try { return JSON.parse(sessionStorage.getItem("ares_suggested_actions") ?? "[]"); } catch { return []; }
  });
  const [gmSceneParticipants, setGmSceneParticipants] = useState(() => {
    try {
      const parsed = JSON.parse(sessionStorage.getItem("ares_scene_participants") ?? "[]");
      return Array.isArray(parsed) ? parsed : [];
    } catch { return []; }
  });
  const [memories, setMemories] = useState([]);
  const [isClarifySidebarOpen, setIsClarifySidebarOpen] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [presentationStage, setPresentationStage] = useState(() => {
    if (typeof localStorage !== "undefined" && localStorage.getItem("ares_intro_seen")) {
      return "game";
    }
    return "boot";
  });
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
    const topbar = document.querySelector(".topbar");
    if (!topbar) return;
    const sync = () => document.documentElement.style.setProperty("--topbar-height", `${topbar.offsetHeight}px`);
    sync();
    const ro = new ResizeObserver(sync);
    ro.observe(topbar);
    return () => ro.disconnect();
  }, []);

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
        localStorage.setItem("ares_intro_seen", "1");
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
    setSuggestedActions(snapshot.suggestedActionsByCampaign?.[snapshot.selectedCampaignId] ?? []);
    setGmSceneParticipants(snapshot.sceneParticipantsByCampaign?.[snapshot.selectedCampaignId] ?? []);
    setTurnHistoryByCampaign(snapshot.turnHistoryByCampaign);
    setLoadingShell(false);
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
      setSuggestedActions(devUiSnapshotRef.current?.suggestedActionsByCampaign?.[selectedCampaignId] ?? []);
      setGmSceneParticipants(devUiSnapshotRef.current?.sceneParticipantsByCampaign?.[selectedCampaignId] ?? []);
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
        const campaignMemories = await fetchCampaignMemories(selectedCampaignId);
        if (isMounted) {
          setMemories(campaignMemories);
        }
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
  const shellStatusText = buildShellStatusText(loadingShell, healthStatus);
  const shellReadiness = deriveShellReadiness({ healthStatus, systemStatus, campaigns, lastSeedResult: null });
  const inferredSceneTone = deriveSceneTone({ campaignState, selectedCampaign, turns });
  const sceneTone = manualSceneTone === "auto" ? inferredSceneTone : manualSceneTone;
  const participants = buildSceneParticipants({ campaignState, gmSceneParticipants, selectedCampaign, sceneTone });
  const staticPresets = buildActionPresets(sceneTone);
  const activeActions = suggestedActions.length
    ? suggestedActions.map((a, i) => ({ id: `gm-${i}`, key: String(i + 1), icon: "→", ...a }))
    : staticPresets;

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
      if (resolution.suggested_actions?.length) {
        setSuggestedActions(resolution.suggested_actions);
        sessionStorage.setItem("ares_suggested_actions", JSON.stringify(resolution.suggested_actions));
      }
      if (resolution.scene_participants?.length) {
        setGmSceneParticipants((current) => mergeParticipants(current, resolution.scene_participants));
        sessionStorage.setItem("ares_scene_participants", JSON.stringify(
          mergeParticipants(
            JSON.parse(sessionStorage.getItem("ares_scene_participants") ?? "[]"),
            resolution.scene_participants
          )
        ));
      }
      const updatedMemories = await fetchCampaignMemories(selectedCampaign.id);
      setMemories(updatedMemories);
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
    localStorage.setItem("ares_intro_seen", "1");
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

  function handleToggleClarify() {
    setIsClarifySidebarOpen((current) => !current);
  }

  const shellMode = "live";

  return (
    <div className={`app-shell frame-shell scene-theme-${sceneTone} mode-${shellMode} ${devUiMode ? "dev-ui-mode" : ""}`}>
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
          <button
            className={`secondary-button topbar-clarify-button ${isClarifySidebarOpen ? "active" : ""}`}
            onClick={handleToggleClarify}
            title="Get GM clarification"
            type="button"
          >
            ?
          </button>
          {devUiMode ? null : (
            <button className="secondary-button topbar-session-button" onClick={handleToggleAudio} type="button">
              {audioMuted ? "Muted" : "Audio"}
            </button>
          )}
        </div>
      </header>


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
              isThinking={isSubmittingTurn}
              objective={campaignState?.active_objective}
              participants={participants}
              speakerCaste={campaignState?.player_character?.race}
              speakerName={campaignState?.player_character?.name}
              speakerRole={campaignState?.player_character?.character_class}
              statusText={
                loadingState ? "Synchronizing feed" : selectedCampaign ? "LLM GM live" : "Awaiting campaign"
              }
              turns={turns}
            />
            <div className="scene-column">
              <SceneBackdrop
                campaignState={campaignState}
                currentLocation={campaignState?.current_location ?? selectedCampaign?.current_location_label}
                objective={campaignState?.active_objective}
                sceneTone={sceneTone}
                selectedCampaign={selectedCampaign}
              />
              <ParticipantStrip participants={participants} sceneTone={sceneTone} />
            </div>
          </section>
          <PlayerInput
            actions={activeActions}
            disabled={!selectedCampaign}
            isSubmitting={isSubmittingTurn}
            onSelectAction={handleSelectAction}
            onSubmit={handleSubmitTurn}
            onValueChange={setInputValue}
            placeholder={
              selectedCampaign
                ? "ares> execute cell directive..."
                : "ares> campaign link required"
            }
            sceneTone={sceneTone}
            value={inputValue}
          />
        </section>

        <StatusPanel
          campaignState={campaignState}
          healthStatus={healthStatus}
          memories={memories}
          selectedCampaign={selectedCampaign}
          shellReadiness={shellReadiness}
          systemStatus={systemStatus}
        />
      </main>

      <ClarifySidebar
        campaignId={selectedCampaignId}
        isOpen={isClarifySidebarOpen}
        onClarify={submitClarification}
        onClose={() => setIsClarifySidebarOpen(false)}
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
