const MODEL_KEYS = [
  "ai_model",
  "ai_generation_model",
  "generation_model",
  "model",
  "ares_model",
];

const SEEDED_FLAG_KEYS = [
  "campaign_seeded",
  "world_bible_seeded",
  "seeded_campaign_exists",
  "canonical_campaign_seeded",
];

const SEEDED_CAMPAIGN_ID_KEYS = [
  "seeded_campaign_id",
  "canonical_campaign_id",
];

const SEEDED_CAMPAIGN_NAME_KEYS = [
  "seeded_campaign_name",
  "canonical_campaign_name",
];

function getFirstDefined(record, keys) {
  if (!record) return undefined;

  for (const key of keys) {
    if (record[key] !== undefined && record[key] !== null && record[key] !== "") {
      return record[key];
    }
  }

  return undefined;
}

function getFirstBoolean(record, keys) {
  if (!record) return undefined;

  for (const key of keys) {
    if (typeof record[key] === "boolean") {
      return record[key];
    }
  }

  return undefined;
}

function buildProviderReadiness(healthStatus, systemStatus) {
  if (healthStatus?.status !== "ok") {
    return {
      tone: "bad",
      label: "offline",
      detail: "Backend health check is not passing, so provider selection is unverified.",
    };
  }

  const provider = systemStatus?.ai_generation_provider;
  const model = getFirstDefined(systemStatus, MODEL_KEYS);

  if (!provider) {
    return {
      tone: "warn",
      label: "unknown",
      detail: "Backend is up, but no generation provider was exposed.",
    };
  }

  return {
    tone: "good",
    label: provider,
    detail: model ? `Model ${model}` : "Model not exposed by current system status payload.",
  };
}

function buildWorldBibleReadiness(systemStatus) {
  if (!systemStatus) {
    return {
      tone: "bad",
      label: "unknown",
      detail: "System status is unavailable.",
    };
  }

  if (systemStatus.world_bible_exists) {
    return {
      tone: "good",
      label: "visible",
      detail: systemStatus.world_bible_path,
    };
  }

  return {
    tone: "bad",
    label: "missing",
    detail: systemStatus.world_bible_path || "Backend did not expose a world bible path.",
  };
}

function buildCampaignSeedReadiness(systemStatus, campaigns, lastSeedResult) {
  const explicitSeeded = getFirstBoolean(systemStatus, SEEDED_FLAG_KEYS);
  const seededCampaignId = getFirstDefined(systemStatus, SEEDED_CAMPAIGN_ID_KEYS);
  const seededCampaignName = getFirstDefined(systemStatus, SEEDED_CAMPAIGN_NAME_KEYS);

  if (explicitSeeded === false) {
    return {
      tone: "warn",
      label: "not seeded",
      detail: "Backend explicitly reports no canonical seeded campaign.",
    };
  }

  if (explicitSeeded === true || seededCampaignId || seededCampaignName) {
    return {
      tone: "good",
      label: "seeded",
      detail: seededCampaignName || seededCampaignId || "Backend reports a canonical seeded campaign.",
    };
  }

  if (lastSeedResult) {
    return {
      tone: "good",
      label: "seeded",
      detail: `${lastSeedResult.campaign_name} from ${lastSeedResult.source_path}`,
    };
  }

  if (!campaigns.length) {
    return {
      tone: "warn",
      label: "not seeded",
      detail: "No campaigns are loaded yet.",
    };
  }

  return {
    tone: "warn",
    label: "unknown",
    detail: "Campaigns exist, but current API routes do not identify which one came from world_bible.md.",
  };
}

export function deriveShellReadiness({ healthStatus, systemStatus, campaigns, lastSeedResult }) {
  return {
    provider: buildProviderReadiness(healthStatus, systemStatus),
    worldBible: buildWorldBibleReadiness(systemStatus),
    campaignSeed: buildCampaignSeedReadiness(systemStatus, campaigns, lastSeedResult),
  };
}
