"""
個人情報管理ユーティリティ

個人情報の読み込み、検証、更新機能
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, Optional
from jsonschema import validate, ValidationError

from ..models.personal_info_schema import PersonalInfo, PERSONAL_INFO_SCHEMA
from ..config import Config


class PersonalInfoManager:
    """個人情報管理クラス"""

    def __init__(self, file_path: Optional[str] = None):
        """初期化"""
        self.file_path = file_path or Config.PERSONAL_INFO_FILE
        self._data: Optional[PersonalInfo] = None

    def load(self) -> PersonalInfo:
        """個人情報を読み込み"""
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(
                f"個人情報ファイルが見つかりません: {self.file_path}"
            )

        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # スキーマ検証
            validate(instance=data, schema=PERSONAL_INFO_SCHEMA)

            self._data = data
            return data

        except json.JSONDecodeError as e:
            raise ValueError(f"JSONファイルの形式が正しくありません: {e}")
        except ValidationError as e:
            raise ValueError(f"個人情報の形式が正しくありません: {e}")

    def save(self, data: PersonalInfo) -> None:
        """個人情報を保存"""
        # スキーマ検証
        validate(instance=data, schema=PERSONAL_INFO_SCHEMA)

        # 更新日時を設定
        data["updated_at"] = datetime.now().isoformat() + "Z"

        # ディレクトリが存在しない場合は作成
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)

        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        self._data = data

    def get(self) -> PersonalInfo:
        """個人情報を取得（キャッシュ付き）"""
        if self._data is None:
            self._data = self.load()
        return self._data

    def update(self, updates: Dict[str, Any]) -> PersonalInfo:
        """個人情報を更新"""
        current_data = self.get()

        # 更新データをマージ
        updated_data = {**current_data, **updates}

        # 保存
        self.save(updated_data)

        return updated_data

    def validate_file(self) -> bool:
        """ファイルの妥当性を検証"""
        try:
            self.load()
            return True
        except Exception:
            return False
