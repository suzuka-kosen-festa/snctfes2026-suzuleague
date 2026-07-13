"""プロトコルのエンコード/デコードのテスト。"""

import pytest

from suzuleague import protocol
from suzuleague.engine import Snapshot, State


class TestEncodeSnapshot:
    def test_encode_all_fields(self):
        snap = Snapshot(
            state=State.REVEAL,
            team_no=2,
            round_no=3,
            question_id=8,
            correct=67,
            balloons=54,
        )
        encoded = protocol.encode_snapshot(snap, seq=12)
        assert encoded == {
            "P2S_STATE": 4,
            "P2S_TEAM": 2,
            "P2S_ROUND": 3,
            "P2S_QID": 8,
            "P2S_CORRECT": 67,
            "P2S_BALLOONS": 54,
            "P2S_SEQ": 12,
        }

    def test_seq_is_last_key(self):
        """SEQは他の変数の後に送信される必要がある（Scratch側の検知順序）。"""
        snap = Snapshot(State.IDLE, 0, 0, 0, -1, 0)
        keys = list(protocol.encode_snapshot(snap, seq=1))
        assert keys[-1] == protocol.VAR_P2S_SEQ

    def test_values_are_all_int(self):
        """TurboWarp cloudは数値のみのため、全て整数で送る。"""
        snap = Snapshot(State.ANSWERING, 1, 1, 1, -1, 100)
        for value in protocol.encode_snapshot(snap, seq=1).values():
            assert isinstance(value, int)


class TestParsePercent:
    @pytest.mark.parametrize(
        ("raw", "expected"),
        [
            ("45", 45),
            (45, 45),
            ("45.0", 45),  # cloudからは小数表記で届くことがある
            ("0", 0),
            ("100", 100),
        ],
    )
    def test_valid_values(self, raw, expected):
        assert protocol.parse_percent(raw) == expected

    @pytest.mark.parametrize("raw", ["101", "-1", "45.5", "abc", "", None, "1e10"])
    def test_invalid_values(self, raw):
        with pytest.raises(protocol.ProtocolError):
            protocol.parse_percent(raw)
