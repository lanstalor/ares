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
      name: "Ghost Packet at Relay 19",
      tagline: "A surface relay job becomes a race against a BoQC audit checksum.",
      current_date_pce: 728,
      hidden_state_enabled: true,
      current_location_label: "Surface Relay Tower 19",
      created_at: isoAt(-240),
      updated_at: isoAt(-8),
    },
  ];

  const campaignStateById = {
    [primaryCampaignId]: {
      campaign: campaigns[0],
      current_location: "Surface Relay Tower 19",
      active_objective: "Recover the ghost packet before Pelsin scrubs the carrier.",
      recent_turns: [
        "The relay buffer still holds a ghost packet in Pellam's maintenance code.",
        "Two Gray supervisors are watching the surface cradle from the checkpoint blister.",
      ],
      player_character: {
        id: "dev-character-1",
        campaign_id: primaryCampaignId,
        name: "Mara of Cimmeria",
        race: "HighRed",
        character_class: "Howler",
        cover_identity: "Mara of Cimmeria",
        current_hp: 40,
        max_hp: 40,
        cover_integrity: 8,
        items: [
          { id: "1", name: "Pressure suit", quantity: 1, tags: "survival", is_equipped: true },
          { id: "2", name: "Relay tools", quantity: 1, tags: "engineering", is_equipped: true },
          { id: "3", name: "Signal damper", quantity: 2, tags: "comms" },
          { id: "4", name: "Dead radiation badge", quantity: 1, tags: "cover" },
        ],
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
        text: "Operative channel open. The Weaver's dead-channel ping is decoded: Relay 19. Ghost packet. Pull it before Pelsin scrubs the carrier.",
        timestamp: isoAt(-7),
      },
      {
        id: "dev-turn-2",
        speaker: "gm",
        label: "GM",
        meta: "Player-safe",
        text: "Relay 19 is the exterior comm mast bolted to Ganymede's pressure rim: HoloCan repeater, Board of Quality Control sensor plate, emergency beacon, and private Gold band running through lowColor hardware. The ghost packet is a corrupted data fragment stuck in its buffer. You do not know what it means yet. You do know Pelsin's diagnostic scrub starts in twenty minutes.",
        timestamp: isoAt(-6),
      },
      {
        id: "dev-turn-3",
        speaker: "player",
        label: "Player",
        meta: "Mara",
        text: "I keep one hand on the relay casing, angle my suit cam toward the damaged strut, and start pulling the ghost packet.",
        timestamp: isoAt(-5),
      },
      {
        id: "dev-turn-4",
        speaker: "gm",
        label: "GM",
        meta: "Player-safe",
        text: '[Red]"Cradle brake is drifting again," Oran says over comms. [Gray]"Technician," the supervisor cuts in. [Gray]"Explain why your slate just went dark."',
        timestamp: isoAt(-4),
      },
    ],
  };

  const suggestedActionsByCampaign = {
    [primaryCampaignId]: [
      {
        label: "Pull The Packet",
        prompt: "I start the buffer extraction and mask it as a repeater calibration fault.",
      },
      {
        label: "Distract The Gray",
        prompt: "I report the drifting cradle brake and make the supervisor look at the wrong failure first.",
      },
      {
        label: "Ask Oran",
        prompt: "I ask Oran to talk me through the cleanest way to kill the suit-cam feed for ten seconds.",
      },
    ],
  };

  const sceneParticipantsByCampaign = {
    [primaryCampaignId]: [
      {
        name: "Oran of Cimmeria",
        caste: "Red",
        role: "Relay crew lead",
        disposition: "friendly",
      },
      {
        name: "Lurcher Vexa ti Rhone",
        caste: "Gray",
        role: "Surface checkpoint supervisor",
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
