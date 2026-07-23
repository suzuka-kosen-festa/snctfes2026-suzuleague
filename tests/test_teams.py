"""チーム構成の読み込みのテスト（ネットワーク不要）。

本番当日に「ファイルが読めない」で詰まると復旧の余地がないので、
エラーメッセージが原因を指すことまで確認する。
"""

from __future__ import annotations

import json

import pytest

from suzuleague.teams import ENV_TEAMS, default_teams, load_teams, resolve_teams


def write(tmp_path, data):
    p = tmp_path / "teams.json"
    p.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return p


class TestLoadTeams:
    def test_reads_name_and_members(self, tmp_path):
        p = write(tmp_path, [
            {"number": 1, "name": "チームA", "members": ["甲", "乙"]},
            {"number": 2, "name": "チームB", "members": []},
        ])
        teams = load_teams(p)
        assert [t.name for t in teams] == ["チームA", "チームB"]
        assert teams[0].members == ["甲", "乙"]

    def test_order_in_file_is_the_appearance_order(self, tmp_path):
        """企画側が「3組を1番目に」と指定してきても対応できる。"""
        p = write(tmp_path, [
            {"number": 3, "name": "先に登場"},
            {"number": 1, "name": "後から登場"},
        ])
        teams = load_teams(p)
        assert [t.name for t in teams] == ["先に登場", "後から登場"]
        assert [t.number for t in teams] == [3, 1]

    def test_number_defaults_to_position(self, tmp_path):
        p = write(tmp_path, [{"name": "A"}, {"name": "B"}])
        assert [t.number for t in load_teams(p)] == [1, 2]

    def test_missing_file_says_so(self, tmp_path):
        with pytest.raises(ValueError, match="見つかりません"):
            load_teams(tmp_path / "nope.json")

    def test_broken_json_says_so(self, tmp_path):
        p = tmp_path / "teams.json"
        p.write_text("{壊れている", encoding="utf-8")
        with pytest.raises(ValueError, match="JSON"):
            load_teams(p)

    def test_missing_name_says_which_entry(self, tmp_path):
        p = write(tmp_path, [{"name": "A"}, {"members": []}])
        with pytest.raises(ValueError, match="2番目"):
            load_teams(p)

    def test_duplicate_numbers_rejected(self, tmp_path):
        p = write(tmp_path, [{"number": 1, "name": "A"}, {"number": 1, "name": "B"}])
        with pytest.raises(ValueError, match="重複"):
            load_teams(p)

    def test_empty_list_rejected(self, tmp_path):
        p = write(tmp_path, [])
        with pytest.raises(ValueError, match="1件以上"):
            load_teams(p)


class TestResolveTeams:
    def test_defaults_when_nothing_given(self, monkeypatch):
        monkeypatch.delenv(ENV_TEAMS, raising=False)
        teams = resolve_teams()
        assert [t.name for t in teams] == ["チーム1", "チーム2", "チーム3", "チーム4"]

    def test_env_var_is_used(self, tmp_path, monkeypatch):
        p = write(tmp_path, [{"name": "環境変数から"}])
        monkeypatch.setenv(ENV_TEAMS, str(p))
        assert resolve_teams()[0].name == "環境変数から"

    def test_cli_wins_over_env(self, tmp_path, monkeypatch):
        env_file = write(tmp_path, [{"name": "env"}])
        cli_file = tmp_path / "cli.json"
        cli_file.write_text(json.dumps([{"name": "cli"}], ensure_ascii=False), encoding="utf-8")
        monkeypatch.setenv(ENV_TEAMS, str(env_file))
        assert resolve_teams(str(cli_file))[0].name == "cli"


class TestDefaultTeams:
    def test_four_teams(self):
        assert len(default_teams()) == 4

    def test_balloons_are_set_by_engine_not_here(self):
        # Team のデフォルト値をそのまま使う。持ち点の初期化は GameEngine の仕事
        assert all(t.balloons == 100 for t in default_teams())
