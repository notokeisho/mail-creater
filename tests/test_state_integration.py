"""
State管理の統合テスト

StateManagerとPersonalInfoManagerの統合テスト
"""

import pytest
from src.utils.state_manager import StateManager
from src.utils.personal_info_manager import PersonalInfoManager


class TestStateIntegration:
    """State管理の統合テスト"""

    def setup_method(self):
        """テスト前の準備"""
        self.state_manager = StateManager()
        self.personal_info_manager = PersonalInfoManager()

    def test_state_with_personal_info(self):
        """個人情報を含むState管理のテスト"""
        # セッション作成
        session_id = self.state_manager.create_session("integration_test")

        # 個人情報を取得
        personal_info = self.personal_info_manager.get()

        # Stateに個人情報を設定
        success = self.state_manager.update_state(
            session_id,
            {
                "personal_info": personal_info,
                "email_type": "new",
                "current_step": "questioning",
            },
        )

        assert success is True

        # Stateを取得して検証
        state = self.state_manager.get_state(session_id)
        assert state["personal_info"] is not None
        assert state["personal_info"]["name"] == personal_info["name"]
        assert state["personal_info"]["company_name"] == personal_info["company_name"]
        assert state["email_type"] == "new"
        assert state["current_step"] == "questioning"

    def test_state_with_recipient_info(self):
        """送信先情報を含むState管理のテスト"""
        session_id = self.state_manager.create_session("recipient_test")

        recipient_info = {
            "name": "受信者太郎",
            "email": "recipient@example.com",
            "company": "受信者株式会社",
            "department": "営業部",
        }

        success = self.state_manager.update_state(
            session_id,
            {
                "recipient_info": recipient_info,
                "email_type": "reply",
                "current_step": "content_creation",
            },
        )

        assert success is True

        state = self.state_manager.get_state(session_id)
        assert state["recipient_info"] == recipient_info
        assert state["email_type"] == "reply"
        assert state["current_step"] == "content_creation"

    def test_state_with_answers(self):
        """回答情報を含むState管理のテスト"""
        session_id = self.state_manager.create_session("answers_test")

        # 複数の回答を追加
        answers = {
            "purpose": "商談のアポイントメント",
            "tone": "丁寧",
            "urgency": "中程度",
            "details": "来週の火曜日に打ち合わせを希望",
        }

        for key, value in answers.items():
            success = self.state_manager.add_answer(session_id, key, value)
            assert success is True

        state = self.state_manager.get_state(session_id)
        assert state["collected_answers"] == answers
        assert len(state["collected_answers"]) == 4

    def test_state_error_handling(self):
        """エラーハンドリングのテスト"""
        session_id = self.state_manager.create_session("error_test")

        # エラーを設定
        error_message = "API接続エラーが発生しました"
        success = self.state_manager.set_error(session_id, error_message)
        assert success is True

        state = self.state_manager.get_state(session_id)
        assert state["current_step"] == "error"
        assert state["error_message"] == error_message
        assert state["retry_count"] == 1

        # エラーをクリア
        success = self.state_manager.clear_error(session_id)
        assert success is True

        state = self.state_manager.get_state(session_id)
        assert state["error_message"] is None

    def test_state_workflow(self):
        """完全なワークフローのテスト"""
        session_id = self.state_manager.create_session("workflow_test")

        # 1. 情報収集ステップ
        personal_info = self.personal_info_manager.get()
        success = self.state_manager.update_state(
            session_id,
            {
                "personal_info": personal_info,
                "email_type": "new",
                "current_step": "information_collection",
            },
        )
        assert success is True

        # 2. 質問ステップ
        success = self.state_manager.update_state(
            session_id, {"current_step": "questioning"}
        )
        assert success is True

        # 回答を追加
        self.state_manager.add_answer(session_id, "purpose", "会議の調整")
        self.state_manager.add_answer(session_id, "tone", "カジュアル")

        # 3. 文章作成ステップ
        success = self.state_manager.update_state(
            session_id, {"current_step": "content_creation"}
        )
        assert success is True

        # 4. 完了ステップ
        success = self.state_manager.update_state(
            session_id, {"current_step": "completed"}
        )
        assert success is True

        # 最終状態を検証
        state = self.state_manager.get_state(session_id)
        assert state["current_step"] == "completed"
        assert state["email_type"] == "new"
        assert state["personal_info"] is not None
        assert len(state["collected_answers"]) == 2
        assert state["collected_answers"]["purpose"] == "会議の調整"
        assert state["collected_answers"]["tone"] == "カジュアル"

    def test_state_validation(self):
        """State検証のテスト"""
        session_id = self.state_manager.create_session("validation_test")

        # 無効なステップを設定しようとする
        success = self.state_manager.update_state(
            session_id, {"current_step": "invalid_step"}
        )
        assert success is False  # 検証に失敗するはず

        # 有効なステップを設定
        success = self.state_manager.update_state(
            session_id, {"current_step": "questioning"}
        )
        assert success is True
