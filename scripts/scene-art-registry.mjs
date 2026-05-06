#!/usr/bin/env node

import { SCENE_ART_LIBRARY, normalizeSceneText } from "../frontend/src/lib/sceneArtLibrary.js";
import backlog from "../data/assets/scene_generation_backlog.json" with { type: "json" };

function printUsage() {
  console.log(`Usage:
  node scripts/scene-art-registry.mjs list
  node scripts/scene-art-registry.mjs backlog
  node scripts/scene-art-registry.mjs match --query "spaceship hangar" [--tone gold] [--scope generic]
`);
}

function parseArgs(argv) {
  const args = { _: [] };
  for (let i = 0; i < argv.length; i += 1) {
    const token = argv[i];
    if (token.startsWith("--")) {
      const key = token.slice(2);
      const value = argv[i + 1] && !argv[i + 1].startsWith("--") ? argv[++i] : "true";
      args[key] = value;
    } else {
      args._.push(token);
    }
  }
  return args;
}

function scoreEntry(entry, queryTokens, tone, scope) {
  const normalizedLabel = normalizeSceneText(entry.label);
  const normalizedConcept = normalizeSceneText(entry.concept);
  const normalizedKeywords = entry.keywords.map(normalizeSceneText);
  let score = 0;

  for (const token of queryTokens) {
    if (normalizedLabel.includes(token)) score += 5;
    if (normalizedConcept.includes(token)) score += 4;
    if (normalizedKeywords.some((keyword) => keyword.includes(token))) score += 3;
  }

  if (tone && entry.tone === tone) score += 2;
  if (scope && entry.scope === scope) score += 2;

  return score;
}

function listLibrary() {
  for (const entry of SCENE_ART_LIBRARY) {
    console.log([
      entry.id,
      entry.label,
      entry.scope,
      entry.tone,
      entry.category,
      entry.src,
    ].join(" | "));
  }
}

function listBacklog() {
  for (const entry of backlog) {
    console.log([
      entry.id,
      entry.status,
      entry.scope,
      entry.preferredAssetId ?? "-",
      entry.label,
    ].join(" | "));
  }
}

function matchScene({ query, tone, scope }) {
  const normalized = normalizeSceneText(query);
  const queryTokens = normalized.split(" ").filter(Boolean);
  const matches = SCENE_ART_LIBRARY
    .map((entry) => ({
      ...entry,
      score: scoreEntry(entry, queryTokens, tone, scope),
    }))
    .filter((entry) => entry.score > 0)
    .sort((a, b) => b.score - a.score || a.label.localeCompare(b.label));

  if (!matches.length) {
    console.log(`No current scene art match for: ${query}`);
    const backlogMatch = backlog.find((entry) =>
      entry.searchTerms.some((term) => normalizeSceneText(term).includes(normalized)),
    );
    if (backlogMatch) {
      console.log(`Closest backlog item: ${backlogMatch.label} (${backlogMatch.status})`);
    }
    return 1;
  }

  for (const entry of matches.slice(0, 5)) {
    console.log([
      entry.score,
      entry.id,
      entry.label,
      entry.scope,
      entry.tone,
      entry.src,
      `keywords=${entry.keywords.join(", ")}`,
    ].join(" | "));
  }

  const best = matches[0];
  const coveredBacklog = backlog.filter((entry) => entry.preferredAssetId === best.id);
  for (const entry of coveredBacklog) {
    console.log(`Backlog coverage: ${entry.label} (${entry.status})`);
  }
  return 0;
}

const args = parseArgs(process.argv.slice(2));
const [command] = args._;

if (!command || command === "help" || command === "--help") {
  printUsage();
  process.exit(0);
}

if (command === "list") {
  listLibrary();
  process.exit(0);
}

if (command === "backlog") {
  listBacklog();
  process.exit(0);
}

if (command === "match") {
  if (!args.query) {
    console.error("match requires --query");
    process.exit(1);
  }
  process.exit(matchScene({ query: args.query, tone: args.tone, scope: args.scope }));
}

printUsage();
process.exit(1);
