"""問題セット管理（コード内管理）。

本番の問題はアンケート集計スプレッドシートから作成予定。
現時点ではプロトタイプ用のサンプル問題を置いている。

問題文はcloud変数（数値のみ）で送れないため、ScratchへはIDのみ送信する
「ID参照方式」を採用。Scratch側には表示用テキストのリストを持ってもらい、
その貼り付け用テキストを export_scratch_list() で生成できる。
"""

from __future__ import annotations

from .models import Question

ROUNDS_PER_TEAM = 5
TEAM_COUNT = 4

# サンプル問題（本番はアンケート結果から差し替える）
# IDは 通し番号。チームtのラウンドr(1始まり)の問題ID = (t-1)*5 + r
SAMPLE_QUESTIONS: list[Question] = [
    # チーム1
    Question(1, "朝ごはんを毎日食べる人の割合は？", 62, "サンプル"),
    Question(2, "犬派の人の割合は？", 48, "サンプル"),
    Question(3, "夏休みの宿題を最終日にやる人の割合は？", 35, "サンプル"),
    Question(4, "きのこの山派の人の割合は？", 55, "サンプル"),
    Question(5, "朝型人間の割合は？", 28, "サンプル"),
    # チーム2
    Question(6, "通学に電車を使う人の割合は？", 44, "サンプル"),
    Question(7, "カレーは甘口派の人の割合は？", 22, "サンプル"),
    Question(8, "スマホの充電が50%を切ると不安な人の割合は？", 67, "サンプル"),
    Question(9, "部活動に入っている人の割合は？", 71, "サンプル"),
    Question(10, "テスト前日に徹夜したことがある人の割合は？", 39, "サンプル"),
    # チーム3
    Question(11, "目玉焼きには醤油派の人の割合は？", 52, "サンプル"),
    Question(12, "自分の学科が好きな人の割合は？", 80, "サンプル"),
    Question(13, "お風呂は夜に入る人の割合は？", 85, "サンプル"),
    Question(14, "遅刻したことがある人の割合は？", 58, "サンプル"),
    Question(15, "ゲームを週3日以上する人の割合は？", 63, "サンプル"),
    # チーム4
    Question(16, "たけのこの里派の人の割合は？", 45, "サンプル"),
    Question(17, "寮生活をしている人の割合は？", 30, "サンプル"),
    Question(18, "プログラミングが得意だと思う人の割合は？", 41, "サンプル"),
    Question(19, "高専祭を楽しみにしている人の割合は？", 77, "サンプル"),
    Question(20, "将来も三重県に住みたい人の割合は？", 33, "サンプル"),
]


class QuestionSet:
    """チーム×ラウンドへの問題割り当てを管理する。"""

    def __init__(self, questions: list[Question] | None = None) -> None:
        self.questions = questions if questions is not None else SAMPLE_QUESTIONS
        need = TEAM_COUNT * ROUNDS_PER_TEAM
        if len(self.questions) < need:
            raise ValueError(f"問題数が不足: {len(self.questions)} < {need}")
        self._by_id = {q.id: q for q in self.questions}
        if len(self._by_id) != len(self.questions):
            raise ValueError("問題IDが重複しています")

    def by_id(self, question_id: int) -> Question:
        return self._by_id[question_id]

    def for_team(self, team_no: int) -> list[Question]:
        """チーム番号(1始まり)に割り当てられた5問を返す。"""
        if not 1 <= team_no <= TEAM_COUNT:
            raise ValueError(f"チーム番号は1-{TEAM_COUNT}: {team_no}")
        start = (team_no - 1) * ROUNDS_PER_TEAM
        return self.questions[start : start + ROUNDS_PER_TEAM]

    def export_scratch_list(self) -> str:
        """Scratchのリストに貼り付けるためのテキストを生成する。

        行番号 = 問題ID になるようにID順で1行1問。
        Scratchエディタでリストを右クリック→「読み込み」で取り込める。
        """
        lines = []
        for i in range(1, max(self._by_id) + 1):
            q = self._by_id.get(i)
            lines.append(q.text if q else "")
        return "\n".join(lines) + "\n"


def main() -> None:
    """問題リストのScratch貼り付け用テキストを標準出力に出す。

    使い方: uv run python -m suzuleague.questions > questions.txt
    """
    print(QuestionSet().export_scratch_list(), end="")


if __name__ == "__main__":
    main()
