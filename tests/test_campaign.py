from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from tools.campaign import SHIPPED_IDS, load_yaml, main, validate_campaign, validate_dir

ROOT = Path(__file__).resolve().parents[1]
CANONICAL = ROOT / "campaigns" / "campaign-devops-dungeon.yaml"
ANSIBLE = ROOT / "campaigns" / "campaign-ansible-bastion.yaml"


def test_canonical_campaign_passes() -> None:
    validate_dir(ROOT / "campaigns")
    data = load_yaml(CANONICAL)
    assert data["metadata"]["id"] == "devops-dungeon"
    assert len(data["rooms"]) == 5
    ansible = load_yaml(ANSIBLE)
    assert ansible["metadata"]["id"] == "ansible-bastion"
    assert len(ansible["rooms"]) == 5
    assert {room["puzzle_type"] for room in ansible["rooms"]} == {"ansible"}
    assert SHIPPED_IDS == {"devops-dungeon", "ansible-bastion"}


def test_main_prints_ok(capsys: pytest.CaptureFixture[str]) -> None:
    assert main() == 0
    assert "ok" in capsys.readouterr().out


def test_rejects_wrong_kind() -> None:
    with pytest.raises(ValueError, match="kind"):
        validate_campaign({"kind": "Dungeon"})


def test_rejects_wrong_id() -> None:
    data = load_yaml(CANONICAL)
    data["metadata"]["id"] = "other"
    with pytest.raises(ValueError, match="shipped campaign id"):
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
    with pytest.raises(ValueError, match="exactly two"):
        validate_dir(tmp_path)
    (tmp_path / "a.yaml").write_text(CANONICAL.read_text(encoding="utf-8"), encoding="utf-8")
    with pytest.raises(ValueError, match="exactly two"):
        validate_dir(tmp_path)
    # Two copies of devops-dungeon → wrong id set
    (tmp_path / "b.yaml").write_text(CANONICAL.read_text(encoding="utf-8"), encoding="utf-8")
    with pytest.raises(ValueError, match="expected ids"):
        validate_dir(tmp_path)


def test_validate_dir_accepts_shipped_pair() -> None:
    files = validate_dir(ROOT / "campaigns")
    assert {p.name for p in files} == {
        "campaign-devops-dungeon.yaml",
        "campaign-ansible-bastion.yaml",
    }


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


def test_rejects_missing_lobby_clues() -> None:
    data = load_yaml(CANONICAL)
    data["story"]["clues"] = []
    with pytest.raises(ValueError, match="story"):
        validate_campaign(data)


def test_rejects_duplicate_lobby_and_room_clue_id() -> None:
    data = load_yaml(CANONICAL)
    data["story"]["clues"][0]["id"] = data["rooms"][0]["clues"][0]["id"]
    with pytest.raises(ValueError, match="duplicate clue id"):
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


def test_allows_explicit_expected_id() -> None:
    data = load_yaml(CANONICAL)
    validate_campaign(data, expected_id="devops-dungeon")
    ansible = load_yaml(ANSIBLE)
    validate_campaign(ansible, expected_id="ansible-bastion")


def test_rejects_mismatched_expected_id() -> None:
    data = load_yaml(CANONICAL)
    with pytest.raises(ValueError, match="expected campaign id"):
        validate_campaign(data, expected_id="ansible-bastion")


def test_lobby_clues_stay_on_the_overworld() -> None:
    data = load_yaml(CANONICAL)
    lobby = {clue["id"]: clue for clue in data["story"]["clues"]}
    assert set(lobby) == {"lobby-hour", "lobby-gates", "lobby-premise"}
    room_ids = {clue["id"] for room in data["rooms"] for clue in room["clues"]}
    assert set(lobby).isdisjoint(room_ids)
    assert "grep -i rune" not in lobby["lobby-hour"]["text"]
    assert "hosts: dungeon" not in lobby["lobby-gates"]["text"]
    shell = data["rooms"][0]
    assert shell["id"] == "room-01-broken-shell"
    assert {clue["id"] for clue in shell["clues"]} == {"shell-tree", "shell-log", "shell-man"}


def test_broken_shell_teaches_tree_log_and_man() -> None:
    data = load_yaml(CANONICAL)
    room = data["rooms"][0]
    by_id = {clue["id"]: clue for clue in room["clues"]}
    assert "quest.log" in by_id["shell-tree"]["text"]
    assert "rune=THORN" in by_id["shell-log"]["text"]
    assert "GREP(1)" in by_id["shell-man"]["text"]
    assert "$NF" in by_id["shell-man"]["text"]
    assert len(room["miss_beats"]) == 2
    assert room["guardian"]["sprite"] == "guardian_shell"
    assert "north challenge door" in room["narrative"]
    assert "south door" in room["narrative"]


def test_every_room_has_a_distinct_guardian() -> None:
    data = load_yaml(CANONICAL)
    sprites = [room["guardian"]["sprite"] for room in data["rooms"]]
    assert sprites == [
        "guardian_shell",
        "guardian_playbook",
        "guardian_pod",
        "guardian_servlet",
        "guardian_throne",
    ]
    for room in data["rooms"]:
        assert "north challenge door" in room["narrative"]
        assert "lobby" in room["narrative"]
        assert "north door unseals" in room["success_narrative"]


def test_rejects_missing_guardian() -> None:
    data = load_yaml(CANONICAL)
    del data["rooms"][0]["guardian"]
    with pytest.raises(ValueError, match="guardian"):
        validate_campaign(data)


def test_rejects_unknown_guardian_sprite() -> None:
    data = load_yaml(CANONICAL)
    data["rooms"][0]["guardian"]["sprite"] = "dragon"
    with pytest.raises(ValueError, match="guardian.sprite"):
        validate_campaign(data)


def test_rejects_duplicate_guardian_sprite() -> None:
    data = load_yaml(CANONICAL)
    data["rooms"][1]["guardian"]["sprite"] = "guardian_shell"
    with pytest.raises(ValueError, match="duplicate guardian sprite"):
        validate_campaign(data)


def test_rejects_duplicate_guardian_id() -> None:
    data = load_yaml(CANONICAL)
    data["rooms"][1]["guardian"]["id"] = data["rooms"][0]["guardian"]["id"]
    with pytest.raises(ValueError, match="duplicate guardian id"):
        validate_campaign(data)


def test_rejects_guardian_not_mapping() -> None:
    data = load_yaml(CANONICAL)
    data["rooms"][0]["guardian"] = "golem"
    with pytest.raises(ValueError, match="mapping"):
        validate_campaign(data)


def test_rejects_bad_miss_beat() -> None:
    data = load_yaml(CANONICAL)
    data["rooms"][0]["miss_beats"] = [{"pattern": "(", "message": "nope"}]
    with pytest.raises(ValueError, match="miss_beats"):
        validate_campaign(data)
    data["rooms"][0]["miss_beats"] = "not-a-list"
    with pytest.raises(ValueError, match="miss_beats"):
        validate_campaign(data)
    data["rooms"][0]["miss_beats"] = ["not-a-map"]
    with pytest.raises(ValueError, match="mapping"):
        validate_campaign(data)
    data["rooms"][0]["miss_beats"] = [{"pattern": "thorn"}]
    with pytest.raises(ValueError, match="pattern and message"):
        validate_campaign(data)
