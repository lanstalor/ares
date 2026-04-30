"""Reporter: assembles per-turn scores and holistic analysis into a markdown report."""

from datetime import datetime
from pathlib import Path

from evaluator import TurnScore

REPORTS_DIR = Path(__file__).parent / "reports"


def write_report(
    campaign_id: str,
    transcript: list[dict],
    scores: list[TurnScore],
    holistic: str,
    backend_url: str,
    player_model: str,
    evaluator_model: str,
) -> Path:
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M")
    report_path = REPORTS_DIR / f"{timestamp}.md"

    lines = [
        f"# Ares Playtester Report — {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "## Run Summary",
        "",
        f"- Turns: {len(transcript)}",
        f"- Campaign ID: `{campaign_id}`",
        f"- Player model: {player_model}",
        f"- Evaluator model: {evaluator_model}",
        f"- Backend: {backend_url}",
        "",
        "---",
        "",
        "## Per-Turn Log",
        "",
    ]

    for entry, score in zip(transcript, scores):
        n = entry["turn_number"]
        lines += [
            f"### Turn {n}",
            "",
            f"**Player:** {entry['player_input']}",
            "",
            f"**GM:** {entry['gm_response']}",
            "",
            score.to_markdown_table(),
            "",
            f"**Overall: {score.average()}**",
            "",
            "---",
            "",
        ]

    lines += [
        "## Holistic Analysis",
        "",
        holistic,
        "",
    ]

    report_path.write_text("\n".join(lines), encoding="utf-8")
    return report_path
