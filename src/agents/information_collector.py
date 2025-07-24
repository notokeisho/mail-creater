"""
情報収集エージェント

メール種類、送信先、元メール内容の収集機能を提供します。
"""

import re
import time
from typing import Dict, Any, Optional
from src.models.state import EmailState, update_state


class InformationCollectorAgent:
    """情報収集エージェント（ターミナル対話型/LangGraphノード対応）"""

    def __init__(self, rate_limit_sec: float = 0.5):
        self.rate_limit_sec = rate_limit_sec

    def collect_email_type(self) -> str:
        """新規送信か返信かを選択"""
        while True:
            print("メールの種類を選択してください: (1) 新規送信 (2) 返信")
            choice = input("番号を入力してください（1または2）: ").strip()
            if choice == "1":
                return "new"
            elif choice == "2":
                return "reply"
            else:
                print("無効な入力です。1または2を入力してください。")
            time.sleep(self.rate_limit_sec)

    def collect_recipient_info(self) -> Dict[str, Any]:
        """送信先情報を収集"""
        print("送信先情報を入力してください。")
        recipient = {}
        recipient["name"] = input("受信者氏名: ").strip()
        recipient["email"] = input("受信者メールアドレス: ").strip()
        recipient["company"] = input("受信者会社名: ").strip()
        recipient["department"] = input("受信者部署名: ").strip()
        # 入力検証
        if not recipient["name"] or not recipient["email"]:
            print("氏名とメールアドレスは必須です。再入力してください。")
            return self.collect_recipient_info()
        if not self._validate_email(recipient["email"]):
            print("メールアドレスの形式が正しくありません。再入力してください。")
            return self.collect_recipient_info()
        return recipient

    def summarize_original_content(self) -> str:
        """返信時の元メール内容を要約（簡易）"""
        print("返信対象の元メール内容を貼り付けてください（空欄でスキップ）:")
        content = input("元メール内容: ").strip()
        if not content:
            return ""
        # 簡易要約（最初の100文字＋...）
        summary = content[:100]
        if len(content) > 100:
            summary += "..."
        print(f"要約: {summary}")
        return summary

    def _validate_email(self, email: str) -> bool:
        return re.match(r"^[\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,}$", email) is not None

    def run(self, state: EmailState) -> EmailState:
        """情報収集エージェントのメイン処理（LangGraphノード互換）"""
        try:
            print("\n=== 情報収集エージェント ===")
            email_type = self.collect_email_type()
            state = update_state(state, {"email_type": email_type})
            time.sleep(self.rate_limit_sec)

            recipient_info = self.collect_recipient_info()
            state = update_state(state, {"recipient_info": recipient_info})
            time.sleep(self.rate_limit_sec)

            original_content = ""
            if email_type == "reply":
                original_content = self.summarize_original_content()
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
