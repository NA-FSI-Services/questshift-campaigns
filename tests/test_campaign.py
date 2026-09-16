from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from tools.campaign import load_yaml, main, validate_campaign, validate_dir

ROOT = Path(__file__).resolve().parents[1]
CANONICAL = ROOT / "campaigns" / "campaign-devops-dungeon.yaml"


def test_canonical_campaign_passes() -> None:
    validate_dir(ROOT / "campaigns")
    data = load_yaml(CANONICAL)
    assert data["metadata"]["id"] == "devops-dungeon"
    assert len(data["rooms"]) == 5


def test_main_prints_ok(capsys: pytest.CaptureFixture[str]) -> None:
    assert main() == 0
    assert "ok" in capsys.readouterr().out


def test_rejects_wrong_kind() -> None:
    with pytest.raises(ValueError, match="kind"):
        validate_campaign({"kind": "Dungeon"})


def test_rejects_wrong_id() -> None:
    data = load_yaml(CANONICAL)
    data["metadata"]["id"] = "other"
    with pytest.raises(ValueError, match="one campaign"):
        validate_campaign(data)


def test_rejects_duration() -> None:
    data = load_yaml(CANONICAL)
    data["metadata"]["durationMinutes"] = 90
    with pytest.raises(ValueError, match="60"):
        validate_campaign(data)


def test_rejects_required_seat() -> None:
    data = load_yaml(CANONICAL)
    data["seats"][0]["required_seat"] = "guardian"
    with pytest.raises(ValueError, match="cosmetic"):
        validate_campaign(data)


def test_rejects_bad_puzzle_type() -> None:
    data = load_yaml(CANONICAL)
    data["rooms"][0]["puzzle_type"] = "riddle"
    with pytest.raises(ValueError, match="puzzle_type"):
        validate_campaign(data)


def test_rejects_bad_regex() -> None:
    data = load_yaml(CANONICAL)
    data["rooms"][0]["expected_command_pattern"] = "("
    with pytest.raises(ValueError, match="expected_command_pattern"):
        validate_campaign(data)


def test_rejects_bad_forbidden_regex() -> None:
    data = load_yaml(CANONICAL)
    data["rooms"][0]["forbidden_patterns"] = ["("]
    with pytest.raises(ValueError, match="forbidden_patterns"):
        validate_campaign(data)


def test_rejects_room_required_seat() -> None:
    data = load_yaml(CANONICAL)
    data["rooms"][0]["required_seat"] = "guardian"
    with pytest.raises(ValueError, match="cosmetic"):
        validate_campaign(data)


def test_rejects_wrong_room_count() -> None:
    data = load_yaml(CANONICAL)
    data["rooms"] = data["rooms"][:1]
    with pytest.raises(ValueError, match="five rooms"):
        validate_campaign(data)


def test_rejects_missing_story() -> None:
    data = load_yaml(CANONICAL)
    del data["story"]["opening"]
    with pytest.raises(ValueError, match="opening"):
        validate_campaign(data)


def test_rejects_secret_text(tmp_path: Path) -> None:
    path = tmp_path / "bad.yaml"
    path.write_text("kind: Campaign\nhf_secret: hf_abc\n", encoding="utf-8")
    with pytest.raises(ValueError, match="secret"):
        load_yaml(path)


def test_rejects_non_mapping(tmp_path: Path) -> None:
    path = tmp_path / "list.yaml"
    path.write_text("- not a map\n", encoding="utf-8")
    with pytest.raises(ValueError, match="mapping"):
        load_yaml(path)


def test_validate_dir_wrong_count(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="exactly one"):
        validate_dir(tmp_path)
    (tmp_path / "a.yaml").write_text(CANONICAL.read_text(encoding="utf-8"), encoding="utf-8")
    (tmp_path / "b.yaml").write_text(CANONICAL.read_text(encoding="utf-8"), encoding="utf-8")
    with pytest.raises(ValueError, match="exactly one"):
        validate_dir(tmp_path)


def test_yaml_roundtrip_keeps_rooms() -> None:
    data = yaml.safe_load(CANONICAL.read_text(encoding="utf-8"))
    assert {room["id"] for room in data["rooms"]} >= {
        "room-01-broken-shell",
        "room-05-operators-throne",
    }


def test_rejects_missing_metadata_id() -> None:
    data = load_yaml(CANONICAL)
    del data["metadata"]["id"]
    with pytest.raises(ValueError, match="id"):
        validate_campaign(data)


def test_rejects_missing_room_field() -> None:
    data = load_yaml(CANONICAL)
    del data["rooms"][0]["hint"]
    with pytest.raises(ValueError, match="hint"):
        validate_campaign(data)


def test_rejects_missing_clues() -> None:
    data = load_yaml(CANONICAL)
    data["rooms"][0]["clues"] = []
    with pytest.raises(ValueError, match="clues"):
        validate_campaign(data)


def test_rejects_clue_not_mapping() -> None:
    data = load_yaml(CANONICAL)
    data["rooms"][0]["clues"] = ["not-a-map"]
    with pytest.raises(ValueError, match="mapping"):
        validate_campaign(data)


def test_rejects_clue_missing_text() -> None:
    data = load_yaml(CANONICAL)
    del data["rooms"][0]["clues"][0]["text"]
    with pytest.raises(ValueError, match="text"):
        validate_campaign(data)


def test_rejects_wrong_room_order() -> None:
    data = load_yaml(CANONICAL)
    data["rooms"][0]["order"] = 2
    with pytest.raises(ValueError, match="order"):
        validate_campaign(data)


def test_rejects_required_seat_flag() -> None:
    data = load_yaml(CANONICAL)
    data["seats"][0]["required"] = True
    with pytest.raises(ValueError, match="cosmetic"):
        validate_campaign(data)


def test_allows_other_id_when_expected_none() -> None:
    data = load_yaml(CANONICAL)
    data["metadata"]["id"] = "other-dungeon"
    validate_campaign(data, expected_id=None)
