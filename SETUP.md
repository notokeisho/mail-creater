# 設定ファイルのセットアップ

このドキュメントでは、メール文作成 AI エージェントの設定ファイルの準備方法を説明します。

## 必要な設定ファイル

### 1. 環境変数ファイル (.env)

プロジェクトルートに`.env`ファイルを作成し、以下の内容を設定してください：

```bash
# OpenAI API設定
OPENAI_API_KEY=your_openai_api_key_here

# その他の環境変数
ENVIRONMENT=development
LOG_LEVEL=INFO
```

**重要**: `.env`ファイルは機密情報を含むため、`.gitignore`に追加してバージョン管理から除外してください。

### 2. 個人情報ファイル (data/personal_info.json)

`data/personal_info.json`ファイルに個人情報を設定してください。以下の形式で記述します：

```json
{
  "company_name": "株式会社サンプル",
  "department": "営業部",
  "name": "田中太郎",
  "email": "tanaka.taro@sample-company.co.jp",
  "phone": "03-1234-5678",
  "address": "東京都渋谷区サンプル1-2-3",
  "postal_code": "150-0001",
  "position": "営業課長",
  "employee_id": "EMP001",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

## 必須フィールド

以下のフィールドは必須です：

- `company_name`: 会社名
- `department`: 部署名
- `name`: 氏名
- `email`: メールアドレス
- `phone`: 電話番号
- `address`: 住所

## オプションフィールド

以下のフィールドは任意です：

- `postal_code`: 郵便番号
- `position`: 役職
- `employee_id`: 社員 ID

## 動作確認

設定が正しく行われているか確認するには、以下のコマンドを実行してください：

```bash
# 設定ファイルの読み込み確認
python -c "from src.config import Config; print('Config loaded successfully')"

# 個人情報ファイルの読み込み確認
python -c "from src.utils.personal_info_manager import PersonalInfoManager; manager = PersonalInfoManager(); data = manager.get(); print('Personal info loaded successfully')"
```

## 注意事項

1. **機密情報の管理**: `.env`ファイルと個人情報ファイルは機密情報を含むため、適切に管理してください。
2. **バックアップ**: 重要な設定ファイルは定期的にバックアップを取ってください。
3. **権限設定**: 設定ファイルの読み書き権限を適切に設定してください。

## トラブルシューティング

### OpenAI API キーが設定されていない場合

```
ValueError: OPENAI_API_KEYが設定されていません。.envファイルまたは環境変数を確認してください。
```

**解決方法**: `.env`ファイルに正しい API キーを設定してください。

### 個人情報ファイルが見つからない場合

```
FileNotFoundError: 個人情報ファイルが見つかりません: /path/to/data/personal_info.json
```

**解決方法**: `data/personal_info.json`ファイルが存在することを確認してください。

### 個人情報の形式が正しくない場合

```
ValueError: 個人情報の形式が正しくありません: ...
```

**解決方法**: JSON ファイルの形式が正しいことを確認し、必須フィールドが含まれていることを確認してください。
