#!/usr/bin/env python3
"""
Ares Playtester — automated 30-turn campaign simulation with UX evaluation.

Requires:
  - Backend running at localhost:8000 (make backend-dev or make compose-up)
  - ANTHROPIC_API_KEY in repo root .env or environment

Usage:
  cd tools/playtester && pip install -r requirements.txt
  python run.py
"""

import os
import sys
from pathlib import Path

# Load .env from repo root
env_path = Path(__file__).parent.parent.parent / ".env"
if env_path.exists():
    from dotenv import load_dotenv
    load_dotenv(env_path)

import anthropic
import httpx

from player import PlayerAgent
from evaluator import EvaluatorAgent, TurnScore
from reporter import write_report

BACKEND_URL = os.getenv("ARES_BACKEND_URL", "http://localhost:8000")
NUM_TURNS = 30
PLAYER_CONTEXT_WINDOW = 5  # last N GM responses fed to the player agent


def seed_campaign(http: httpx.Client) -> str:
    print("→ Seeding fresh campaign...")
    resp = http.post(
        f"{BACKEND_URL}/api/v1/seed/world-bible",
        json={"campaign_name_override": "Playtester Run"},
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    campaign_id = data["campaign_id"]
    print(f"  Campaign ID: {campaign_id}")
    print(
        f"  Seeded: {data['factions_imported']} factions, {data['npcs_imported']} NPCs, "
        f"{data['areas_imported']} areas, {data['secrets_imported']} secrets"
    )
    return campaign_id


def submit_turn(http: httpx.Client, campaign_id: str, player_input: str) -> dict:
    resp = http.post(
        f"{BACKEND_URL}/api/v1/campaigns/{campaign_id}/turns",
        json={"player_input": player_input},
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()


def main() -> None:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY not set. Add it to .env or environment.", file=sys.stderr)
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)
    player = PlayerAgent(client)
    evaluator = EvaluatorAgent(client)

    transcript: list[dict] = []
    scores: list[TurnScore] = []
    recent_gm: list[str] = []

    with httpx.Client() as http:
        # Verify backend is reachable
        try:
            health = http.get(f"{BACKEND_URL}/api/v1/system/health", timeout=5)
            health.raise_for_status()
        except Exception as e:
            print(f"ERROR: Backend not reachable at {BACKEND_URL}: {e}", file=sys.stderr)
            print("Start the backend with: make backend-dev  (or make compose-up)", file=sys.stderr)
            sys.exit(1)

        campaign_id = seed_campaign(http)

        print(f"\n{'='*60}")
        print(f"Starting {NUM_TURNS}-turn playtester session")
        print(f"{'='*60}\n")

        for turn_num in range(1, NUM_TURNS + 1):
            print(f"--- Turn {turn_num}/{NUM_TURNS} ---")

            # Player generates action
            if not recent_gm:
                player_input = "I take in my surroundings and assess what needs doing before the shift starts."
            else:
                player_input = player.next_action(recent_gm[-PLAYER_CONTEXT_WINDOW:])
            print(f"  Player: {player_input}")

            # Submit to backend
            try:
                result = submit_turn(http, campaign_id, player_input)
            except httpx.HTTPError as e:
                print(f"  [SKIP] Turn {turn_num} failed: {e}")
                continue

            gm_response = result["turn"]["gm_response"]
            print(f"  GM:     {gm_response[:120]}{'...' if len(gm_response) > 120 else ''}")

            # Record turn
            entry = {
                "turn_number": turn_num,
                "player_input": player_input,
                "gm_response": gm_response,
            }
            transcript.append(entry)
            recent_gm.append(gm_response)

            # Evaluate
            score = evaluator.score_turn(turn_num, player_input, gm_response, transcript)
            scores.append(score)
            avg = score.average()
            dim_summary = "  ".join(
                f"{k[0].upper()}:{score.data.get(k, {}).get('score', '?')}"
                for k in ["realism", "continuity", "engagement", "repetition", "quality", "flow"]
            )
            print(f"  Scores: {dim_summary}  avg={avg}")
            print()

        print(f"{'='*60}")
        print("Running holistic analysis...")
        print(f"{'='*60}\n")

        holistic = evaluator.holistic_summary(transcript, scores)

        report_path = write_report(campaign_id, transcript, scores, holistic, BACKEND_URL)
        print(f"\nReport saved: {report_path}")
        print("\n--- Holistic Summary Preview ---")
        preview_lines = holistic.splitlines()[:20]
        print("\n".join(preview_lines))
        if len(holistic.splitlines()) > 20:
            print(f"... ({len(holistic.splitlines()) - 20} more lines in report)")


if __name__ == "__main__":
    main()
