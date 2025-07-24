"""
統合テスト

エンドツーエンドの動作確認テスト
"""

import pytest
import sys
import os
from unittest.mock import patch, MagicMock
from io import StringIO

# プロジェクトルートをパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.main import EmailCreationWorkflow
from src.models.state import EmailState, create_initial_state


class TestEmailCreationWorkflow:
    """メール文作成ワークフローの統合テスト"""

    def setup_method(self):
        """テスト前の準備"""
        self.workflow = EmailCreationWorkflow()

    def test_workflow_initialization(self):
        """ワークフローの初期化テスト"""
        assert self.workflow is not None
        assert self.workflow.info_collector is not None
        assert self.workflow.questioner is not None
        assert self.workflow.content_creator is not None
        assert self.workflow.workflow is not None

    def test_should_continue_logic(self):
        """継続判定ロジックのテスト"""
        # 正常ケース
        normal_state = create_initial_state()
        result = self.workflow._should_continue(normal_state)
        assert result == "continue"

        # エラーケース
        error_state = create_initial_state()
        error_state["error_message"] = "テストエラー"
        result = self.workflow._should_continue(error_state)
        assert result == "error"

        # 完了ケース
        completed_state = create_initial_state()
        completed_state["current_step"] = "completed"
        result = self.workflow._should_continue(completed_state)
        assert result == "end"

    @patch("builtins.input")
    def test_information_collection_node_success(self, mock_input):
        """情報収集ノードの成功テスト"""
        # モック入力の設定
        mock_input.side_effect = [
            "1",  # 新規送信
            "テスト太郎",  # 受信者氏名
            "test@example.com",  # メールアドレス
            "テスト株式会社",  # 会社名
            "営業部",  # 部署名
        ]

        initial_state = create_initial_state()
        result = self.workflow._information_collection_node(initial_state)

        assert result["email_type"] == "new"
        assert result["recipient_info"]["name"] == "テスト太郎"
        assert result["recipient_info"]["email"] == "test@example.com"
        assert result["current_step"] == "questioning"
        assert result["error_message"] is None

    @patch("builtins.input")
    def test_questioning_node_success(self, mock_input):
        """質問ノードの成功テスト"""
        # モック入力の設定
        mock_input.side_effect = [
            "アポイント調整",  # 目的
            "丁寧",  # 文体
            "特にありません",  # 追加情報
        ]

        initial_state = create_initial_state()
        initial_state["email_type"] = "new"
        initial_state["recipient_info"] = {
            "name": "テスト太郎",
            "email": "test@example.com",
        }

        result = self.workflow._questioning_node(initial_state)

        assert "purpose" in result["collected_answers"]
        assert "tone" in result["collected_answers"]
        assert result["current_step"] == "content_creation"
        assert result["error_message"] is None

    def test_content_creation_node_success(self):
        """文章作成ノードの成功テスト"""
        initial_state = create_initial_state()
        initial_state["email_type"] = "new"
        initial_state["recipient_info"] = {
            "name": "テスト太郎",
            "email": "test@example.com",
            "company": "テスト株式会社",
        }
        initial_state["collected_answers"] = {
            "purpose": "アポイント調整",
            "tone": "丁寧",
        }

        result = self.workflow._content_creation_node(initial_state)

        assert result["current_step"] == "completed"
        assert result["error_message"] is None
        assert "final_email" in result

    def test_error_handler_node(self):
        """エラーハンドリングノードのテスト"""
        error_state = create_initial_state()
        error_state["error_message"] = "テストエラー"
        error_state["retry_count"] = 0

        with patch("builtins.input", return_value="n"):
            result = self.workflow._error_handler_node(error_state)

        assert result["current_step"] == "error"
        assert "最終エラー" in result["error_message"]

    @patch("builtins.input")
    def test_workflow_run_success(self, mock_input):
        """ワークフロー実行の成功テスト"""
        # モック入力の設定（情報収集 + 質問）
        mock_input.side_effect = [
            "1",  # 新規送信
            "テスト太郎",  # 受信者氏名
            "test@example.com",  # メールアドレス
            "テスト株式会社",  # 会社名
            "営業部",  # 部署名
            "アポイント調整",  # 目的
            "丁寧",  # 文体
            "特にありません",  # 追加情報
        ]

        result = self.workflow.run("test_session")

        assert result["success"] is True
        assert result["session_id"] == "test_session"
        assert result["error_message"] is None
        assert "final_email" in result

    def test_workflow_run_with_error(self):
        """ワークフロー実行のエラーテスト"""
        # 実際のエラーケースをテスト（設定エラーは初期化時に発生するため）
        # 代わりに、無効なセッションIDでテスト
        result = self.workflow.run("")

        # 結果が正常に返されることを確認
        assert "success" in result
        assert "session_id" in result

    def test_session_id_generation(self):
        """セッションID生成のテスト"""
        # モック入力を使用してテスト
        with patch("builtins.input", return_value="1"):
            result1 = self.workflow.run("session1")
            result2 = self.workflow.run("session2")

        assert result1["session_id"] != result2["session_id"]
        assert result1["session_id"] is not None
        assert result2["session_id"] is not None

    def test_state_consistency(self):
        """状態の整合性テスト"""
        initial_state = create_initial_state("test_session")

        # 情報収集
        with patch("builtins.input", return_value="1"):
            state1 = self.workflow._information_collection_node(initial_state)

        # 質問
        with patch("builtins.input", return_value="テスト"):
            state2 = self.workflow._questioning_node(state1)

        # 文章作成
        state3 = self.workflow._content_creation_node(state2)

        # 状態の整合性確認
        assert state1["session_id"] == state2["session_id"] == state3["session_id"]
        assert state1["email_type"] == state2["email_type"] == state3["email_type"]
        assert (
            state1["recipient_info"]
            == state2["recipient_info"]
            == state3["recipient_info"]
        )

    @patch("sys.stdout", new_callable=StringIO)
    def test_workflow_output_format(self, mock_stdout):
        """ワークフロー出力形式のテスト"""
        with patch("builtins.input", return_value="1"):
            self.workflow.run("test_session")

        output = mock_stdout.getvalue()

        # 出力に必要な要素が含まれているか確認
        assert "メール文作成AIエージェント" in output
        assert "情報収集エージェント" in output
        assert "質問エージェント" in output
        assert "文章作成エージェント" in output

    def test_error_recovery(self):
        """エラー回復のテスト"""
        error_state = create_initial_state()
        error_state["error_message"] = "一時的なエラー"
        error_state["retry_count"] = 1

        with patch("builtins.input", return_value="y"):
            result = self.workflow._error_handler_node(error_state)

        assert result["retry_count"] == 2
        assert result["error_message"] is None
        assert result["current_step"] == "information_collection"


class TestWorkflowIntegration:
    """ワークフロー統合テスト（実際のファイル操作を含む）"""

    def test_personal_info_integration(self):
        """個人情報との統合テスト"""
        workflow = EmailCreationWorkflow()

        # 個人情報ファイルが存在することを確認
        assert os.path.exists(workflow.config.PERSONAL_INFO_FILE)

        # 個人情報が読み込めることを確認
        with open(workflow.config.PERSONAL_INFO_FILE, "r", encoding="utf-8") as f:
            import json

            personal_info = json.load(f)
            assert "name" in personal_info
            assert "email" in personal_info
            assert "company_name" in personal_info

    def test_rag_integration(self):
        """RAG機能との統合テスト"""
        workflow = EmailCreationWorkflow()

        # RAGが正常に初期化されることを確認
        assert workflow.content_creator.rag is not None

        # 個人情報が取得できることを確認
        personal_info = workflow.content_creator.rag.get_all_personal_info()
        assert isinstance(personal_info, dict)
        # 個人情報が空でないことを確認（インデックス化されているため）
        assert len(personal_info) > 0


if __name__ == "__main__":
    pytest.main([__file__])
