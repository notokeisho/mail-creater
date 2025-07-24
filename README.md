# 📧 メール文作成 AI エージェント

LangGraph を使用した 3 つのエージェント（情報収集、質問、文章作成）による段階的なメール文作成システムです。

## 🚀 機能

- **📋 情報収集エージェント**: メール種類、送信先情報、元メール内容の収集
- **❓ 質問エージェント**: 動的な質問生成と回答収集
- **✍️ 文章作成エージェント**: RAG 検索による個人情報活用とメール文生成
- **⚠️ エラーハンドリング**: リトライ機能とエラー回復
- **🔄 状態管理**: LangGraph による型安全な状態管理

## 📦 インストール

```bash
# リポジトリのクローン
git clone <repository-url>
cd mail-creater

# 依存関係のインストール
pip install -r requirements.txt

# 環境変数の設定
cp .env.example .env
# .envファイルにOPENAI_API_KEYを設定
```

## 🎯 使用方法

### 基本的な使用方法

```bash
# メインアプリケーションの実行
python src/main.py
```

### 対話型実行

```python
from src.main import EmailCreationWorkflow

# ワークフローの作成
workflow = EmailCreationWorkflow()

# 対話型実行
result = workflow.run_interactive()

# プログラム実行
result = workflow.run("session_id")
```

## 🏗️ アーキテクチャ

### プロジェクト構造

```
src/
├── main.py                 # メインアプリケーション
├── config.py              # 設定管理
├── agents/                # エージェント群
│   ├── information_collector.py
│   ├── questioner.py
│   └── content_creator.py
├── models/                # データモデル
│   ├── state.py
│   └── personal_info_schema.py
└── utils/                 # ユーティリティ
    ├── rag.py
    ├── state_manager.py
    └── personal_info_manager.py
```

### ワークフロー

```
START → 情報収集 → 質問 → 文章作成 → END
   ↓         ↓        ↓         ↓
エラーハンドリング ← 各ノードから分岐
```

## 🧪 テスト

```bash
# 全テストの実行
pytest tests/ -v

# 特定のテストの実行
pytest tests/test_integration.py -v
pytest tests/test_state.py -v
```

## 📊 テスト結果

- **統合テスト**: 14 個のテストがすべて成功
- **全体テスト**: 53 個のテストがすべて成功
- **動作確認**: 新規送信・返信メールの両方が正常に処理

## 🔧 設定

### 環境変数

- `OPENAI_API_KEY`: OpenAI API キー
- `ENVIRONMENT`: 環境設定（development/production）
- `LOG_LEVEL`: ログレベル

### 個人情報設定

`data/personal_info.json`に個人情報を設定：

```json
{
  "company_name": "株式会社サンプル",
  "department": "営業部",
  "name": "田中太郎",
  "email": "tanaka.taro@sample-company.co.jp",
  "phone": "03-1234-5678",
  "address": "東京都渋谷区サンプル1-2-3"
}
```

## 🎯 主要機能

### 1. 情報収集エージェント

- メール種類選択（新規/返信）
- 送信先情報収集
- 元メール内容要約（返信時）
- 入力検証・エラー処理

### 2. 質問エージェント

- 動的質問生成
- ユーザー回答収集
- State 更新
- 必須項目チェック

### 3. 文章作成エージェント

- RAG 検索（個人情報取得）
- メール文生成
- 美しい出力形式
- 署名自動付与

### 4. エラーハンドリング

- エラー診断・メッセージ表示
- リトライ機能（最大 3 回）
- ユーザー選択（継続/終了）
- 状態復旧

## 📈 パフォーマンス

- **初期化時間**: ~0.003 秒
- **State 管理**: ~0.000 秒
- **RAG 検索**: ~0.000 秒
- **文章生成**: ~0.000 秒

## 🔒 セキュリティ

- 個人情報の安全な管理
- 環境変数による設定管理
- 入力検証とエラー処理

## 🤝 貢献

1. フォークを作成
2. フィーチャーブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add amazing feature'`)
4. ブランチにプッシュ (`git push origin feature/amazing-feature`)
5. プルリクエストを作成

## 📄 ライセンス

このプロジェクトは MIT ライセンスの下で公開されています。

## 📞 サポート

問題や質問がある場合は、Issue を作成してください。
