"""
文章作成エージェント

返信メール用のRAG検索と最終メール文の生成機能を提供します。
"""

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from typing import Dict, Any
from src.models.state import EmailState, update_state
from src.utils.rag import PersonalInfoRAG
import time
import openai


class ContentCreatorAgent:
    """文章作成エージェント（返信専用・RAG検索・メール生成・LangGraphノード対応）"""

    prompt_template = """
あなたはビジネスメールのプロです。以下の情報をもとに、適切な日本語の返信メール本文を作成してください。

【入力情報】
{answers}
[署名]
{signature_info}

【元メール内容】
{original_content}

---
【元メール内容】の返答が【入力情報】です。これを目上の人に向けて敬語でメールを返します。
今から作成するのはメールの本文のみです。
## メール構成
- 「お世話になっております。」から始める。
- 署名{signature_info}より、自分の身分を名乗る。(例：〇〇大学 〇〇学部の〇〇です。)
- 【入力情報】の内容を元に、返信メールの内容を目上の人への敬語で作成する。
 -- answersの中身はpurposeとadditional_infoのような形式です。
 -- purposeは返信の目的です。まずこれについて返信してください。この後に改行を入れてください。
 -- additional_infoは追加の要望・質問です。これについては要望・質問であるので丁寧な口調で質問してください。この後に改行を入れてください。
- 最後に締めの言葉を入れる。（例：何卒よろしくお願い申し上げます。）

## 作成例(参考に)
- お世話になっております。\n
- 〇〇大学 〇〇学部の〇〇です。\n
- 【入力情報】の内容を元に、返信メールの内容を目上の人への敬語で作成する。\n
- 最後に締めの言葉を入れる。（例：何卒よろしくお願い申し上げます。）\n

## 注意事項
- 必ず本文のみを作成すること。
- 必ず敬語を使用すること。その上で丁寧な言葉で作成すること。
- 目上の人に対してメールするため、失礼な言葉は使わないこと。
- 学生の立場で企業の方々に対してメールしているため、どうすれば良いかをしっかり聞く。
- おすすめや提案などの行為はしない。
- 「安心してください。」という言葉は使わない。
- 簡潔に述べる。

- 必ず締めの言葉を入れること。
- 必ず【入力情報】の内容を元に、返信メールの内容を丁寧な言葉で作成すること。
"""

    def __init__(self, rate_limit_sec: float = 0.5):
        self.rate_limit_sec = rate_limit_sec
        self.rag = PersonalInfoRAG()
        self.openai_client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    def retrieve_personal_info(self, state: EmailState) -> Dict[str, Any]:
        """RAGで個人情報を取得（全件取得）"""
        return self.rag.get_all_personal_info()

    def call_llm(self, prompt: str) -> str:
        response = self.openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()

    def generate_email_content(
        self, state: EmailState, personal_info: Dict[str, Any]
    ) -> Dict[str, str]:
        """収集情報に基づき返信メール文を生成"""
        recipient = state.get("recipient_info", {})
        answers = state.get("collected_answers", {})
        original_content = state.get("original_content", "")

        # 宛名
        if recipient.get("company"):
            addressee = f"{recipient['company']}\n{recipient.get('department', '')} {recipient['name']} 様"
        else:
            addressee = f"{recipient.get('name', '')} 様"

        # RAG署名情報
        signature_info = "\n".join(
            [
                f"大学名: {personal_info.get('university_name', '')}",
                f"学部・学科名: {personal_info.get('department', '')}",
                f"名前: {personal_info.get('name', '')}",
                f"メール: {personal_info.get('email', '')}",
                f"電話: {personal_info.get('phone', '')}",
                f"住所: {personal_info.get('address', '')}",
            ]
        )

        # プロンプト生成
        prompt = self.prompt_template.format(
            answers="\n".join([f"{k}: {v}" for k, v in answers.items()]),
            signature_info=signature_info,
            original_content=original_content,
        )
        # LLMで本文生成
        body = self.call_llm(prompt)

        # 本文全体
        body_lines = [addressee, "", body, ""]
        # 署名
        body_lines.append("――――――――――――――――――――")
        body_lines.append(f"{personal_info.get('university_name', '')}")
        body_lines.append(f"{personal_info.get('department', '')}")
        body_lines.append(f"{personal_info.get('name', '')}")
        body_lines.append(f"Email: {personal_info.get('email', '')}")
        body_lines.append(f"TEL: {personal_info.get('phone', '')}")
        body_lines.append(f"住所: {personal_info.get('address', '')}")
        body_lines.append("――――――――――――――――――――")

        return {"body": "\n".join(body_lines).strip()}

    def format_email(self, state: EmailState, content: Dict[str, str]) -> str:
        """メール文を美しく整形（返信専用）"""
        # 返信専用なので件名と宛先は不要、本文のみを返す
        return content["body"]

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
