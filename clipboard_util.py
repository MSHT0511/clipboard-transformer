"""
クリップボード操作ユーティリティ

win32clipboard を使用して Windows クリップボードの読み書きを行う
"""

import logging
import time

import win32clipboard
import win32con

logger = logging.getLogger(__name__)


def get_text() -> str:
    """
    クリップボードからテキストを取得する

    Returns:
        str: クリップボードのテキスト。テキストが無い場合は空文字列
    """
    try:
        win32clipboard.OpenClipboard()
        try:
            # テキストが利用可能かチェック
            if win32clipboard.IsClipboardFormatAvailable(win32con.CF_UNICODETEXT):
                text = win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
                return text
            elif win32clipboard.IsClipboardFormatAvailable(win32con.CF_TEXT):
                text = win32clipboard.GetClipboardData(win32con.CF_TEXT)
                return text.decode("utf-8", errors="ignore")
            else:
                logger.debug("No text data in clipboard")
                return ""
        finally:
            win32clipboard.CloseClipboard()

    except Exception as e:
        logger.error(f"Failed to get clipboard text: {e}")
        return ""


def set_text(text: str, retry_count: int = 3, retry_delay: float = 0.05) -> bool:
    """
    クリップボードにテキストを設定する

    Args:
        text: 設定するテキスト
        retry_count: リトライ回数
        retry_delay: リトライ間隔（秒）

    Returns:
        bool: 成功した場合 True
    """
    for attempt in range(retry_count):
        try:
            win32clipboard.OpenClipboard()
            try:
                win32clipboard.EmptyClipboard()
                win32clipboard.SetClipboardData(win32con.CF_UNICODETEXT, text)
                logger.debug("Clipboard text set successfully")
                return True
            finally:
                win32clipboard.CloseClipboard()

        except Exception as e:
            if attempt < retry_count - 1:
                logger.debug(f"Failed to set clipboard (attempt {attempt + 1}), retrying...")
                time.sleep(retry_delay)
            else:
                logger.error(f"Failed to set clipboard text after {retry_count} attempts: {e}")
                return False

    return False


def has_text() -> bool:
    """
    クリップボードにテキストがあるかチェックする

    Returns:
        bool: テキストがある場合 True
    """
    try:
        win32clipboard.OpenClipboard()
        try:
            has_unicode = win32clipboard.IsClipboardFormatAvailable(win32con.CF_UNICODETEXT)
            has_text = win32clipboard.IsClipboardFormatAvailable(win32con.CF_TEXT)
            return has_unicode or has_text
        finally:
            win32clipboard.CloseClipboard()

    except Exception as e:
        logger.error(f"Failed to check clipboard format: {e}")
        return False
