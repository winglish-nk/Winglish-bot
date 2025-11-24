"""
入力値のバリデーション用ユーティリティ
"""
import re
from typing import Optional


def validate_svocm_answer(
    s: str,
    v: str,
    o1: Optional[str] = None,
    o2: Optional[str] = None,
    c: Optional[str] = None,
    m: Optional[str] = None
) -> tuple[bool, Optional[str]]:
    """
    SVOCM解答の入力値を検証する
    
    Args:
        s, v, o1, o2, c, m: SVOCMの各要素
        
    Returns:
        (is_valid, error_message)のタプル
        is_validがTrueの場合、error_messageはNone
    """
    # SとVは必須
    if not s or not s.strip():
        return False, "S（主語）は必須です。"
    if not v or not v.strip():
        return False, "V（動詞）は必須です。"
    
    # 文字数制限（SQLインジェクション対策とデータベース制限）
    max_length = 500
    fields = [
        ("S", s),
        ("V", v),
        ("O1", o1),
        ("O2", o2),
        ("C", c),
        ("M", m),
    ]
    
    for field_name, field_value in fields:
        if field_value and len(field_value) > max_length:
            return False, f"{field_name}は{max_length}文字以内で入力してください。"
    
    # 危険な文字列のチェック（基本的なSQLインジェクション対策）
    dangerous_patterns = [
        r";\s*--",
        r";\s*/\*",
        r"DROP\s+TABLE",
        r"DELETE\s+FROM",
        r"UPDATE\s+.*\s+SET",
    ]
    
    all_fields = [s, v, o1, o2, c, m]
    for field_value in all_fields:
        if field_value:
            field_upper = field_value.upper()
            for pattern in dangerous_patterns:
                if re.search(pattern, field_upper, re.IGNORECASE):
                    return False, f"無効な文字列が検出されました。"
    
    return True, None


def validate_message_id(message_id: str) -> tuple[bool, Optional[int], Optional[str]]:
    """
    メッセージIDを検証する
    
    Args:
        message_id: 検証するメッセージID文字列
        
    Returns:
        (is_valid, parsed_id, error_message)のタプル
        is_validがTrueの場合、parsed_idに変換されたIDが入る
    """
    if not message_id or not message_id.strip():
        return False, None, "メッセージIDが空です。"
    
    # 数値のみかチェック
    if not message_id.strip().isdigit():
        return False, None, "メッセージIDは数値である必要があります。"
    
    try:
        parsed_id = int(message_id.strip())
        # DiscordのメッセージIDの範囲チェック（64ビット整数）
        if parsed_id < 0 or parsed_id > 2**63 - 1:
            return False, None, "無効なメッセージIDです。"
        return True, parsed_id, None
    except ValueError:
        return False, None, "メッセージIDを数値に変換できませんでした。"


def sanitize_string(value: str, max_length: int = 1000) -> str:
    """
    文字列をサニタイズする（基本的なXSS対策）
    
    Args:
        value: サニタイズする文字列
        max_length: 最大長
        
    Returns:
        サニタイズされた文字列
    """
    if not value:
        return ""
    
    # 長さ制限
    if len(value) > max_length:
        value = value[:max_length]
    
    # 制御文字を削除（ただし改行とタブは許可）
    sanitized = ""
    for char in value:
        if char.isprintable() or char in '\n\t':
            sanitized += char
    
    return sanitized.strip()

