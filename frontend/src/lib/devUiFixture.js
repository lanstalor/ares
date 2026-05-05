function isoAt(offsetMinutes) {
  return new Date(Date.now() + offsetMinutes * 60 * 1000).toISOString();
}

export const DEV_UI_ROUTE = "/ui-dev";
export const DEV_UI_QUERY = "ui-dev";
export const ASSET_OVERLAY_QUERY = "asset-overlay";

function hasQueryFlag(flag) {
  if (typeof window === "undefined") {
    return false;
  }

  const params = new URLSearchParams(window.location.search);
  return params.get(flag) === "1";
}

export function isDevUiMode() {
  if (typeof window === "undefined") {
    return false;
  }

  return window.location.pathname === DEV_UI_ROUTE || hasQueryFlag(DEV_UI_QUERY);
}

export function isAssetOverlayMode() {
  return hasQueryFlag(ASSET_OVERLAY_QUERY);
}

export function setQueryFlag(flag, enabled) {
  if (typeof window === "undefined") {
    return;
  }

  const url = new URL(window.location.href);

  if (enabled) {
    url.searchParams.set(flag, "1");
  } else {
    url.searchParams.delete(flag);
  }

  window.history.replaceState({}, "", `${url.pathname}${url.search}${url.hash}`);
}

export function createDevUiSnapshot() {
  const primaryCampaignId = "dev-campaign-1";
  const campaigns = [
    {
      id: primaryCampaignId,
      name: "Ash in the Dockyards",
      tagline: "A quiet extraction collapses into a pressure-cooker meeting in the Crescent Block.",
      current_date_pce: 728,
      hidden_state_enabled: true,
      current_location_label: "Crescent Block / Callisto Depot District",
      created_at: isoAt(-240),
      updated_at: isoAt(-8),
    },
  ];

  const campaignStateById = {
    [primaryCampaignId]: {
      campaign: campaigns[0],
      current_location: "Crescent Block / Callisto Depot District",
      active_objective: "Get the stolen burner ledger out before the Gray sweep locks the tram lines.",
      recent_turns: [
        "A dock contact slipped Davan a stolen ledger tagged with Gray routing marks.",
        "A command relay warned that an inspection team is already moving toward the block.",
      ],
      player_character: {
        id: "dev-character-1",
        campaign_id: primaryCampaignId,
        name: "Davan of Tharsis",
        race: "HighRed",
        character_class: "Operative",
        cover_identity: "Dav of Vashti",
        current_hp: 38,
        max_hp: 38,
        cover_integrity: 7,
        inventory_summary: "Forged sigil, relay wafer, burner ledger, work harness.",
        notes: "Mock UI state for frontend iteration only.",
        created_at: isoAt(-240),
        updated_at: isoAt(-8),
      },
      hidden_state_summary: "Hidden state remains server-only.",
    },
  };

  const turnHistoryByCampaign = {
    [primaryCampaignId]: [
      {
        id: "dev-turn-1",
        speaker: "system",
        label: "System",
        meta: "Link primed",
        text: "Operative channel open. Crescent Block is unstable. Gray movement is light but converging.",
        timestamp: isoAt(-7),
      },
      {
        id: "dev-turn-2",
        speaker: "gm",
        label: "GM",
        meta: "Player-safe",
        text: "Steam hisses from cracked pipes above the tram channel. Blue work-lights smear across the wet steel as your contact edges out from behind a cargo brace and presses the ledger into your palm.",
        timestamp: isoAt(-6),
      },
      {
        id: "dev-turn-3",
        speaker: "player",
        label: "Player",
        meta: "Davan",
        text: "I tuck the ledger under my harness, keep my voice low, and ask who else knows it changed hands.",
        timestamp: isoAt(-5),
      },
      {
        id: "dev-turn-4",
        speaker: "gm",
        label: "GM",
        meta: "Player-safe",
        text: '[Red]"Only the wrong people," she says. [Gray]"Keep moving," a lurcher barks from the tram cut as the siren starts to rise somewhere deeper in the block.',
        timestamp: isoAt(-4),
      },
    ],
  };

  const suggestedActionsByCampaign = {
    [primaryCampaignId]: [
      {
        label: "Press The Contact",
        prompt: "I keep my voice low and press the contact to tell me who is already hunting the ledger.",
      },
      {
        label: "Slip To Transit",
        prompt: "I break from the stall line and angle toward the tram spine before the Gray sweep closes.",
      },
      {
        label: "Read The Room",
        prompt: "I stay still for a beat and read the market for who is acting scared, armed, or too calm.",
      },
    ],
  };

  const sceneParticipantsByCampaign = {
    [primaryCampaignId]: [
      {
        name: "Tavi of Ceres Row",
        caste: "Red",
        role: "Dock contact",
        disposition: "friendly",
      },
      {
        name: "Lurcher Vexa ti Rhone",
        caste: "Gray",
        role: "Security sweep lead",
        disposition: "suspicious",
      },
    ],
  };

  return {
    healthStatus: { status: "ok" },
    systemStatus: {
      app_name: "Project Ares",
      environment: "development",
      ai_generation_provider: "mock-gm",
      ai_model: "ui-dev-sim",
      embedding_provider: "mock",
      world_bible_exists: true,
      world_bible_path: "/home/lans/ares/world_bible.md",
      hidden_state_enabled: true,
      multi_agent_enabled: false,
      campaign_seeded: true,
      seeded_campaign_name: campaigns[0].name,
    },
    campaigns,
    selectedCampaignId: primaryCampaignId,
    campaignStateById,
    sceneParticipantsByCampaign,
    suggestedActionsByCampaign,
    turnHistoryByCampaign,
    lastSeedResult: {
      campaign_id: primaryCampaignId,
      campaign_name: campaigns[0].name,
      source_path: "/home/lans/ares/world_bible.md",
    },
  };
}
