"""
質問エージェント

返信メール内容に関する質問生成と回答収集機能を提供します。
"""

from typing import List, Dict, Any
from src.models.state import EmailState, update_state
import time


class QuestionerAgent:
    """質問エージェント（返信専用・ターミナル対話型/LangGraphノード対応）"""

    def __init__(self, rate_limit_sec: float = 0.5):
        self.rate_limit_sec = rate_limit_sec

    def generate_questions(self, state: EmailState) -> List[Dict[str, Any]]:
        """返信メール用の質問リストを生成"""
        questions = []

        # 返信メール専用の質問
        questions.append(
            {
                "key": "purpose",
                "text": "この返信メールの目的は何ですか？",
                "required": True,
            }
        )
        questions.append(
            {
                "key": "additional_info",
                "text": "その他、伝えたいことや要望があればご記入ください（任意）",
                "required": False,
            }
        )

        return questions

    def collect_answers(self, questions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """質問に対する回答を収集"""
        answers = {}
        for question in questions:
            while True:
                print(f"{question['text']}")
                answer = input(f"{question['key']}: ").strip()

                if question["required"] and not answer:
                    print("この質問は必須です。入力してください。")
                    continue

                answers[question["key"]] = answer
                break
            time.sleep(self.rate_limit_sec)
        return answers

    def run(self, state: EmailState) -> EmailState:
        """質問エージェントのメイン処理（LangGraphノード互換）"""
        try:
            print("\n=== 質問エージェント ===")

            # 質問の生成
            questions = self.generate_questions(state)

            # 回答の収集
            answers = self.collect_answers(questions)

            # Stateの更新
            state = update_state(state, {"collected_answers": answers})

            print("質問への回答が完了しました。\n")
            print(answers)
            return state

        except Exception as e:
            print(f"エラーが発生しました: {e}")
            state = update_state(state, {"error_message": str(e)})
            return state


# LangGraphノードとして利用する場合
# def questioner_node(state: EmailState) -> EmailState:
#     agent = QuestionerAgent()
#     return agent.run(state)
