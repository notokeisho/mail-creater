"""
情報収集エージェント

返信メール用の送信先、元メール内容の収集機能を提供します。
"""

import re
import time
from typing import Dict, Any, Optional
from src.models.state import EmailState, update_state


class InformationCollectorAgent:
    """情報収集エージェント（返信専用・ターミナル対話型/LangGraphノード対応）"""

    def __init__(self, rate_limit_sec: float = 0.5):
        self.rate_limit_sec = rate_limit_sec

    def collect_recipient_info(self) -> Dict[str, Any]:
        """送信先情報を収集"""
        print("送信先情報を入力してください。")
        recipient = {}
        recipient["name"] = input("受信者氏名: ").strip()
        recipient["company"] = input("受信者会社名: ").strip()
        recipient["department"] = input("受信者部署名: ").strip()
        # 入力検証
        if not recipient["name"]:
            print("氏名は必須です。再入力してください。")
            return self.collect_recipient_info()
        return recipient

    def collect_original_content(self) -> str:
        """返信時の元メール内容を収集"""
        print("返信対象の元メール内容を貼り付けてください（空欄でスキップ）:")
        content = input("元メール内容: ").strip()
        return content

    def run(self, state: EmailState) -> EmailState:
        """情報収集エージェントのメイン処理（LangGraphノード互換）"""
        try:
            print("\n=== 情報収集エージェント ===")

            # 返信メールとして固定
            state = update_state(state, {"email_type": "reply"})
            time.sleep(self.rate_limit_sec)

            recipient_info = self.collect_recipient_info()
            state = update_state(state, {"recipient_info": recipient_info})
            time.sleep(self.rate_limit_sec)

            original_content = self.collect_original_content()
            state = update_state(state, {"original_content": original_content})
            time.sleep(self.rate_limit_sec)

            print("情報収集が完了しました。\n")
            return state
        except Exception as e:
            print(f"エラーが発生しました: {e}")
            state = update_state(state, {"error_message": str(e)})
            return state


# LangGraphノードとして利用する場合
# def information_collector_node(state: EmailState) -> EmailState:
#     agent = InformationCollectorAgent()
#     return agent.run(state)
