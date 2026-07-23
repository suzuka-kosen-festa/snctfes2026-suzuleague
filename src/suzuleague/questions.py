"""問題セット管理（コード内管理）。

本番の問題は企画側が実施したアンケート2種の集計結果から作成している
（アンケート1: 485件 / アンケート2: 423件、いずれも2026-06-26実施）。

問題文はcloud変数（数値のみ）で送れないため、ScratchへはIDのみ送信する
「ID参照方式」を採用。Scratch側には表示用テキストのリストを持ってもらい、
その貼り付け用テキストを export_scratch_list() で生成できる。
"""

from __future__ import annotations

from .models import Question

ROUNDS_PER_TEAM = 5
TEAM_COUNT = 4

SURVEY_1 = "鈴鹿高専生485人アンケート"
SURVEY_2 = "鈴鹿高専生423人アンケート"

# 本番問題。IDは通し番号で、チームtのラウンドr(1始まり)の問題ID = (t-1)*5 + r
#
# 各チームが同じ難易度構成になるよう、正解値の分布を揃えてある:
#   1問目=85%以上 / 2問目=30%以下 / 3問目=60-70% / 4問目=35-40% / 5問目=50%前後
# 序盤は予想しやすい極端な値、終盤は差が出にくい中間値という並び。
#
# 正解値は集計結果の四捨五入。差し替えるときは docs/development.md の
# 「リリースチェックリスト」に従い、Scratch側のリストも必ず同時に更新すること。
PRODUCTION_QUESTIONS: list[Question] = [
    # チーム1
    Question(1, "三重県に住んでいる人の割合は？", 93, SURVEY_1),
    Question(2, "テスト期間中に3本以上エナジードリンクを飲む人の割合は？", 19, SURVEY_2),
    Question(3, "告白したこと、またはされたことがある人の割合は？", 68, SURVEY_1),
    Question(4, "BeRealをダウンロードしている人の割合は？", 37, SURVEY_2),
    Question(5, "月子チェックに行ったことがある人の割合は？", 49, SURVEY_2),
    # チーム2
    Question(6, "部活動・同好会に入っている人の割合は？", 93, SURVEY_1),
    Question(7, "身長が175cm以上ある人の割合は？", 18, SURVEY_2),
    Question(8, "高専で1度でも赤点を取ったことがある人の割合は？", 70, SURVEY_1),
    Question(9, "通学に1時間以上かかる人の割合は？", 40, SURVEY_2),
    Question(10, "3DSで妖怪ウォッチシリーズをプレイしたことがある人の割合は？", 54, SURVEY_2),
    # チーム3
    Question(11, "鈴鹿高専に第1志望で入学した人の割合は？", 92, SURVEY_1),
    Question(12, "Nintendo Switch2を買った人の割合は？", 24, SURVEY_2),
    Question(13, "中学のテストでランキング10位以内に入ったことがある人の割合は？", 70, SURVEY_2),
    Question(14, "中学時代に得意だった教科が数学だった人の割合は？", 39, SURVEY_2),
    Question(15, "アルバイトをしたことがある人の割合は？", 55, SURVEY_1),
    # チーム4
    Question(16, "ゲームをするのが好きな人の割合は？", 87, SURVEY_2),
    Question(17, "将来自分の子供にも高専に入学してほしい人の割合は？", 31, SURVEY_2),
    Question(18, "過去と未来なら、過去に行きたい人の割合は？", 64, SURVEY_2),
    Question(19, "好きなポテトチップスの味がコンソメの人の割合は？", 38, SURVEY_1),
    Question(20, "自分のパソコンを持っている人の割合は？", 55, SURVEY_1),
]

# 予備。問題を差し替えたくなったときの候補（集計済み・そのまま使える）。
# ID は 101 以降にして本番の通し番号と衝突させない。
SPARE_QUESTIONS: list[Question] = [
    Question(101, "過去1ヶ月以内に紙のノートやルーズリーフで勉強した人の割合は？", 85, SURVEY_1),
    Question(102, "購買のクッキーシューを食べたことがある人の割合は？", 62, SURVEY_1),
    Question(103, "卒業後の進路に進学を希望している人の割合は？", 53, SURVEY_1),
    Question(104, "体操服の色を選べるなら青を選ぶ人の割合は？", 56, SURVEY_1),
    Question(105, "中学の内申点が41〜44だった人の割合は？", 52, SURVEY_1),
    Question(106, "テスト期間に日付を跨ぐ前に寝ている人の割合は？", 28, SURVEY_2),
    Question(107, "高専の定期テストで45点以下を取ったことがある人の割合は？", 43, SURVEY_2),
    Question(108, "SNSのサブスクリプションを1つ以上登録している人の割合は？", 63, SURVEY_2),
]

# 旧名の互換用エイリアス（プロトタイプ期のサンプル問題は本番データに差し替え済み）
SAMPLE_QUESTIONS = PRODUCTION_QUESTIONS


class QuestionSet:
    """チーム×ラウンドへの問題割り当てを管理する。"""

    def __init__(self, questions: list[Question] | None = None) -> None:
        self.questions = questions if questions is not None else PRODUCTION_QUESTIONS
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

    def export_audience_json(self) -> str:
        """観客用ページに埋め込む問題文のJSONを生成する。

        観客の画面は正解を先に知ってはいけないので、**問題文だけ**を渡す。
        正解は正解発表のタイミングで cloud 変数 P2S_CORRECT から届く。
        """
        import json

        table = {str(q.id): q.text for q in sorted(self.questions, key=lambda q: q.id)}
        return json.dumps(table, ensure_ascii=False, indent=2)


def main() -> None:
    """問題リストを外部向けの形式で書き出す。

    使い方:
      uv run python -m suzuleague.questions > questions.txt        # Scratch貼り付け用
      uv run python -m suzuleague.questions --audience-json        # 観客ページ用
    """
    import argparse

    parser = argparse.ArgumentParser(description="問題リストの書き出し")
    parser.add_argument(
        "--audience-json",
        action="store_true",
        help="観客用ページに埋め込むJSONを出力する（既定はScratch貼り付け用テキスト）",
    )
    args = parser.parse_args()

    qs = QuestionSet()
    if args.audience_json:
        print(qs.export_audience_json())
    else:
        print(qs.export_scratch_list(), end="")


if __name__ == "__main__":
    main()
