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

    def __call__(self, prompt=""):
        if self.index < len(self.responses):
            response = self.responses[self.index]
            self.index += 1
            return response
        return ""


@pytest.mark.parametrize(
    "recipient, original_content",
    [
        (
            ["受信者A", "A社", "営業部"],
            "これは元メールの内容です。",
        ),
        (
            ["受信者B", "B社", "企画部"],
            "別の元メール内容です。",
        ),
    ],
)
def test_information_collector(monkeypatch, recipient, original_content):
    # 入力シーケンスを作成
    responses = recipient + [original_content]
    dummy_input = DummyInput(responses)
    monkeypatch.setattr("builtins.input", dummy_input)

    agent = InformationCollectorAgent(rate_limit_sec=0)
    state = create_initial_state("test_session")
    new_state = agent.run(state)

    # 検証
    assert new_state["email_type"] == "reply"
    assert new_state["recipient_info"]["name"] == recipient[0]
    assert new_state["recipient_info"]["company"] == recipient[1]
    assert new_state["recipient_info"]["department"] == recipient[2]
    assert new_state["original_content"].startswith(original_content[:10])
    assert new_state["error_message"] is None


def test_information_collector_empty_input(monkeypatch):
    """空の入力のテスト"""
    responses = ["", "", "", ""]
    dummy_input = DummyInput(responses)
    monkeypatch.setattr("builtins.input", dummy_input)

    agent = InformationCollectorAgent(rate_limit_sec=0)
    state = create_initial_state("test_session")
    new_state = agent.run(state)

    # エラーメッセージが設定されていることを確認
    assert new_state["error_message"] is not None
