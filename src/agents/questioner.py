"""
質問エージェント

メール内容に関する質問生成と回答収集機能を提供します。
"""

from typing import List, Dict, Any
from src.models.state import EmailState, update_state
import time


class QuestionerAgent:
    """質問エージェント（ターミナル対話型/LangGraphノード対応）"""

    def __init__(self, rate_limit_sec: float = 0.5):
        self.rate_limit_sec = rate_limit_sec

    def generate_questions(self, state: EmailState) -> List[Dict[str, Any]]:
        """状況に応じた質問リストを生成"""
        questions = []
        # メール種別による分岐
        if state.get("email_type") == "new":
            questions.append(
                {
                    "key": "purpose",
                    "text": "このメールの送信目的は何ですか？（例：アポイント調整、資料送付など）",
                    "required": True,
                }
            )
            questions.append(
                {
                    "key": "tone",
                    "text": "メールの文体（丁寧・カジュアルなど）を指定してください。",
                    "required": False,
                }
            )
        elif state.get("email_type") == "reply":
            questions.append(
                {
                    "key": "summary_check",
                    "text": "元メールの要約内容で間違いありませんか？（はい/いいえ）",
                    "required": True,
                }
            )
            questions.append(
                {
                    "key": "purpose",
                    "text": "この返信メールの目的は何ですか？",
                    "required": True,
                }
            )
        # 共通質問
        questions.append(
            {
                "key": "additional_info",
                "text": "その他、伝えたいことや要望があればご記入ください（任意）",
                "required": False,
            }
        )
        return questions

    def collect_answers(self, questions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """質問ごとにユーザーから回答を収集"""
        answers = {}
        for q in questions:
            while True:
                print(q["text"])
                ans = input(f"{q['key']}: ").strip()
                if q["required"] and not ans:
                    print("この質問は必須です。入力してください。")
                    time.sleep(self.rate_limit_sec)
                    continue
                answers[q["key"]] = ans
                break
            time.sleep(self.rate_limit_sec)
        return answers

    def run(self, state: EmailState) -> EmailState:
        """質問エージェントのメイン処理（LangGraphノード互換）"""
        try:
            print("\n=== 質問エージェント ===")
            questions = self.generate_questions(state)
            answers = self.collect_answers(questions)
            # Stateに回答をマージ
            prev = state.get("collected_answers", {})
            merged = {**prev, **answers}
            state = update_state(state, {"collected_answers": merged})
            print("質問への回答が完了しました。\n")
            return state
        except Exception as e:
            print(f"エラーが発生しました: {e}")
            state = update_state(state, {"error_message": str(e)})
            return state


# LangGraphノードとして利用する場合
# def questioner_node(state: EmailState) -> EmailState:
#     agent = QuestionerAgent()
#     return agent.run(state)
