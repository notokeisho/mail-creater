"""
RAG機能のテスト
"""

import os
import pytest
from src.utils.rag import PersonalInfoRAG
from src.config import Config


@pytest.mark.skipif(
    not Config.OPENAI_API_KEY, reason="OPENAI_API_KEYが未設定のためスキップ"
)
class TestPersonalInfoRAG:
    def setup_method(self):
        self.rag = PersonalInfoRAG(persist_directory="test_text_db")
        self.rag.clear_index()

    def teardown_method(self):
        self.rag.clear_index()

    def test_index_and_search(self):
        """インデックス作成と検索のテスト"""
        # ダミー個人情報をインデックス
        self.rag.index_personal_info()

        # 検索
        results = self.rag.search("田中太郎")
        assert isinstance(results, list)
        # 結果がある場合は内容をチェック
        if results:
            assert any("田中太郎" in r["content"] for r in results)
            assert all("score" in r for r in results)

        # 別のフィールドで検索
        results = self.rag.search("株式会社サンプル")
        assert isinstance(results, list)
        if results:
            assert any("株式会社サンプル" in r["content"] for r in results)

    def test_search_no_result(self):
        """結果がない検索のテスト"""
        self.rag.index_personal_info()
        results = self.rag.search("存在しないキーワード")
        assert isinstance(results, list)
        assert len(results) == 0

    def test_index_info(self):
        """インデックス情報取得のテスト"""
        info = self.rag.get_index_info()
        assert isinstance(info, dict)
        assert "status" in info
        assert "index_size" in info
        assert "personal_info_fields" in info

    def test_clear_index(self):
        """インデックスクリアのテスト"""
        self.rag.index_personal_info()
        self.rag.clear_index()
        info = self.rag.get_index_info()
        assert info["status"] == "active"
        assert info["index_size"] == 0

    def test_load_personal_info(self):
        """個人情報読み込みのテスト"""
        info = self.rag.load_personal_info()
        assert isinstance(info, dict)
        assert "name" in info
        assert "company_name" in info

    def test_get_all_personal_info(self):
        """全個人情報取得のテスト"""
        self.rag.index_personal_info()
        all_info = self.rag.get_all_personal_info()
        assert isinstance(all_info, dict)
        assert "name" in all_info
        assert "company_name" in all_info

    def test_search_scoring(self):
        """検索スコアリングのテスト"""
        self.rag.index_personal_info()

        # 完全一致のテスト
        results = self.rag.search("田中太郎")
        if results:
            # スコアが高い順にソートされていることを確認
            scores = [r["score"] for r in results]
            assert scores == sorted(scores, reverse=True)

            # スコアが正の値であることを確認
            assert all(score > 0 for score in scores)

    def test_keyword_extraction(self):
        """キーワード抽出のテスト"""
        self.rag.index_personal_info()
        info = self.rag.get_index_info()
        assert info["index_size"] > 0  # インデックスが作成されていることを確認
