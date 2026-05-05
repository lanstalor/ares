const PORTRAIT_BY_NAME = new Map([
  ["dancer epsilon callo faran mine", "/portraits/dancer-epsilon-callo-faran-mine.png"],
  ["davan o tharsis", "/portraits/davan-o-tharsis.png"],
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
