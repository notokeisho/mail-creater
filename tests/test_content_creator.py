"""
文章作成エージェントのテスト
"""

import pytest
from src.agents.content_creator import ContentCreatorAgent
from src.models.state import create_initial_state, update_state
from src.utils.personal_info_manager import PersonalInfoManager


@pytest.mark.parametrize(
    "recipient, answers, original_content",
    [
        (
            {
                "name": "受信者A",
                "company": "A社",
                "department": "営業部",
            },
            {"purpose": "資料送付", "additional_info": "至急返信希望"},
            "これは元メールの内容です。",
        ),
        (
            {
                "name": "受信者B",
                "company": "B社",
                "department": "企画部",
            },
            {"purpose": "確認事項", "additional_info": ""},
            "別の元メール内容です。",
        ),
    ],
)
def test_content_creator(monkeypatch, recipient, answers, original_content):
    # Stateを準備
    state = create_initial_state("test_session")
    state = update_state(
        state,
        {
            "email_type": "reply",
            "recipient_info": recipient,
            "collected_answers": answers,
            "original_content": original_content,
        },
    )

    # 標準出力を抑制
    monkeypatch.setattr("builtins.print", lambda *a, **k: None)

    agent = ContentCreatorAgent(rate_limit_sec=0)
    new_state = agent.run(state)

    # 検証
    assert "final_email" in new_state
    email = new_state["final_email"]
    assert recipient["name"] in email
    assert answers["purpose"] in email
    assert "Re:" not in email  # 件名が削除されたのでRe:は含まれない
    assert original_content in email  # 元メール内容全体が含まれる
    assert new_state["error_message"] is None


def test_content_creator_empty_original_content(monkeypatch):
    """元メール内容が空の場合のテスト"""
    state = create_initial_state("test_session")
    state = update_state(
        state,
        {
            "email_type": "reply",
            "recipient_info": {
                "name": "受信者",
                "company": "テスト社",
                "department": "テスト部",
            },
            "collected_answers": {"purpose": "確認事項"},
            "original_content": "",
        },
    )

    # 標準出力を抑制
    monkeypatch.setattr("builtins.print", lambda *a, **k: None)

    agent = ContentCreatorAgent(rate_limit_sec=0)
    new_state = agent.run(state)

    # 検証
    assert "final_email" in new_state
    email = new_state["final_email"]
    assert "Re: ご連絡" not in email  # 件名が削除されたので含まれない
    assert new_state["error_message"] is None


def test_content_creator_retrieve_personal_info():
    """個人情報取得のテスト"""
    agent = ContentCreatorAgent()
    state = create_initial_state("test_session")

    personal_info = agent.retrieve_personal_info(state)

    # 個人情報が取得できることを確認
    assert isinstance(personal_info, dict)
    assert "company_name" in personal_info
    assert "name" in personal_info
    assert "email" in personal_info


def test_content_creator_generate_email_content():
    """メール文生成のテスト"""
    agent = ContentCreatorAgent()
    state = create_initial_state("test_session")
    state = update_state(
        state,
        {
            "email_type": "reply",
            "recipient_info": {
                "name": "受信者",
                "company": "テスト社",
                "department": "テスト部",
            },
            "collected_answers": {"purpose": "確認事項"},
            "original_content": "元メール内容",
        },
    )

    personal_info = {
        "company_name": "株式会社サンプル",
        "department": "営業部",
        "name": "田中太郎",
        "email": "tanaka@example.com",
        "phone": "03-1234-5678",
        "address": "東京都渋谷区",
    }

    content = agent.generate_email_content(state, personal_info)

    # 件名と本文が生成されることを確認
    assert "subject" in content
    assert "body" in content
    assert "Re:" in content["subject"]
    assert "受信者" in content["body"]
    assert "確認事項" in content["body"]
    assert "元メール内容" in content["body"]  # 元メール内容全体が含まれる
