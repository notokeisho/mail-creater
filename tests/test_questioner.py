"""
質問エージェントのテスト
"""

import pytest
from src.agents.questioner import QuestionerAgent
from src.models.state import create_initial_state, update_state


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
    "email_type, answers, expected_keys",
    [
        (
            "new",
            ["商談調整", "丁寧", "特になし"],
            ["purpose", "tone", "additional_info"],
        ),
        (
            "reply",
            ["はい", "資料送付", "至急返信希望"],
            ["summary_check", "purpose", "additional_info"],
        ),
    ],
)
def test_questioner(monkeypatch, email_type, answers, expected_keys):
    # Stateを準備
    state = create_initial_state("test_session")
    state = update_state(state, {"email_type": email_type})
    dummy_input = DummyInput(answers)
    monkeypatch.setattr("builtins.input", dummy_input)

    agent = QuestionerAgent(rate_limit_sec=0)
    new_state = agent.run(state)

    # 検証
    for k, v in zip(expected_keys, answers):
        assert new_state["collected_answers"][k] == v
    assert new_state["error_message"] is None
