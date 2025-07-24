"""
文章作成エージェントのテスト
"""

import pytest
from src.agents.content_creator import ContentCreatorAgent
from src.models.state import create_initial_state, update_state
from src.utils.personal_info_manager import PersonalInfoManager


@pytest.mark.parametrize(
    "email_type, recipient, answers, original_content",
    [
        (
            "new",
            {
                "name": "受信者A",
                "email": "a@example.com",
                "company": "A社",
                "department": "営業部",
            },
            {"purpose": "商談調整", "additional_info": "特になし"},
            "",
        ),
        (
            "reply",
            {
                "name": "受信者B",
                "email": "b@example.com",
                "company": "B社",
                "department": "企画部",
            },
            {"purpose": "資料送付", "additional_info": "至急返信希望"},
            "これは元メールの内容です。",
        ),
    ],
)
def test_content_creator(monkeypatch, email_type, recipient, answers, original_content):
    # Stateを準備
    state = create_initial_state("test_session")
    state = update_state(
        state,
        {
            "email_type": email_type,
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
    assert recipient["email"] in email
    assert answers["purpose"] in email
    if email_type == "reply":
        assert "Re:" in email or "返信" in email
        assert original_content[:10] in email
    assert new_state["error_message"] is None
