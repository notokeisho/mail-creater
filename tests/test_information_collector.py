"""
情報収集エージェントのテスト
"""

import pytest
from src.agents.information_collector import InformationCollectorAgent
from src.models.state import create_initial_state


class DummyInput:
    def __init__(self, responses):
        self.responses = responses
        self.index = 0

    def __call__(self, prompt=None):
        if self.index < len(self.responses):
            res = self.responses[self.index]
            self.index += 1
            return res
        return ""


@pytest.mark.parametrize(
    "email_type, recipient, is_reply, original_content",
    [
        ("1", ["受信者A", "a@example.com", "A社", "営業部"], False, ""),
        (
            "2",
            ["受信者B", "b@example.com", "B社", "企画部"],
            True,
            "これは元メールの内容です。",
        ),
    ],
)
def test_information_collector(
    monkeypatch, email_type, recipient, is_reply, original_content
):
    # 入力シーケンスを作成
    responses = [email_type] + recipient
    if is_reply:
        responses.append(original_content)
    dummy_input = DummyInput(responses)
    monkeypatch.setattr("builtins.input", dummy_input)

    agent = InformationCollectorAgent(rate_limit_sec=0)
    state = create_initial_state("test_session")
    new_state = agent.run(state)

    # 検証
    assert new_state["email_type"] == ("reply" if is_reply else "new")
    assert new_state["recipient_info"]["name"] == recipient[0]
    assert new_state["recipient_info"]["email"] == recipient[1]
    if is_reply:
        assert new_state["original_content"].startswith(original_content[:10])
    else:
        assert new_state["original_content"] == ""
    assert new_state["error_message"] is None
