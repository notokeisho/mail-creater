"""
文章作成エージェント

RAG検索と最終メール文の生成機能を提供します。
"""

from typing import Dict, Any
from src.models.state import EmailState, update_state
from src.utils.rag import PersonalInfoRAG
import time


class ContentCreatorAgent:
    """文章作成エージェント（RAG検索・メール生成・LangGraphノード対応）"""

    def __init__(self, rate_limit_sec: float = 0.5):
        self.rate_limit_sec = rate_limit_sec
        self.rag = PersonalInfoRAG()

    def retrieve_personal_info(self, state: EmailState) -> Dict[str, Any]:
        """RAGで個人情報を取得（全件取得）"""
        return self.rag.get_all_personal_info()

    def generate_email_content(
        self, state: EmailState, personal_info: Dict[str, Any]
    ) -> Dict[str, str]:
        """収集情報に基づきメール文を生成"""
        recipient = state.get("recipient_info", {})
        answers = state.get("collected_answers", {})
        email_type = state.get("email_type", "new")
        original_content = state.get("original_content", "")

        # 件名生成
        if email_type == "reply":
            subject = f"Re: {original_content[:20]}"
        else:
            subject = f"{answers.get('purpose', 'ご連絡')}"
        # 本文生成
        body_lines = []
        if recipient.get("company"):
            body_lines.append(
                f"{recipient['company']} {recipient.get('department', '')} {recipient['name']} 様"
            )
        else:
            body_lines.append(f"{recipient.get('name', '')} 様")
        body_lines.append("")
        if email_type == "reply" and original_content:
            body_lines.append(
                f"> {original_content[:100]}{'...' if len(original_content)>100 else ''}"
            )
            body_lines.append("")
        # 本文メイン
        if answers.get("purpose"):
            body_lines.append(f"この度は{answers['purpose']}の件でご連絡いたしました。")
        if answers.get("additional_info"):
            body_lines.append(f"【ご要望・補足】{answers['additional_info']}")
        body_lines.append("")
        body_lines.append("ご確認のほど、よろしくお願いいたします。")
        body_lines.append("")
        # 署名
        body_lines.append("――――――――――――――――――――")
        body_lines.append(f"{personal_info.get('company_name', '')}")
        body_lines.append(f"{personal_info.get('department', '')}")
        body_lines.append(f"{personal_info.get('name', '')}")
        body_lines.append(f"Email: {personal_info.get('email', '')}")
        body_lines.append(f"TEL: {personal_info.get('phone', '')}")
        body_lines.append(f"住所: {personal_info.get('address', '')}")
        body_lines.append("――――――――――――――――――――")

        return {"subject": subject.strip(), "body": "\n".join(body_lines).strip()}

    def format_email(self, state: EmailState, content: Dict[str, str]) -> str:
        """メール文を美しく整形"""
        recipient = state.get("recipient_info", {})
        lines = [
            f"件名: {content['subject']}",
            f"宛先: {recipient.get('email', '')} ({recipient.get('name', '')})",
            "",
            content["body"],
        ]
        return "\n".join(lines)

    def run(self, state: EmailState) -> EmailState:
        """文章作成エージェントのメイン処理（LangGraphノード互換）"""
        try:
            print("\n=== 文章作成エージェント ===")
            personal_info = self.retrieve_personal_info(state)
            time.sleep(self.rate_limit_sec)
            content = self.generate_email_content(state, personal_info)
            time.sleep(self.rate_limit_sec)
            formatted = self.format_email(state, content)
            print("\n--- 生成されたメール文 ---\n")
            print(formatted)
            print("\n------------------------\n")
            state = update_state(state, {"final_email": formatted})
            return state
        except Exception as e:
            print(f"エラーが発生しました: {e}")
            state = update_state(state, {"error_message": str(e)})
            return state


# LangGraphノードとして利用する場合
# def content_creator_node(state: EmailState) -> EmailState:
#     agent = ContentCreatorAgent()
#     return agent.run(state)
