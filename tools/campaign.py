"""Validate QuestShift campaign YAML (puzzle source of truth)."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

PUZZLE_TYPES = {"linux", "ansible", "openshift", "java"}
GUARDIAN_SPRITES = {
    "guardian_shell",
    "guardian_playbook",
    "guardian_pod",
    "guardian_servlet",
    "guardian_throne",
}
SHIPPED_IDS = frozenset({"devops-dungeon", "ansible-bastion"})
ROOM_REQUIRED = (
    "id",
    "order",
    "title",
    "mapX",
    "mapY",
    "puzzle_type",
    "guardian",
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


def validate_campaign(data: dict[str, Any], *, expected_id: str | None = None) -> None:
    if data.get("kind") != "Campaign":
        raise ValueError("kind must be Campaign")
    metadata = data.get("metadata") or {}
    campaign_id = _require(metadata, "id", "metadata")
    if expected_id is not None and campaign_id != expected_id:
        raise ValueError(f"expected campaign id {expected_id}, found {campaign_id}")
    if expected_id is None and campaign_id not in SHIPPED_IDS:
        raise ValueError(
            f"shipped campaign id must be one of {sorted(SHIPPED_IDS)}, found {campaign_id}"
        )
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
        raise ValueError("campaign must have exactly five rooms")
    orders = []
    clue_ids: set[str] = set()
    _validate_clues(story.get("clues"), "story", clue_ids)
    guardian_ids: set[str] = set()
    guardian_sprites: set[str] = set()
    for room in rooms:
        where = f"room {room.get('id', '?')}"
        for key in ROOM_REQUIRED:
            _require(room, key, where)
        if room["puzzle_type"] not in PUZZLE_TYPES:
            raise ValueError(f"{where}: puzzle_type must be one of {sorted(PUZZLE_TYPES)}")
        _validate_guardian(room, where, guardian_ids, guardian_sprites)
        try:
            re.compile(str(room["expected_command_pattern"]))
        except re.error as exc:
            raise ValueError(f"{where}: invalid expected_command_pattern ({exc})") from exc
        for pattern in room.get("forbidden_patterns") or []:
            try:
                re.compile(str(pattern))
            except re.error as exc:
                raise ValueError(f"{where}: invalid forbidden_patterns ({exc})") from exc
        _validate_miss_beats(room, where)
        orders.append(int(room["order"]))
        if "required_seat" in room:
            raise ValueError(f"{where}: seats are cosmetic")
        _validate_clues(room.get("clues"), where, clue_ids)
    if sorted(orders) != list(range(1, 6)):
        raise ValueError("room order must be 1..5")


def _validate_guardian(
    room: dict[str, Any],
    where: str,
    seen_ids: set[str],
    seen_sprites: set[str],
) -> None:
    guardian = room.get("guardian")
    if not isinstance(guardian, dict):
        raise ValueError(f"{where}: guardian must be a mapping")
    for key in ("id", "title", "sprite"):
        _require(guardian, key, f"{where}.guardian")
    sprite = str(guardian["sprite"])
    if sprite not in GUARDIAN_SPRITES:
        raise ValueError(f"{where}: guardian.sprite must be one of {sorted(GUARDIAN_SPRITES)}")
    guardian_id = str(guardian["id"])
    if guardian_id in seen_ids:
        raise ValueError(f"{where}: duplicate guardian id {guardian_id}")
    if sprite in seen_sprites:
        raise ValueError(f"{where}: duplicate guardian sprite {sprite}")
    seen_ids.add(guardian_id)
    seen_sprites.add(sprite)


def _validate_miss_beats(room: dict[str, Any], where: str) -> None:
    beats = room.get("miss_beats") or []
    if not beats:
        return
    if not isinstance(beats, list):
        raise ValueError(f"{where}: miss_beats must be a list")
    for beat in beats:
        if not isinstance(beat, dict):
            raise ValueError(f"{where}: miss_beat must be a mapping")
        pattern = beat.get("pattern")
        message = beat.get("message")
        if not pattern or not str(message or "").strip():
            raise ValueError(f"{where}: miss_beat needs pattern and message")
        try:
            re.compile(str(pattern))
        except re.error as exc:
            raise ValueError(f"{where}: invalid miss_beats pattern ({exc})") from exc


def _validate_clues(clues: Any, where: str, seen: set[str]) -> None:
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
    if len(files) != 2:
        raise ValueError(
            f"shipped campaigns are exactly two YAMLs (devops-dungeon + ansible-bastion), "
            f"found {len(files)}"
        )
    found_ids: set[str] = set()
    for path in files:
        data = load_yaml(path)
        validate_campaign(data)
        found_ids.add(str(data["metadata"]["id"]))
    if found_ids != SHIPPED_IDS:
        raise ValueError(f"expected ids {sorted(SHIPPED_IDS)}, found {sorted(found_ids)}")
    return files


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    validate_dir(root / "campaigns")
    print("campaign YAML ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
