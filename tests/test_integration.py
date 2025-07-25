"""
統合テスト

LangGraphワークフローの統合テスト
"""

import pytest
from unittest.mock import patch
from src.main import EmailCreationWorkflow
from src.models.state import create_initial_state


class TestEmailCreationWorkflow:
    """EmailCreationWorkflowのテスト"""

    def setup_method(self):
        """テスト前の準備"""
        self.workflow = EmailCreationWorkflow()

    def test_workflow_initialization(self):
        """ワークフローの初期化テスト"""
        assert self.workflow is not None
        assert hasattr(self.workflow, "workflow")
        assert hasattr(self.workflow, "info_collector")
        assert hasattr(self.workflow, "questioner")
        assert hasattr(self.workflow, "content_creator")

    def test_should_continue_logic(self):
        """条件分岐ロジックのテスト"""
        # 正常ケース
        state = create_initial_state()
        state["error_message"] = None
        state["current_step"] = "information_collection"
        result = self.workflow._should_continue(state)
        assert result == "continue"

        # エラーケース
        state["error_message"] = "エラーが発生しました"
        result = self.workflow._should_continue(state)
        assert result == "error"

        # 完了ケース
        state["current_step"] = "completed"
        state["error_message"] = None
        result = self.workflow._should_continue(state)
        assert result == "end"

    @patch("builtins.input")
    def test_information_collection_node_success(self, mock_input):
        """情報収集ノードの成功テスト"""
        # モック入力の設定
        mock_input.side_effect = [
            "テスト太郎",  # 受信者氏名
            "テスト株式会社",  # 会社名
            "営業部",  # 部署名
            "元メール内容",  # 元メール内容
        ]

        initial_state = create_initial_state()
        result = self.workflow._information_collection_node(initial_state)

        assert result["email_type"] == "reply"
        assert result["recipient_info"]["name"] == "テスト太郎"
        assert result["recipient_info"]["company"] == "テスト株式会社"
        assert result["current_step"] == "questioning"
        assert result["error_message"] is None

    @patch("builtins.input")
    def test_questioning_node_success(self, mock_input):
        """質問ノードの成功テスト"""
        # モック入力の設定
        mock_input.side_effect = [
            "資料送付",  # 目的
            "至急返信希望",  # 追加情報
        ]

        initial_state = create_initial_state()
        initial_state["email_type"] = "reply"
        initial_state["recipient_info"] = {
            "name": "テスト太郎",
            "company": "テスト社",
            "department": "テスト部",
        }

        result = self.workflow._questioning_node(initial_state)

        assert "purpose" in result["collected_answers"]
        assert result["current_step"] == "content_creation"
        assert result["error_message"] is None

    def test_content_creation_node_success(self):
        """文章作成ノードの成功テスト"""
        initial_state = create_initial_state()
        initial_state["email_type"] = "reply"
        initial_state["recipient_info"] = {
            "name": "テスト太郎",
            "company": "テスト社",
            "department": "テスト部",
        }
        initial_state["collected_answers"] = {
            "purpose": "資料送付",
        }

        result = self.workflow._content_creation_node(initial_state)

        assert result["current_step"] == "completed"
        assert "final_email" in result
        assert result["error_message"] is None

    @patch("builtins.input")
    def test_error_handler_node(self, mock_input):
        """エラーハンドリングノードのテスト"""
        mock_input.return_value = "1"  # 継続を選択

        initial_state = create_initial_state()
        initial_state["error_message"] = "テストエラー"
        initial_state["retry_count"] = 0

        result = self.workflow._error_handler_node(initial_state)

        assert result["retry_count"] == 1
        assert result["error_message"] is None

    @patch("builtins.input")
    def test_workflow_run_success(self, mock_input):
        """ワークフロー実行の成功テスト"""
        # モック入力の設定
        mock_input.side_effect = [
            "テスト太郎",  # 受信者氏名
            "テスト株式会社",  # 会社名
            "営業部",  # 部署名
            "元メール内容",  # 元メール内容
            "資料送付",  # 目的
            "至急返信希望",  # 追加情報
        ]

        result = self.workflow.run("test_session")

        assert result["success"] is True
        assert "final_email" in result
        assert result["session_id"] == "test_session"

    def test_workflow_run_with_error(self):
        """エラー時のワークフロー実行テスト"""
        result = self.workflow.run("")  # 空のセッションIDでエラーをシミュレート

        assert "success" in result
        assert "session_id" in result

    def test_session_id_generation(self):
        """セッションID生成のテスト"""
        with patch("builtins.input", return_value="1"):
            result1 = self.workflow.run("session1")
            result2 = self.workflow.run("session2")

        assert result1["session_id"] == "session1"
        assert result2["session_id"] == "session2"

    def test_state_consistency(self):
        """状態の整合性テスト"""
        initial_state = create_initial_state("test_session")

        # 情報収集
        state1 = self.workflow._information_collection_node(initial_state)
        assert state1["email_type"] == "reply"
        assert state1["current_step"] == "questioning"

        # 質問
        state2 = self.workflow._questioning_node(state1)
        assert state2["current_step"] == "content_creation"

        # 文章作成
        state3 = self.workflow._content_creation_node(state2)
        assert state3["current_step"] == "completed"

    def test_workflow_output_format(self):
        """ワークフロー出力形式のテスト"""
        with patch("builtins.input", return_value="テスト"):
            result = self.workflow.run("test_session")

        assert isinstance(result, dict)
        assert "success" in result
        assert "session_id" in result
        assert "error_message" in result

    @patch("builtins.input")
    def test_error_recovery(self, mock_input):
        """エラー回復のテスト"""
        mock_input.side_effect = ["1", "1", "1"]  # 3回リトライ

        initial_state = create_initial_state()
        initial_state["error_message"] = "テストエラー"
        initial_state["retry_count"] = 0

        result = self.workflow._error_handler_node(initial_state)

        assert result["retry_count"] <= 3
        assert result["error_message"] is None


class TestWorkflowIntegration:
    """ワークフロー統合テスト"""

    def setup_method(self):
        """テスト前の準備"""
        self.workflow = EmailCreationWorkflow()

    def test_personal_info_integration(self):
        """個人情報統合のテスト"""
        initial_state = create_initial_state()
        initial_state["email_type"] = "reply"
        initial_state["recipient_info"] = {
            "name": "テスト太郎",
            "company": "テスト社",
            "department": "テスト部",
        }
        initial_state["collected_answers"] = {
            "purpose": "資料送付",
        }

        result = self.workflow._content_creation_node(initial_state)

        assert result["final_email"] is not None
        # 個人情報が含まれていることを確認
        email_content = result["final_email"]
        assert "株式会社サンプル" in email_content or "田中太郎" in email_content

    def test_rag_integration(self):
        """RAG統合のテスト"""
        from src.utils.rag import PersonalInfoRAG

        rag = PersonalInfoRAG()
        personal_info = rag.get_all_personal_info()

        # 個人情報が取得できることを確認
        assert isinstance(personal_info, dict)
        assert len(personal_info) > 0
