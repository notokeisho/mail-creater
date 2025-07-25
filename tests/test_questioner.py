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

    def __call__(self, prompt=""):
        if self.index < len(self.responses):
            response = self.responses[self.index]
            self.index += 1
            return response
        return ""


@pytest.mark.parametrize(
    "answers, expected_keys",
    [
        (
            ["資料送付", "至急返信希望"],
            ["purpose", "additional_info"],
        ),
        (
            ["確認事項", ""],
            ["purpose", "additional_info"],
        ),
    ],
)
def test_questioner(monkeypatch, answers, expected_keys):
    # Stateを準備
    state = create_initial_state("test_session")
    state = update_state(state, {"email_type": "reply"})
    dummy_input = DummyInput(answers)
    monkeypatch.setattr("builtins.input", dummy_input)

    agent = QuestionerAgent(rate_limit_sec=0)
    new_state = agent.run(state)

    # 検証
    for k, v in zip(expected_keys, answers):
        assert new_state["collected_answers"][k] == v
    assert new_state["error_message"] is None


def test_questioner_empty_required_field(monkeypatch):
    """必須フィールドが空の場合のテスト"""
    responses = ["", "資料送付", "至急返信希望"]  # 最初の必須フィールドを空にする
    dummy_input = DummyInput(responses)
    monkeypatch.setattr("builtins.input", dummy_input)

    agent = QuestionerAgent(rate_limit_sec=0)
    state = create_initial_state("test_session")
    state = update_state(state, {"email_type": "reply"})
    new_state = agent.run(state)

    # 空の回答でもエラーにならない（再入力を促すだけ）
    assert new_state["error_message"] is None
    assert "purpose" in new_state["collected_answers"]
    assert new_state["collected_answers"]["purpose"] == "資料送付"


def test_questioner_generate_questions():
    """質問生成のテスト"""
    agent = QuestionerAgent()
    state = create_initial_state("test_session")
    state = update_state(state, {"email_type": "reply"})

    questions = agent.generate_questions(state)

    # 返信専用の質問が生成されることを確認
    assert len(questions) == 2
    assert questions[0]["key"] == "purpose"
    assert questions[1]["key"] == "additional_info"

    # 必須フィールドの確認
    assert questions[0]["required"] == True
    assert questions[1]["required"] == False
