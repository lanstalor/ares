import { BOOT_SEQUENCE_LINES, UNIVERSAL_STORY_SCENES } from "../lib/introContent";

function BootScreen({ bootProgress, shellStatusText }) {
  const visibleCount = Math.max(
    1,
    Math.min(BOOT_SEQUENCE_LINES.length, Math.ceil((bootProgress / 100) * BOOT_SEQUENCE_LINES.length)),
  );

  return (
    <div className="intro-overlay intro-overlay-boot">
      <div className="intro-noise" />
      <div className="intro-frame intro-frame-boot">
        <p className="eyebrow">Project Ares Boot</p>
        <h1>Runtime Handshake</h1>
        <p className="intro-copy">
          Establishing the Ganymede command shell and sealing the hidden-state partitions before live play.
        </p>

        <div className="boot-log" aria-live="polite">
          {BOOT_SEQUENCE_LINES.slice(0, visibleCount).map((line) => (
            <div className="boot-line" key={line}>
              <span className="boot-line-mark">&gt;</span>
              <span>{line}</span>
            </div>
          ))}
        </div>

        <div className="boot-progress">
          <div className="boot-progress-track">
            <div className="boot-progress-fill" style={{ width: `${bootProgress}%` }} />
          </div>
          <div className="boot-progress-meta">
            <span>{bootProgress}%</span>
            <span>{shellStatusText}</span>
          </div>
        </div>
      </div>
    </div>
  );
}

function TitleScreen({ audioMuted, audioReady, onPressStart, onToggleAudio, shellStatusText }) {
  return (
    <div className="intro-overlay intro-overlay-title">
      <div className="intro-noise" />
      <div className="title-backdrop" />

      <div className="intro-frame title-frame">
        <p className="eyebrow">Project Ares</p>
        <div className="title-logo-block">
          <p className="title-super">Sons of Ares era</p>
          <h1 className="title-logo">Red Rising</h1>
          <p className="title-subtitle">Ganymede cell command interface</p>
        </div>

        <p className="intro-copy title-copy">
          A single-screen tactical narrative shell for a pre-authored campaign handoff into a live LLM GM.
        </p>

        <div className="title-meta">
          <span className="system-badge">{shellStatusText}</span>
          <span className="system-badge">{audioReady ? "Synth ambience primed" : "Audio arms on start"}</span>
        </div>

        <div className="title-actions">
          <button className="start-button" onClick={onPressStart} type="button">
            Press Start
          </button>
          <button className="secondary-button" onClick={onToggleAudio} type="button">
            {audioMuted ? "Audio: muted" : "Audio: live"}
          </button>
        </div>

        <p className="title-hint">Press Enter to start. Audio uses a procedural placeholder score.</p>
      </div>
    </div>
  );
}

function StoryScreen({
  activeSceneIndex,
  audioMuted,
  onAdvanceStory,
  onSkipIntro,
  onToggleAudio,
  scenePhase,
}) {
  return (
    <div className="intro-overlay intro-overlay-story">
      <div className={`story-blackout ${scenePhase === "flash" ? "is-active" : ""}`} />
      <div className="intro-noise" />

      <div className="story-topbar">
        <span className="system-badge">Universal campaign prelude</span>
        <div className="story-actions">
          <button className="secondary-button" onClick={onToggleAudio} type="button">
            {audioMuted ? "Audio muted" : "Audio live"}
          </button>
          <button className="secondary-button" onClick={onSkipIntro} type="button">
            Skip intro
          </button>
        </div>
      </div>

      <div className="story-stage">
        {UNIVERSAL_STORY_SCENES.map((scene, index) => (
          <article
            className={`story-scene scene-${scene.key} ${index === activeSceneIndex ? "is-active" : ""}`}
            key={scene.key}
          >
            <div className="story-visual">
              <div className={`story-canvas scene-${scene.key}`} />
            </div>
            <div className="story-copy-panel">
              <p className="eyebrow">{scene.kicker}</p>
              <h2>{scene.title}</h2>
              <p>{scene.body}</p>
              <span className="story-caption">{scene.caption}</span>
            </div>
          </article>
        ))}
      </div>

      <div className="story-footer">
        <div className="story-progress">
          {UNIVERSAL_STORY_SCENES.map((scene, index) => (
            <span className={index === activeSceneIndex ? "is-active" : ""} key={scene.key} />
          ))}
        </div>
        <button className="start-button story-advance" onClick={onAdvanceStory} type="button">
          {activeSceneIndex === UNIVERSAL_STORY_SCENES.length - 1 ? "Enter Campaign" : "Continue"}
        </button>
      </div>
    </div>
  );
}

export function IntroOverlay(props) {
  const { activeSceneIndex, audioMuted, audioReady, bootProgress, onAdvanceStory, onPressStart, onSkipIntro, onToggleAudio, scenePhase, shellStatusText, stage } =
    props;

  if (stage === "game") {
    return null;
  }

  if (stage === "boot") {
    return <BootScreen bootProgress={bootProgress} shellStatusText={shellStatusText} />;
  }

  if (stage === "title") {
    return (
      <TitleScreen
        audioMuted={audioMuted}
        audioReady={audioReady}
        onPressStart={onPressStart}
        onToggleAudio={onToggleAudio}
        shellStatusText={shellStatusText}
      />
    );
  }

  return (
    <StoryScreen
      activeSceneIndex={activeSceneIndex}
      audioMuted={audioMuted}
      onAdvanceStory={onAdvanceStory}
      onSkipIntro={onSkipIntro}
      onToggleAudio={onToggleAudio}
      scenePhase={scenePhase}
    />
  );
}
