const CASTE_COLOR_MAP = {
  red: "var(--color-red)",
  highred: "var(--color-red)",
  lowred: "var(--color-red)",
  gold: "var(--color-gold)",
  gray: "var(--color-gray)",
  grey: "var(--color-gray)",
  obsidian: "var(--color-obsidian)",
  blue: "var(--color-blue)",
  green: "var(--color-green)",
  orange: "var(--color-orange)",
  yellow: "var(--color-yellow)",
  pink: "var(--color-pink)",
  white: "var(--color-white)",
  silver: "var(--color-silver)",
  copper: "var(--color-copper)",
  brown: "var(--color-brown)",
  violet: "var(--color-violet)",
};

const GOLD_THEME_MATCHERS = [
  "gold",
  "arch",
  "praetor",
  "governor",
  "house",
  "citadel",
  "senate",
  "imperial",
  "official",
  "augustus",
  "bellona",
  "palace",
  "administrative",
];

export function getCasteColorToken(label) {
  if (!label) {
    return "var(--text-primary)";
  }

  const normalized = String(label).toLowerCase().replace(/\s+/g, "");

  for (const [key, value] of Object.entries(CASTE_COLOR_MAP)) {
    if (normalized.includes(key)) {
      return value;
    }
  }

  return "var(--text-primary)";
}

export function deriveSceneTone({ campaignState, selectedCampaign, turns }) {
  const text = [
    selectedCampaign?.name,
    selectedCampaign?.tagline,
    selectedCampaign?.current_location_label,
    campaignState?.current_location,
    campaignState?.active_objective,
    turns?.[turns.length - 1]?.text,
  ]
    .filter(Boolean)
    .join(" ")
    .toLowerCase();

  if (GOLD_THEME_MATCHERS.some((term) => text.includes(term))) {
    return "gold";
  }

  return "friendly";
}

export function buildSceneParticipants({ campaignState, selectedCampaign, sceneTone }) {
  const player = campaignState?.player_character
    ? {
        id: campaignState.player_character.id,
        name: campaignState.player_character.name,
        caste: campaignState.player_character.race ?? "HighRed",
        role: campaignState.player_character.character_class ?? "Operative",
        tone: "player",
        active: true,
      }
    : null;

  const placeholderParticipants =
    sceneTone === "gold"
      ? [
          {
            id: "gold-proxy",
            name: "Dominus Severa au Cador",
            caste: "Gold",
            role: "Official presence",
            tone: "watcher",
            active: false,
          },
          {
            id: "gray-escort",
            name: "Lurcher Vexa ti Rhone",
            caste: "Gray",
            role: "Security escort",
            tone: "support",
            active: false,
          },
        ]
      : [
          {
            id: "red-contact",
            name: "Tavi of Ceres Row",
            caste: "Red",
            role: "Dock contact",
            tone: "support",
            active: false,
          },
          {
            id: "blue-handler",
            name: "Lys xe Morrow",
            caste: "Blue",
            role: "Relay analyst",
            tone: "support",
            active: false,
          },
        ];

  const systemParticipant = {
    id: "relay",
    name: selectedCampaign ? "Ares Relay" : "Command Uplink",
    caste: "System",
    role: selectedCampaign ? "Encrypted GM runtime" : "Standby link",
    tone: "system",
    active: !player,
  };

  return [player, ...placeholderParticipants, systemParticipant].filter(Boolean);
}

export function buildActionPresets(sceneTone) {
  if (sceneTone === "gold") {
    return [
      { id: "petition", key: "1", label: "Petition", icon: "[]", prompt: "I make a controlled, formal appeal and ask what this authority wants from us." },
      { id: "observe", key: "2", label: "Observe", icon: "++", prompt: "I stay quiet, study the room, and look for pressure points, hierarchy, and hidden threats." },
      { id: "deceive", key: "3", label: "Deceive", icon: "//", prompt: "I maintain cover and offer a plausible lie that protects the cell's real objective." },
      { id: "withdraw", key: "4", label: "Withdraw", icon: "--", prompt: "I disengage carefully and look for the cleanest exit without escalating suspicion." },
    ];
  }

  return [
    { id: "talk", key: "1", label: "Talk", icon: "[]", prompt: "I talk to them plainly and try to build trust before pushing for information." },
    { id: "bribe", key: "2", label: "Bribe", icon: "$$", prompt: "I offer credits, favors, or gear to loosen their tongue and see what they know." },
    { id: "shadow", key: "3", label: "Shadow", icon: "//", prompt: "I hang back, observe quietly, and follow without revealing myself yet." },
    { id: "inspect", key: "4", label: "Inspect", icon: "++", prompt: "I inspect the scene carefully for clues, surveillance, hidden access points, or useful leverage." },
  ];
}
