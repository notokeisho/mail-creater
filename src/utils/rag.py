"""
RAG機能

シンプルなテキストベース検索を使用したRAG機能の実装
"""

import os
import json
import re
from typing import List, Dict, Any
from src.config import Config


class PersonalInfoRAG:
    """個人情報RAGユーティリティ（テキストベース検索）"""

    def __init__(self, persist_directory: str = "text_db"):
        self.persist_directory = persist_directory
        self.personal_info = {}
        self.indexed_data = []
        self._load_or_create_index()

    def _load_or_create_index(self):
        """インデックスを読み込みまたは作成"""
        index_file = os.path.join(self.persist_directory, "personal_info_index.json")

        if os.path.exists(index_file):
            try:
                with open(index_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.personal_info = data.get("personal_info", {})
                    self.indexed_data = data.get("indexed_data", [])
                print(f"Index loaded from {index_file}")
            except Exception as e:
                print(f"Failed to load index: {e}")
                self.personal_info = {}
                self.indexed_data = []
                # インデックスが読み込めない場合は新規作成
                self.index_personal_info()
        else:
            print("New index will be created")
            # 新規作成時は個人情報を自動的にインデックス化
            self.index_personal_info()

    def load_personal_info(self, file_path: str = None) -> Dict[str, Any]:
        """個人情報JSONをロード"""
        file_path = file_path or Config.PERSONAL_INFO_FILE
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def index_personal_info(self, personal_info: Dict[str, Any] = None):
        """個人情報をインデックスに登録"""
        if personal_info is None:
            personal_info = self.load_personal_info()

        self.personal_info = personal_info
        self.indexed_data = []

        # 各フィールドをインデックス化
        for field, value in personal_info.items():
            if value and str(value).strip():
                self.indexed_data.append(
                    {
                        "field": field,
                        "content": str(value),
                        "type": "personal_info",
                        "keywords": self._extract_keywords(str(value)),
                    }
                )

        # 保存
        self._save_index()
        print(f"Indexed {len(self.indexed_data)} personal info fields")

    def _extract_keywords(self, text: str) -> List[str]:
        """テキストからキーワードを抽出"""
        # 基本的なキーワード抽出（日本語対応）
        keywords = []

        # 文字列を分割してキーワードとして扱う
        words = re.findall(r"[\w\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]+", text)
        keywords.extend(words)

        # 元のテキストも含める
        keywords.append(text)

        return list(set(keywords))

    def _save_index(self):
        """インデックスを保存"""
        os.makedirs(self.persist_directory, exist_ok=True)
        index_file = os.path.join(self.persist_directory, "personal_info_index.json")

        data = {"personal_info": self.personal_info, "indexed_data": self.indexed_data}

        with open(index_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def search(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        """クエリに対して関連する個人情報を検索"""
        if not self.indexed_data:
            return []

        results = []
        query_lower = query.lower()

        for item in self.indexed_data:
            score = 0

            # 完全一致
            if query in item["content"]:
                score += 10
            elif query_lower in item["content"].lower():
                score += 8

            # キーワード一致
            for keyword in item["keywords"]:
                if query in keyword:
                    score += 5
                elif query_lower in keyword.lower():
                    score += 3

            # フィールド名一致
            if query in item["field"]:
                score += 2

            if score > 0:
                results.append(
                    {
                        "field": item["field"],
                        "content": item["content"],
                        "type": item["type"],
                        "score": score,
                    }
                )

        # スコアでソート
        results.sort(key=lambda x: x["score"], reverse=True)

        # 上位k件を返す
        return results[:k]

    def clear_index(self):
        """インデックスをクリア"""
        if os.path.exists(self.persist_directory):
            import shutil

            shutil.rmtree(self.persist_directory)

        self.personal_info = {}
        self.indexed_data = []

    def get_index_info(self) -> Dict[str, Any]:
        """インデックス情報を取得"""
        return {
            "status": "active",
            "index_size": len(self.indexed_data),
            "persist_directory": self.persist_directory,
            "exists": os.path.exists(self.persist_directory),
            "personal_info_fields": (
                list(self.personal_info.keys()) if self.personal_info else []
            ),
        }

    def get_all_personal_info(self) -> Dict[str, Any]:
        """全ての個人情報を取得"""
        return self.personal_info.copy()


# 使い方例（テスト用）
# rag = PersonalInfoRAG()
# rag.index_personal_info()
# print(rag.search("田中太郎"))
