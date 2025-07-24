"""
設定管理

環境変数とアプリケーション設定の管理
"""

import os
from dotenv import load_dotenv

# .envファイルを読み込み
load_dotenv()


class Config:
    """アプリケーション設定クラス"""

    # OpenAI設定
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    # 環境設定
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    # ファイルパス設定
    DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    PERSONAL_INFO_FILE = os.path.join(DATA_DIR, "personal_info.json")

    @classmethod
    def validate(cls):
        """設定の妥当性を検証"""
        if not cls.OPENAI_API_KEY:
            raise ValueError(
                "OPENAI_API_KEYが設定されていません。.envファイルまたは環境変数を確認してください。"
            )

        if not os.path.exists(cls.DATA_DIR):
            os.makedirs(cls.DATA_DIR)

        return True
