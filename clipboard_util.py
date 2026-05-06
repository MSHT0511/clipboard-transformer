"""
クリップボード操作ユーティリティ

win32clipboard を使用して Windows クリップボードの読み書きを行う
"""

import logging
import time
from contextlib import contextmanager

import win32clipboard
import win32con

from constants import CLIPBOARD_RETRY_COUNT, CLIPBOARD_RETRY_DELAY

logger = logging.getLogger(__name__)


@contextmanager
def _clipboard_context():
    """クリップボードのオープン/クローズを管理するコンテキストマネージャ"""
    win32clipboard.OpenClipboard()
    try:
        yield
    finally:
        win32clipboard.CloseClipboard()


def get_text() -> str:
    """
    クリップボードからテキストを取得する

    Returns:
        str: クリップボードのテキスト。テキストが無い場合は空文字列
    """
    try:
        with _clipboard_context():
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

    except Exception as e:
        logger.error(f"Failed to get clipboard text: {e}")
        return ""


def set_text(text: str, retry_count: int = CLIPBOARD_RETRY_COUNT, retry_delay: float = CLIPBOARD_RETRY_DELAY) -> bool:
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
            with _clipboard_context():
                win32clipboard.EmptyClipboard()
                win32clipboard.SetClipboardData(win32con.CF_UNICODETEXT, text)
                logger.debug("Clipboard text set successfully")
                return True

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
        with _clipboard_context():
            has_unicode = win32clipboard.IsClipboardFormatAvailable(win32con.CF_UNICODETEXT)
            has_text = win32clipboard.IsClipboardFormatAvailable(win32con.CF_TEXT)
            return has_unicode or has_text

    except Exception as e:
        logger.error(f"Failed to check clipboard format: {e}")
        return False
