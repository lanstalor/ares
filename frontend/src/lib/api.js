const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";
const API_PREFIX = `${API_BASE_URL}/api/v1`;

async function readJson(response, fallbackMessage) {
  if (response.ok) {
    return response.json();
  }

  let detail = fallbackMessage;

  try {
    const payload = await response.json();
    if (typeof payload?.detail === "string" && payload.detail.trim()) {
      detail = payload.detail;
    }
  } catch {
    // Ignore JSON parsing failures and keep the fallback message.
  }

  throw new Error(detail);
}

async function request(path, options = {}, fallbackMessage = "Request failed") {
  const response = await fetch(`${API_PREFIX}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers ?? {}),
    },
    ...options,
  });

  return readJson(response, fallbackMessage);
}

export function getHealth() {
  return request("/health", {}, "Backend health check failed");
}

export function getSystemStatus() {
  return request("/system/status", {}, "System status request failed");
}

export function listCampaigns() {
  return request("/campaigns", {}, "Campaign list request failed");
}

export function createCampaign(payload) {
  return request("/campaigns", {
    method: "POST",
    body: JSON.stringify(payload),
  }, "Campaign creation failed");
}

export function getCampaignState(campaignId) {
  return request(`/campaigns/${campaignId}/state`, {}, "Campaign state request failed");
}

export function listTurns(campaignId, limit = 50) {
  return request(`/campaigns/${campaignId}/turns?limit=${limit}`, {}, "Turn history request failed");
}

export function submitTurn(campaignId, payload) {
  return request(`/campaigns/${campaignId}/turns`, {
    method: "POST",
    body: JSON.stringify(payload),
  }, "Turn submission failed");
}

export function submitClarification(campaignId, payload) {
  return request(`/campaigns/${campaignId}/clarify`, {
    method: "POST",
    body: JSON.stringify(payload),
  }, "Clarification request failed");
}

export function fetchMemories(campaignId, limit = 5) {
  return request(`/campaigns/${campaignId}/memories?limit=${limit}`, {}, "Memory fetch failed");
}

export function getCurrentSceneArt(campaignId) {
  return request(`/campaigns/${campaignId}/scene-art/current`, {}, "Scene art request failed");
}

export function regenerateSceneArt(campaignId, payload = {}) {
  return request(`/campaigns/${campaignId}/scene-art/regenerate`, {
    method: "POST",
    body: JSON.stringify(payload),
  }, "Scene art regeneration failed");
}

export function seedWorldBible(payload = {}) {
  return request("/seed/world-bible", {
    method: "POST",
    body: JSON.stringify(payload),
  }, "World bible seed request failed");
}

export { API_BASE_URL };
