"""
メインアプリケーション

3つのエージェントを統合したLangGraphワークフロー
"""

import os
import sys
import time
from typing import Dict, Any
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

# プロジェクトルートをパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models.state import EmailState, create_initial_state, update_state
from src.agents.information_collector import InformationCollectorAgent
from src.agents.questioner import QuestionerAgent
from src.agents.content_creator import ContentCreatorAgent
from src.config import Config


class EmailCreationWorkflow:
    """メール文作成ワークフロー（LangGraph統合）"""

    def __init__(self):
        """ワークフローの初期化"""
        self.config = Config()
        self.config.validate()

        # エージェントの初期化
        self.info_collector = InformationCollectorAgent()
        self.questioner = QuestionerAgent()
        self.content_creator = ContentCreatorAgent()

        # LangGraphワークフローの構築
        self.workflow = self._build_workflow()

    def _build_workflow(self) -> StateGraph:
        """LangGraphワークフローの構築"""

        # StateGraphの作成
        workflow = StateGraph(EmailState)

        # ノードの追加
        workflow.add_node("information_collection", self._information_collection_node)
        workflow.add_node("questioning", self._questioning_node)
        workflow.add_node("content_creation", self._content_creation_node)
        workflow.add_node("error_handler", self._error_handler_node)

        # エッジの設定
        workflow.set_entry_point("information_collection")

        # 正常フロー
        workflow.add_edge("information_collection", "questioning")
        workflow.add_edge("questioning", "content_creation")
        workflow.add_edge("content_creation", END)

        # エラーハンドリング
        workflow.add_conditional_edges(
            "information_collection",
            self._should_continue,
            {"continue": "questioning", "error": "error_handler", "end": END},
        )

        workflow.add_conditional_edges(
            "questioning",
            self._should_continue,
            {"continue": "content_creation", "error": "error_handler", "end": END},
        )

        workflow.add_conditional_edges(
            "content_creation",
            self._should_continue,
            {"continue": END, "error": "error_handler", "end": END},
        )

        workflow.add_edge("error_handler", END)

        return workflow.compile(checkpointer=MemorySaver())

    def _information_collection_node(self, state: EmailState) -> EmailState:
        """情報収集ノード"""
        try:
            print("\n" + "=" * 50)
            print("📧 情報収集エージェント")
            print("=" * 50)

            # 情報収集エージェントを実行
            updated_state = self.info_collector.run(state)

            # ステップ更新
            updated_state = update_state(
                updated_state, {"current_step": "questioning", "error_message": None}
            )

            print("✅ 情報収集が完了しました")
            return updated_state

        except Exception as e:
            print(f"❌ 情報収集でエラーが発生しました: {e}")
            return update_state(
                state, {"error_message": str(e), "current_step": "error"}
            )

    def _questioning_node(self, state: EmailState) -> EmailState:
        """質問ノード"""
        try:
            print("\n" + "=" * 50)
            print("❓ 質問エージェント")
            print("=" * 50)

            # 質問エージェントを実行
            updated_state = self.questioner.run(state)

            # ステップ更新
            updated_state = update_state(
                updated_state,
                {"current_step": "content_creation", "error_message": None},
            )

            print("✅ 質問への回答が完了しました")
            return updated_state

        except Exception as e:
            print(f"❌ 質問でエラーが発生しました: {e}")
            return update_state(
                state, {"error_message": str(e), "current_step": "error"}
            )

    def _content_creation_node(self, state: EmailState) -> EmailState:
        """文章作成ノード"""
        try:
            print("\n" + "=" * 50)
            print("✍️ 文章作成エージェント")
            print("=" * 50)

            # 文章作成エージェントを実行
            updated_state = self.content_creator.run(state)

            # ステップ更新
            updated_state = update_state(
                updated_state, {"current_step": "completed", "error_message": None}
            )

            print("✅ メール文の作成が完了しました")
            return updated_state

        except Exception as e:
            print(f"❌ 文章作成でエラーが発生しました: {e}")
            return update_state(
                state, {"error_message": str(e), "current_step": "error"}
            )

    def _error_handler_node(self, state: EmailState) -> EmailState:
        """エラーハンドリングノード"""
        print("\n" + "=" * 50)
        print("⚠️ エラーハンドリング")
        print("=" * 50)

        error_msg = state.get("error_message", "不明なエラー")
        retry_count = state.get("retry_count", 0)

        print(f"エラー内容: {error_msg}")
        print(f"リトライ回数: {retry_count}")

        if retry_count < 3:
            print("リトライしますか？ (y/n): ", end="")
            retry_choice = input().strip().lower()

            if retry_choice == "y":
                # リトライ
                updated_state = update_state(
                    state,
                    {
                        "retry_count": retry_count + 1,
                        "error_message": None,
                        "current_step": "information_collection",
                    },
                )
                print("🔄 リトライを開始します")
                return updated_state

        print("❌ 処理を終了します")
        return update_state(
            state,
            {"current_step": "error", "error_message": f"最終エラー: {error_msg}"},
        )

    def _should_continue(self, state: EmailState) -> str:
        """次のステップを決定"""
        if state.get("error_message"):
            return "error"
        elif state.get("current_step") == "completed":
            return "end"
        else:
            return "continue"

    def run(self, session_id: str = None) -> Dict[str, Any]:
        """ワークフローの実行"""
        try:
            print("🚀 メール文作成AIエージェントを開始します")
            print("=" * 60)

            # 初期状態の作成
            initial_state = create_initial_state(session_id)

            # ワークフローの実行
            config = {"configurable": {"thread_id": session_id or "default"}}
            result = self.workflow.invoke(initial_state, config)

            # 結果の整理
            final_state = result.get("__end__", result)

            print("\n" + "=" * 60)
            print("🎉 ワークフローが完了しました")
            print("=" * 60)

            return {
                "success": final_state.get("current_step") == "completed",
                "final_email": final_state.get("final_email"),
                "error_message": final_state.get("error_message"),
                "session_id": final_state.get("session_id"),
                "state": final_state,
            }

        except Exception as e:
            print(f"❌ ワークフロー実行中にエラーが発生しました: {e}")
            return {"success": False, "error_message": str(e), "session_id": session_id}

    def run_interactive(self):
        """対話型実行"""
        print("📧 メール文作成AIエージェント")
        print("=" * 40)

        # セッションIDの生成
        session_id = f"session_{int(time.time())}"

        # ワークフローの実行
        result = self.run(session_id)

        if result["success"]:
            print("\n✅ メール文の作成が完了しました！")
            if result.get("final_email"):
                print("\n📄 生成されたメール文:")
                print("-" * 40)
                print(result["final_email"])
                print("-" * 40)
        else:
            print(f"\n❌ エラーが発生しました: {result.get('error_message')}")

        return result


def main():
    """メイン関数"""
    try:
        # ワークフローの作成と実行
        workflow = EmailCreationWorkflow()
        result = workflow.run_interactive()

        return result

    except KeyboardInterrupt:
        print("\n\n👋 ユーザーによって中断されました")
        return {"success": False, "error_message": "User interrupted"}
    except Exception as e:
        print(f"\n❌ 予期しないエラーが発生しました: {e}")
        return {"success": False, "error_message": str(e)}


if __name__ == "__main__":
    main()
