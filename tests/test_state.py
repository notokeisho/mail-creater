"""
Stateクラスのテスト
"""

import pytest
from datetime import datetime
from src.models.state import (
    EmailState,
    create_initial_state,
    update_state,
    validate_state,
    get_state_summary,
)
from src.utils.state_manager import StateManager


class TestEmailState:
    """EmailStateクラスのテスト"""

    def test_create_initial_state(self):
        """初期状態の作成テスト"""
        state = create_initial_state("test_session")

        assert state["session_id"] == "test_session"
        assert state["current_step"] == "information_collection"
        assert state["collected_answers"] == {}
        assert state["retry_count"] == 0
        assert state["email_type"] is None
        assert state["recipient_info"] is None
        assert state["personal_info"] is None
        assert state["error_message"] is None
        assert "created_at" in state
        assert "updated_at" in state

    def test_update_state(self):
        """状態更新のテスト"""
        initial_state = create_initial_state("test_session")

        updates = {
            "email_type": "new",
            "current_step": "questioning",
            "collected_answers": {"question1": "answer1"},
        }

        updated_state = update_state(initial_state, updates)

        assert updated_state["email_type"] == "new"
        assert updated_state["current_step"] == "questioning"
        assert updated_state["collected_answers"] == {"question1": "answer1"}
        assert "updated_at" in updated_state
        assert updated_state["updated_at"] != initial_state["updated_at"]

    def test_validate_state_valid(self):
        """妥当な状態の検証テスト"""
        state = create_initial_state("test_session")
        assert validate_state(state) is True

    def test_validate_state_invalid_step(self):
        """無効なステップの検証テスト"""
        state = create_initial_state("test_session")
        state["current_step"] = "invalid_step"
        assert validate_state(state) is False

    def test_validate_state_negative_retry(self):
        """負のリトライ回数の検証テスト"""
        state = create_initial_state("test_session")
        state["retry_count"] = -1
        assert validate_state(state) is False

    def test_validate_state_missing_required_fields(self):
        """必須フィールド不足の検証テスト"""
        state = create_initial_state("test_session")
        del state["current_step"]
        assert validate_state(state) is False

    def test_get_state_summary(self):
        """状態サマリー取得のテスト"""
        state = create_initial_state("test_session")
        state["email_type"] = "new"
        state["recipient_info"] = {"name": "Test User"}
        state["personal_info"] = {"name": "Sender"}
        state["collected_answers"] = {"q1": "a1", "q2": "a2"}

        summary = get_state_summary(state)

        assert summary["current_step"] == "information_collection"
        assert summary["email_type"] == "new"
        assert summary["has_recipient_info"] is True
        assert summary["has_personal_info"] is True
        assert summary["answers_count"] == 2
        assert summary["retry_count"] == 0
        assert summary["session_id"] == "test_session"


class TestStateManager:
    """StateManagerクラスのテスト"""

    def setup_method(self):
        """テスト前の準備"""
        self.manager = StateManager()

    def test_create_session(self):
        """セッション作成のテスト"""
        session_id = self.manager.create_session("test_session")
        assert session_id == "test_session"

        state = self.manager.get_state(session_id)
        assert state is not None
        assert state["session_id"] == "test_session"

    def test_create_session_auto_id(self):
        """自動セッションID生成のテスト"""
        session_id = self.manager.create_session()
        assert session_id is not None
        assert len(session_id) > 0

        state = self.manager.get_state(session_id)
        assert state is not None

    def test_get_state_nonexistent(self):
        """存在しないセッションの取得テスト"""
        state = self.manager.get_state("nonexistent")
        assert state is None

    def test_update_state(self):
        """状態更新のテスト"""
        session_id = self.manager.create_session("test_session")

        updates = {"email_type": "reply", "current_step": "content_creation"}

        success = self.manager.update_state(session_id, updates)
        assert success is True

        state = self.manager.get_state(session_id)
        assert state["email_type"] == "reply"
        assert state["current_step"] == "content_creation"

    def test_update_state_nonexistent(self):
        """存在しないセッションの更新テスト"""
        success = self.manager.update_state("nonexistent", {"email_type": "new"})
        assert success is False

    def test_add_answer(self):
        """回答追加のテスト"""
        session_id = self.manager.create_session("test_session")

        success = self.manager.add_answer(session_id, "question1", "answer1")
        assert success is True

        state = self.manager.get_state(session_id)
        assert state["collected_answers"]["question1"] == "answer1"

    def test_set_error(self):
        """エラー設定のテスト"""
        session_id = self.manager.create_session("test_session")

        success = self.manager.set_error(session_id, "Test error message")
        assert success is True

        state = self.manager.get_state(session_id)
        assert state["current_step"] == "error"
        assert state["error_message"] == "Test error message"
        assert state["retry_count"] == 1

    def test_clear_error(self):
        """エラークリアのテスト"""
        session_id = self.manager.create_session("test_session")
        self.manager.set_error(session_id, "Test error")

        success = self.manager.clear_error(session_id)
        assert success is True

        state = self.manager.get_state(session_id)
        assert state["error_message"] is None

    def test_get_session_summary(self):
        """セッションサマリー取得のテスト"""
        session_id = self.manager.create_session("test_session")

        summary = self.manager.get_session_summary(session_id)
        assert summary is not None
        assert summary["session_id"] == session_id
        assert summary["current_step"] == "information_collection"

    def test_list_sessions(self):
        """セッション一覧取得のテスト"""
        self.manager.create_session("session1")
        self.manager.create_session("session2")

        sessions = self.manager.list_sessions()
        assert len(sessions) == 2

        session_ids = [s["session_id"] for s in sessions]
        assert "session1" in session_ids
        assert "session2" in session_ids

    def test_delete_session(self):
        """セッション削除のテスト"""
        session_id = self.manager.create_session("test_session")

        success = self.manager.delete_session(session_id)
        assert success is True

        state = self.manager.get_state(session_id)
        assert state is None

    def test_delete_nonexistent_session(self):
        """存在しないセッションの削除テスト"""
        success = self.manager.delete_session("nonexistent")
        assert success is False
