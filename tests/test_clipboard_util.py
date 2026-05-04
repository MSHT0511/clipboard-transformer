"""
clipboard_util.py の単体テスト

クリップボード操作の詳細な動作とエラーハンドリングをテストする
"""

from unittest.mock import patch

import win32con

import clipboard_util


class TestGetText:
    """get_text() の単体テスト"""

    @patch("clipboard_util.win32clipboard")
    def test_get_unicode_text(self, mock_clipboard):
        """CF_UNICODETEXT でテキスト取得（正常系）"""
        mock_clipboard.IsClipboardFormatAvailable.return_value = True
        mock_clipboard.GetClipboardData.return_value = "Unicode テキスト"

        result = clipboard_util.get_text()

        assert result == "Unicode テキスト"
        mock_clipboard.OpenClipboard.assert_called_once()
        mock_clipboard.IsClipboardFormatAvailable.assert_called_with(win32con.CF_UNICODETEXT)
        mock_clipboard.CloseClipboard.assert_called_once()

    @patch("clipboard_util.win32clipboard")
    def test_get_text_fallback_to_cf_text(self, mock_clipboard):
        """CF_UNICODETEXT が無い場合、CF_TEXT にフォールバック"""

        def is_format_available(format_type):
            if format_type == win32con.CF_UNICODETEXT:
                return False
            elif format_type == win32con.CF_TEXT:
                return True
            return False

        mock_clipboard.IsClipboardFormatAvailable.side_effect = is_format_available
        mock_clipboard.GetClipboardData.return_value = b"ANSI text"

        result = clipboard_util.get_text()

        assert result == "ANSI text"
        # CF_TEXT からの取得を確認
        assert mock_clipboard.IsClipboardFormatAvailable.call_count == 2
        mock_clipboard.GetClipboardData.assert_called_with(win32con.CF_TEXT)

    @patch("clipboard_util.win32clipboard")
    def test_get_text_no_text_available(self, mock_clipboard):
        """テキスト形式が利用できない場合、空文字列を返す"""
        mock_clipboard.IsClipboardFormatAvailable.return_value = False

        result = clipboard_util.get_text()

        assert result == ""
        mock_clipboard.OpenClipboard.assert_called_once()
        mock_clipboard.CloseClipboard.assert_called_once()

    @patch("clipboard_util.win32clipboard")
    def test_get_text_open_clipboard_error(self, mock_clipboard):
        """OpenClipboard() が例外を投げた場合、空文字列を返す"""
        mock_clipboard.OpenClipboard.side_effect = Exception("Clipboard in use")

        result = clipboard_util.get_text()

        assert result == ""
        mock_clipboard.CloseClipboard.assert_not_called()


class TestSetText:
    """set_text() の単体テスト"""

    @patch("clipboard_util.win32clipboard")
    def test_set_text_success(self, mock_clipboard):
        """テキスト設定が1回で成功"""
        result = clipboard_util.set_text("test text")

        assert result is True
        mock_clipboard.OpenClipboard.assert_called_once()
        mock_clipboard.EmptyClipboard.assert_called_once()
        mock_clipboard.SetClipboardData.assert_called_once_with(win32con.CF_UNICODETEXT, "test text")
        mock_clipboard.CloseClipboard.assert_called_once()

    @patch("clipboard_util.time.sleep")
    @patch("clipboard_util.win32clipboard")
    def test_set_text_retry_success_on_second_attempt(self, mock_clipboard, mock_sleep):
        """1回目失敗→2回目成功のリトライロジック"""
        # 1回目は失敗、2回目は成功
        call_count = 0

        def open_clipboard_side_effect():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise Exception("Clipboard locked")
            # 2回目以降は成功（何もしない）

        mock_clipboard.OpenClipboard.side_effect = open_clipboard_side_effect

        result = clipboard_util.set_text("test", retry_count=3, retry_delay=0.01)

        assert result is True
        assert mock_clipboard.OpenClipboard.call_count == 2
        mock_sleep.assert_called_once_with(0.01)

    @patch("clipboard_util.time.sleep")
    @patch("clipboard_util.win32clipboard")
    def test_set_text_all_retries_fail(self, mock_clipboard, mock_sleep):
        """全リトライが失敗した場合、False を返す"""
        mock_clipboard.OpenClipboard.side_effect = Exception("Clipboard locked")

        result = clipboard_util.set_text("test", retry_count=3, retry_delay=0.01)

        assert result is False
        assert mock_clipboard.OpenClipboard.call_count == 3
        assert mock_sleep.call_count == 2  # 最後のリトライ後は sleep しない

    @patch("clipboard_util.time.sleep")
    @patch("clipboard_util.win32clipboard")
    def test_set_text_retry_delay(self, mock_clipboard, mock_sleep):
        """retry_delay パラメータが正しく使用される"""
        mock_clipboard.OpenClipboard.side_effect = Exception("Error")

        clipboard_util.set_text("test", retry_count=3, retry_delay=0.05)

        # 2回目と3回目の試行前に sleep が呼ばれる
        assert mock_sleep.call_count == 2
        mock_sleep.assert_called_with(0.05)


class TestHasText:
    """has_text() の単体テスト"""

    @patch("clipboard_util.win32clipboard")
    def test_has_unicode_text(self, mock_clipboard):
        """CF_UNICODETEXT が利用可能"""

        def is_format_available(format_type):
            return format_type == win32con.CF_UNICODETEXT

        mock_clipboard.IsClipboardFormatAvailable.side_effect = is_format_available

        result = clipboard_util.has_text()

        assert result is True
        mock_clipboard.OpenClipboard.assert_called_once()
        mock_clipboard.CloseClipboard.assert_called_once()

    @patch("clipboard_util.win32clipboard")
    def test_has_cf_text_only(self, mock_clipboard):
        """CF_TEXT のみが利用可能"""

        def is_format_available(format_type):
            return format_type == win32con.CF_TEXT

        mock_clipboard.IsClipboardFormatAvailable.side_effect = is_format_available

        result = clipboard_util.has_text()

        assert result is True

    @patch("clipboard_util.win32clipboard")
    def test_has_no_text(self, mock_clipboard):
        """テキスト形式が利用できない"""
        mock_clipboard.IsClipboardFormatAvailable.return_value = False

        result = clipboard_util.has_text()

        assert result is False

    @patch("clipboard_util.win32clipboard")
    def test_has_text_open_clipboard_error(self, mock_clipboard):
        """OpenClipboard() が例外を投げた場合、False を返す"""
        mock_clipboard.OpenClipboard.side_effect = Exception("Clipboard error")

        result = clipboard_util.has_text()

        assert result is False
        mock_clipboard.CloseClipboard.assert_not_called()


class TestEdgeCases:
    """エッジケース"""

    @patch("clipboard_util.win32clipboard")
    def test_get_text_cf_text_decode_error(self, mock_clipboard):
        """CF_TEXT のデコードエラーを errors='ignore' で処理"""

        def is_format_available(format_type):
            if format_type == win32con.CF_UNICODETEXT:
                return False
            elif format_type == win32con.CF_TEXT:
                return True
            return False

        mock_clipboard.IsClipboardFormatAvailable.side_effect = is_format_available
        # 不正な UTF-8 バイト列
        mock_clipboard.GetClipboardData.return_value = b"\xff\xfe Invalid UTF-8"

        result = clipboard_util.get_text()

        # errors='ignore' で処理されるため、例外は発生しない
        assert isinstance(result, str)

    @patch("clipboard_util.win32clipboard")
    def test_set_text_empty_string(self, mock_clipboard):
        """空文字列の設定も正常に処理"""
        result = clipboard_util.set_text("")

        assert result is True
        mock_clipboard.SetClipboardData.assert_called_once_with(win32con.CF_UNICODETEXT, "")
