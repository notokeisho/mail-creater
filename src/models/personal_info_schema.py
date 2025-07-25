"""
個人情報スキーマ

個人情報のJSONスキーマ定義
"""

from typing import TypedDict, Optional


class PersonalInfo(TypedDict):
    """個人情報の型定義"""

    # 基本情報
    university_name: str
    department: str
    name: str

    # 連絡先情報
    email: str
    phone: str

    # 住所情報
    address: str
    postal_code: Optional[str]

    # その他の情報
    student_id: Optional[str]
    grade: Optional[str]

    # メタデータ
    created_at: str
    updated_at: str


# JSONスキーマ定義
PERSONAL_INFO_SCHEMA = {
    "type": "object",
    "properties": {
        "university_name": {"type": "string", "description": "大学名"},
        "department": {"type": "string", "description": "学部・学科名"},
        "name": {"type": "string", "description": "氏名"},
        "email": {"type": "string", "format": "email", "description": "メールアドレス"},
        "phone": {"type": "string", "description": "電話番号"},
        "address": {"type": "string", "description": "住所"},
        "postal_code": {"type": "string", "description": "郵便番号"},
        "student_id": {"type": "string", "description": "学籍番号"},
        "grade": {"type": "string", "description": "学年"},
        "created_at": {
            "type": "string",
            "format": "date-time",
            "description": "作成日時",
        },
        "updated_at": {
            "type": "string",
            "format": "date-time",
            "description": "更新日時",
        },
    },
    "required": ["university_name", "department", "name", "email", "phone", "address"],
    "additionalProperties": False,
}
