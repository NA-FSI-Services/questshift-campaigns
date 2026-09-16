"""Validate QuestShift campaign YAML (puzzle source of truth)."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

PUZZLE_TYPES = {"linux", "ansible", "openshift", "java"}
ROOM_REQUIRED = (
    "id",
    "order",
    "title",
    "mapX",
    "mapY",
    "puzzle_type",
    "narrative",
    "prompt",
    "expected_command_pattern",
    "accepted_examples",
    "hint",
    "success_narrative",
    "canvas_event",
    "clues",
)
SECRET_MARKERS = ("BEGIN PRIVATE KEY", "hf_", "AKIA", "openshift-v4")


def load_yaml(path: Path) -> Any:
    text = path.read_text(encoding="utf-8")
    for marker in SECRET_MARKERS:
        if marker in text:
            raise ValueError(f"{path}: looks like a secret ({marker})")
    data = yaml.safe_load(text)
    if not isinstance(data, dict):
        raise ValueError(f"{path}: campaign must be a mapping")
    return data


def _require(mapping: dict[str, Any], key: str, where: str) -> Any:
    if key not in mapping or mapping[key] in (None, "", []):
        raise ValueError(f"{where}: missing {key}")
    return mapping[key]


def validate_campaign(data: dict[str, Any], *, expected_id: str | None = "devops-dungeon") -> None:
    if data.get("kind") != "Campaign":
        raise ValueError("kind must be Campaign")
    metadata = data.get("metadata") or {}
    campaign_id = _require(metadata, "id", "metadata")
    if expected_id and campaign_id != expected_id:
        raise ValueError(f"v1 ships one campaign id {expected_id}, found {campaign_id}")
    duration = metadata.get("durationMinutes")
    if duration != 60:
        raise ValueError("metadata.durationMinutes must be 60")
    seats = data.get("seats") or []
    for seat in seats:
        if "required_seat" in seat or seat.get("required"):
            raise ValueError("seats must stay cosmetic; no required_seat")
    story = data.get("story") or {}
    for key in ("premise", "opening", "winCondition", "failCondition"):
        _require(story, key, "story")
    gm = data.get("game_master") or {}
    _require(gm, "system_prompt", "game_master")
    rooms = data.get("rooms") or []
    if len(rooms) != 5:
        raise ValueError("v1 campaign must have exactly five rooms")
    orders = []
    clue_ids: set[str] = set()
    for room in rooms:
        where = f"room {room.get('id', '?')}"
        for key in ROOM_REQUIRED:
            _require(room, key, where)
        if room["puzzle_type"] not in PUZZLE_TYPES:
            raise ValueError(f"{where}: puzzle_type must be one of {sorted(PUZZLE_TYPES)}")
        try:
            re.compile(str(room["expected_command_pattern"]))
        except re.error as exc:
            raise ValueError(f"{where}: invalid expected_command_pattern ({exc})") from exc
        for pattern in room.get("forbidden_patterns") or []:
            try:
                re.compile(str(pattern))
            except re.error as exc:
                raise ValueError(f"{where}: invalid forbidden_patterns ({exc})") from exc
        orders.append(int(room["order"]))
        if "required_seat" in room:
            raise ValueError(f"{where}: seats are cosmetic")
        _validate_clues(room, where, clue_ids)
    if sorted(orders) != list(range(1, 6)):
        raise ValueError("room order must be 1..5")


def _validate_clues(room: dict[str, Any], where: str, seen: set[str]) -> None:
    clues = room.get("clues") or []
    if not isinstance(clues, list) or not clues:
        raise ValueError(f"{where}: missing clues")
    for clue in clues:
        if not isinstance(clue, dict):
            raise ValueError(f"{where}: clue must be a mapping")
        for key in ("id", "label", "text", "x", "y"):
            if clue.get(key) in (None, ""):
                raise ValueError(f"{where}: clue missing {key}")
        clue_id = str(clue["id"])
        if clue_id in seen:
            raise ValueError(f"{where}: duplicate clue id {clue_id}")
        seen.add(clue_id)


def validate_dir(campaigns_dir: Path) -> list[Path]:
    files = sorted(campaigns_dir.glob("*.yaml")) + sorted(campaigns_dir.glob("*.yml"))
    files = [p for p in files if p.is_file()]
    if len(files) != 1:
        raise ValueError(f"v1 ships exactly one campaign YAML, found {len(files)}")
    validate_campaign(load_yaml(files[0]))
    return files


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    validate_dir(root / "campaigns")
    print("campaign YAML ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
