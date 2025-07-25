"""
State管理

LangGraphのTypedDictを使用したStateクラスの実装
"""

from typing import TypedDict, Optional, Dict, Any, List
from langgraph.graph import StateGraph


class EmailState(TypedDict):
    """
    メール文作成プロセスの状態管理クラス

    LangGraphのTypedDictを使用して型安全な状態管理を実現
    """

    # メールの基本情報
    email_type: Optional[str]  # "reply" (返信専用)
    recipient_info: Optional[Dict[str, Any]]  # 送信先情報
    original_content: Optional[str]  # 返信時の元メール内容

    # 収集された情報
    collected_answers: Dict[str, Any]  # 質問に対する回答

    # プロセス制御
    current_step: str  # 現在のステップ
    personal_info: Optional[Dict[str, Any]]  # 個人情報

    # 最終結果
    final_email: Optional[str]  # 生成されたメール文

    # エラー処理
    error_message: Optional[str]  # エラーメッセージ
    retry_count: int  # リトライ回数

    # メタデータ
    session_id: Optional[str]  # セッションID
    created_at: Optional[str]  # 作成日時
    updated_at: Optional[str]  # 更新日時


def create_initial_state(session_id: Optional[str] = None) -> EmailState:
    """
    初期状態を作成

    Args:
        session_id: セッションID

    Returns:
        EmailState: 初期状態
    """
    from datetime import datetime

    return EmailState(
        email_type=None,
        recipient_info=None,
        original_content=None,
        collected_answers={},
        current_step="information_collection",
        personal_info=None,
        final_email=None,
        error_message=None,
        retry_count=0,
        session_id=session_id,
        created_at=datetime.now().isoformat(),
        updated_at=datetime.now().isoformat(),
    )


def update_state(state: EmailState, updates: Dict[str, Any]) -> EmailState:
    """
    状態を更新

    Args:
        state: 現在の状態
        updates: 更新内容

    Returns:
        EmailState: 更新された状態
    """
    from datetime import datetime

    updated_state = state.copy()
    updated_state.update(updates)
    updated_state["updated_at"] = datetime.now().isoformat()
    return updated_state


def validate_state(state: EmailState) -> bool:
    """
    状態の妥当性を検証

    Args:
        state: 検証する状態

    Returns:
        bool: 妥当性
    """
    # 必須フィールドの存在確認
    required_fields = ["current_step", "collected_answers", "retry_count"]

    for field in required_fields:
        if field not in state:
            return False

    # ステップの妥当性確認
    valid_steps = [
        "information_collection",
        "questioning",
        "content_creation",
        "completed",
        "error",
    ]

    if state["current_step"] not in valid_steps:
        return False

    # リトライ回数の妥当性確認
    if state["retry_count"] < 0:
        return False

    return True


def get_state_summary(state: EmailState) -> Dict[str, Any]:
    """
    状態のサマリーを取得

    Args:
        state: 状態

    Returns:
        Dict[str, Any]: 状態のサマリー
    """
    return {
        "current_step": state["current_step"],
        "email_type": state["email_type"],
        "has_recipient_info": bool(state.get("recipient_info")),
        "has_personal_info": bool(state.get("personal_info")),
        "answers_count": len(state.get("collected_answers", {})),
        "error_message": state.get("error_message"),
        "retry_count": state["retry_count"],
        "session_id": state.get("session_id"),
    }
