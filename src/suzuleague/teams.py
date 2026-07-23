"""チーム構成の読み込み。

本番のチーム名・メンバー・登場順は企画側から受け取る。
**メンバーの氏名は個人情報**なので、リポジトリには含めず
JSONファイルを外から渡す形にしている（`teams.json` は .gitignore 済み）。

    uv run suzuleague --teams teams.json

書式は teams.example.json を参照。ファイルを渡さなければ
「チーム1」〜「チーム4」の既定値で動く。
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from .models import Team

ENV_TEAMS = "SUZULEAGUE_TEAMS"
DEFAULT_TEAM_COUNT = 4


def default_teams(count: int = DEFAULT_TEAM_COUNT) -> list[Team]:
    """名前が決まっていないときの既定チーム。"""
    return [Team(number=i, name=f"チーム{i}") for i in range(1, count + 1)]


def load_teams(path: str | os.PathLike[str]) -> list[Team]:
    """チーム構成のJSONを読み込む。

    登場順はファイルに書かれた順。`number` は表示・プロトコル用の
    チーム番号で、登場順とは独立に指定できる（企画側が
    「3組が1番目に登場」のような並びを指定してきても対応できる）。
    """
    p = Path(path)
    try:
        raw = json.loads(p.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise ValueError(f"チーム構成ファイルが見つかりません: {p}") from None
    except json.JSONDecodeError as e:
        raise ValueError(f"チーム構成ファイルのJSONが壊れています: {p} ({e})") from None

    if not isinstance(raw, list) or not raw:
        raise ValueError("チーム構成は1件以上の配列である必要があります")

    teams: list[Team] = []
    for i, item in enumerate(raw, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"{i}番目の要素がオブジェクトではありません")
        name = str(item.get("name") or "").strip()
        if not name:
            raise ValueError(f"{i}番目のチームに name がありません")
        number = item.get("number", i)
        try:
            number = int(number)
        except (TypeError, ValueError):
            raise ValueError(f"{name} の number が数値ではありません: {number!r}") from None
        members = item.get("members") or []
        if not isinstance(members, list):
            raise ValueError(f"{name} の members が配列ではありません")
        teams.append(
            Team(number=number, name=name, members=[str(m) for m in members])
        )

    numbers = [t.number for t in teams]
    if len(set(numbers)) != len(numbers):
        raise ValueError(f"チーム番号が重複しています: {numbers}")
    return teams


def resolve_teams(cli_path: str | None = None) -> list[Team]:
    """チーム構成を CLI引数 > 環境変数 > 既定値 の順で決める。"""
    path = cli_path or os.environ.get(ENV_TEAMS)
    return load_teams(path) if path else default_teams()
