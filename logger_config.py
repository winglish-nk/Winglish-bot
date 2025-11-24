"""
ロギング設定モジュール

構造化されたログ出力とファイル出力を提供します。
"""
import logging
import logging.handlers
import os
from pathlib import Path
from typing import Optional


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
) -> None:
    """
    ロギング設定を初期化する
    
    Args:
        log_level: ログレベル（DEBUG, INFO, WARNING, ERROR, CRITICAL）
        log_file: ログファイルのパス（Noneの場合はファイル出力なし）
        max_bytes: ログファイルの最大サイズ（バイト）
        backup_count: 保持するログファイルの数
    """
    # ログレベルを文字列から設定
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # ルートロガーの設定
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # 既存のハンドラをクリア
    root_logger.handlers.clear()
    
    # フォーマッターの設定
    formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # コンソールハンドラ（標準出力）
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # ファイルハンドラ（オプション）
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # RotatingFileHandlerを使用してファイルサイズベースのローテーション
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
        
        root_logger.info(f"📝 ログファイル: {log_file}")
    
    # discord.pyのロガーはWARNINGレベル以上のみ
    logging.getLogger('discord').setLevel(logging.WARNING)
    logging.getLogger('discord.http').setLevel(logging.INFO)


def get_logger(name: str) -> logging.Logger:
    """
    ロガーを取得する
    
    Args:
        name: ロガー名（通常はモジュール名）
        
    Returns:
        logging.Loggerインスタンス
    """
    return logging.getLogger(name)

