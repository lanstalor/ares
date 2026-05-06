const PORTRAIT_BY_NAME = new Map([
  ["dancer epsilon callo faran mine", "/portraits/dancer-epsilon-callo-faran-mine.png"],
  ["davan o tharsis", "/portraits/davan-o-tharsis.png"],
  ["davan of tharsis", "/portraits/davan-of-tharsis.png"],
  ["fitchner au barca ares", "/portraits/fitchner-au-barca-ares.png"],
  ["holiday ti nakamura", "/portraits/holiday-ti-nakamura.png"],
  ["legate voss ti harlan", "/portraits/legate-voss-ti-harlan.png"],
  ["lorn au arcos", "/portraits/lorn-au-arcos.png"],
  ["nero au augustus", "/portraits/nero-au-augustus.png"],
  ["regulus ag sun quicksilver", "/portraits/regulus-ag-sun-quicksilver.png"],
  ["ryanna of cryssos", "/portraits/ryanna-of-cryssos.png"],
  ["syla au codovan", "/portraits/syla-au-codovan.png"],
  ["trigg ti nakamura", "/portraits/trigg-ti-nakamura.png"],
  ["vex of gamma", "/portraits/vex-of-gamma.png"],
]);

function normalizePortraitName(value) {
  return String(value ?? "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, " ")
    .trim();
}

/**
 * Slugify a character name to match backend slug generation.
 * Mirrors app/services/npc_portrait_service.py slugify_npc_name()
 */
export function slugifyCharacterName(name) {
  if (!name) {
    return "unknown-npc";
  }

  let slug = String(name).toLowerCase();
  slug = slug.replace(/[^a-z0-9]+/g, "-");
  slug = slug.replace(/^-+|-+$/g, "");
  slug = slug.substring(0, 120);

  if (!slug) {
    return "unknown-npc";
  }

  return slug;
}

export function resolvePortrait(name) {
  const normalized = normalizePortraitName(name);
  if (!normalized) return null;

  if (PORTRAIT_BY_NAME.has(normalized)) {
    return PORTRAIT_BY_NAME.get(normalized);
  }

  for (const [key, src] of PORTRAIT_BY_NAME.entries()) {
    if (key.includes(normalized) || normalized.includes(key)) {
      return src;
    }
  }

  const firstLast = normalized.split(" ").filter(Boolean);
  if (firstLast.length >= 2) {
    const compact = `${firstLast[0]} ${firstLast[firstLast.length - 1]}`;
    for (const [key, src] of PORTRAIT_BY_NAME.entries()) {
      if (key.includes(compact)) return src;
    }
  }

  return null;
}

/**
 * Get the computed portrait URL for a character, using the backend-generated slug.
 * Falls back to static library if needed.
 */
export function getGeneratedPortraitUrl(character) {
  if (!character || !character.name) {
    return null;
  }

  return `/portraits/${slugifyCharacterName(character.name)}.png`;
}
