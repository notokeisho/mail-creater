"""
State管理ユーティリティ

Stateオブジェクトの操作と管理を行うユーティリティ
"""

import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime

from ..models.state import (
    EmailState,
    create_initial_state,
    update_state,
    validate_state,
    get_state_summary,
)


class StateManager:
    """State管理クラス"""

    def __init__(self):
        """初期化"""
        self._states: Dict[str, EmailState] = {}

    def create_session(self, session_id: Optional[str] = None) -> str:
        """
        新しいセッションを作成

        Args:
            session_id: 指定するセッションID（Noneの場合は自動生成）

        Returns:
            str: セッションID
        """
        if session_id is None:
            session_id = str(uuid.uuid4())

        state = create_initial_state(session_id)
        self._states[session_id] = state

        return session_id

    def get_state(self, session_id: str) -> Optional[EmailState]:
        """
        状態を取得

        Args:
            session_id: セッションID

        Returns:
            Optional[EmailState]: 状態（存在しない場合はNone）
        """
        return self._states.get(session_id)

    def update_state(self, session_id: str, updates: Dict[str, Any]) -> bool:
        """
        状態を更新

        Args:
            session_id: セッションID
            updates: 更新内容

        Returns:
            bool: 更新成功フラグ
        """
        if session_id not in self._states:
            return False

        current_state = self._states[session_id]
        updated_state = update_state(current_state, updates)

        # 妥当性検証
        if not validate_state(updated_state):
            return False

        self._states[session_id] = updated_state
        return True

    def add_answer(self, session_id: str, question_key: str, answer: Any) -> bool:
        """
        回答を追加

        Args:
            session_id: セッションID
            question_key: 質問のキー
            answer: 回答内容

        Returns:
            bool: 追加成功フラグ
        """
        if session_id not in self._states:
            return False

        current_state = self._states[session_id]
        current_answers = current_state.get("collected_answers", {})
        current_answers[question_key] = answer

        return self.update_state(session_id, {"collected_answers": current_answers})

    def set_error(self, session_id: str, error_message: str) -> bool:
        """
        エラーを設定

        Args:
            session_id: セッションID
            error_message: エラーメッセージ

        Returns:
            bool: 設定成功フラグ
        """
        return self.update_state(
            session_id,
            {
                "current_step": "error",
                "error_message": error_message,
                "retry_count": self._states[session_id].get("retry_count", 0) + 1,
            },
        )

    def clear_error(self, session_id: str) -> bool:
        """
        エラーをクリア

        Args:
            session_id: セッションID

        Returns:
            bool: クリア成功フラグ
        """
        return self.update_state(session_id, {"error_message": None})

    def get_session_summary(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        セッションのサマリーを取得

        Args:
            session_id: セッションID

        Returns:
            Optional[Dict[str, Any]]: セッションサマリー
        """
        state = self.get_state(session_id)
        if state is None:
            return None

        return get_state_summary(state)

    def list_sessions(self) -> List[Dict[str, Any]]:
        """
        セッション一覧を取得

        Returns:
            List[Dict[str, Any]]: セッション一覧
        """
        sessions = []
        for session_id, state in self._states.items():
            summary = get_state_summary(state)
            summary["session_id"] = session_id
            sessions.append(summary)

        return sessions

    def delete_session(self, session_id: str) -> bool:
        """
        セッションを削除

        Args:
            session_id: セッションID

        Returns:
            bool: 削除成功フラグ
        """
        if session_id in self._states:
            del self._states[session_id]
            return True
        return False

    def cleanup_old_sessions(self, max_age_hours: int = 24) -> int:
        """
        古いセッションをクリーンアップ

        Args:
            max_age_hours: 最大保持時間（時間）

        Returns:
            int: 削除されたセッション数
        """
        current_time = datetime.now()
        deleted_count = 0
        sessions_to_delete = []

        for session_id, state in self._states.items():
            created_at = state.get("created_at")
            if created_at:
                try:
                    created_time = datetime.fromisoformat(
                        created_at.replace("Z", "+00:00")
                    )
                    age_hours = (current_time - created_time).total_seconds() / 3600

                    if age_hours > max_age_hours:
                        sessions_to_delete.append(session_id)
                except ValueError:
                    # 日時形式が不正な場合は削除対象とする
                    sessions_to_delete.append(session_id)

        for session_id in sessions_to_delete:
            self.delete_session(session_id)
            deleted_count += 1

        return deleted_count
