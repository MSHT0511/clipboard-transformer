"""
統合テスト - クリップボード変換の動作確認
"""

import json
import os
import tempfile
import time
from unittest.mock import Mock, patch

import pytest

from clipboard_util import get_text, has_text, set_text
from config import Config
from main import ClipboardTransformerApp
from transformer import Transformer


class TestClipboardOperations:
    """クリップボード操作の基本テスト"""

    def test_set_and_get_text(self):
        """クリップボードへのテキスト設定と取得"""
        test_text = "テストテキスト"
        assert set_text(test_text) is True
        time.sleep(0.05)
        assert get_text() == test_text

    def test_has_text_with_text(self):
        """テキストがある場合のhas_text"""
        set_text("test")
        time.sleep(0.05)
        assert has_text()

    def test_set_empty_string(self):
        """空文字列の設定"""
        assert set_text("") is True
        time.sleep(0.05)
        assert get_text() == ""

    def test_unicode_text(self):
        """Unicode文字のクリップボード操作"""
        test_text = "日本語 🎉 𠮷野家"
        assert set_text(test_text) is True
        time.sleep(0.05)
        assert get_text() == test_text

    def test_long_text(self):
        """長いテキストのクリップボード操作"""
        test_text = "あ" * 10000
        assert set_text(test_text) is True
        time.sleep(0.05)
        retrieved = get_text()
        assert retrieved == test_text
        assert len(retrieved) == 10000

    def test_special_characters(self):
        """特殊文字を含むテキスト"""
        test_text = "Line1\nLine2\tTab\r\nCRLF"
        assert set_text(test_text) is True
        time.sleep(0.05)
        assert get_text() == test_text


class TestClipboardTransformation:
    """クリップボード変換の統合テスト"""

    @pytest.fixture
    def temp_config(self):
        """テスト用の一時設定ファイルを作成"""
        config_data = {
            "enabled": True,
            "rules": [
                {"name": "literal-test", "type": "literal", "from": "旧文字列", "to": "新文字列", "enabled": True},
                {
                    "name": "regex-test",
                    "type": "regex",
                    "pattern": r"\d{4}-\d{2}-\d{2}",
                    "replacement": "DATE_REMOVED",
                    "enabled": True,
                },
            ],
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
            json.dump(config_data, f)
            temp_file = f.name

        yield temp_file

        if os.path.exists(temp_file):
            os.unlink(temp_file)

    def test_literal_replacement(self, temp_config):
        """リテラル置換の統合テスト"""
        config = Config(temp_config)
        transformer = Transformer()
        transformer.load_rules_from_config(config.get_rules())

        input_text = "これは旧文字列です"
        expected = "これは新文字列です"

        set_text(input_text)
        time.sleep(0.05)
        clipboard_text = get_text()
        result = transformer.transform(clipboard_text)

        assert result == expected

    def test_regex_replacement(self, temp_config):
        """正規表現置換の統合テスト"""
        config = Config(temp_config)
        transformer = Transformer()
        transformer.load_rules_from_config(config.get_rules())

        input_text = "今日は2026-05-03です"
        expected = "今日はDATE_REMOVEDです"

        set_text(input_text)
        time.sleep(0.05)
        clipboard_text = get_text()
        result = transformer.transform(clipboard_text)

        assert result == expected

    def test_both_rules(self, temp_config):
        """複数ルールの統合テスト"""
        config = Config(temp_config)
        transformer = Transformer()
        transformer.load_rules_from_config(config.get_rules())

        input_text = "旧文字列は2026-05-03に変更されます"
        expected = "新文字列はDATE_REMOVEDに変更されます"

        set_text(input_text)
        time.sleep(0.05)
        clipboard_text = get_text()
        result = transformer.transform(clipboard_text)

        assert result == expected

    def test_no_change(self, temp_config):
        """変換が不要な場合の統合テスト"""
        config = Config(temp_config)
        transformer = Transformer()
        transformer.load_rules_from_config(config.get_rules())

        input_text = "この文字列は変更されません"

        set_text(input_text)
        time.sleep(0.05)
        clipboard_text = get_text()
        result = transformer.transform(clipboard_text)

        assert result == input_text

    def test_clipboard_roundtrip(self, temp_config):
        """クリップボード経由の変換ラウンドトリップ"""
        config = Config(temp_config)
        transformer = Transformer()
        transformer.load_rules_from_config(config.get_rules())

        # 元のテキストをクリップボードに設定
        original = "旧文字列"
        set_text(original)
        time.sleep(0.05)

        # クリップボードから取得
        clipboard_text = get_text()
        assert clipboard_text == original

        # 変換
        transformed = transformer.transform(clipboard_text)
        assert transformed == "新文字列"

        # 変換後をクリップボードに設定
        set_text(transformed)
        time.sleep(0.05)

        # 再取得して確認
        final = get_text()
        assert final == "新文字列"


class TestOnPasteDetected:
    """_on_paste_detected() メソッドの統合テスト"""

    @pytest.fixture
    def temp_config_file(self):
        """テスト用の一時設定ファイルを作成"""
        config_data = {
            "enabled": True,
            "rules": [{"name": "test-rule", "type": "literal", "from": "変換前", "to": "変換後", "enabled": True}],
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
            json.dump(config_data, f)
            temp_file = f.name

        yield temp_file

        if os.path.exists(temp_file):
            os.unlink(temp_file)

    @pytest.fixture
    def app(self, temp_config_file):
        """モックされたKeyboardHookを持つアプリケーションインスタンス"""
        with patch("main.KeyboardHook") as mock_hook_class:
            mock_hook_instance = Mock()
            mock_hook_class.return_value = mock_hook_instance

            with patch("main.Config") as mock_config_class:
                mock_config = Config(temp_config_file)
                mock_config_class.return_value = mock_config

                app = ClipboardTransformerApp()
                app.hook = mock_hook_instance
                return app

    @patch("main.has_text")
    @patch("main.get_text")
    @patch("main.set_text")
    def test_disabled_returns_false(self, mock_set, mock_get, mock_has, app):
        """機能が無効の場合は False を返す"""
        app.config.enabled = False

        result = app._on_paste_detected()

        assert result is False
        mock_has.assert_not_called()
        mock_get.assert_not_called()
        mock_set.assert_not_called()

    @patch("main.has_text", return_value=False)
    @patch("main.get_text")
    @patch("main.set_text")
    def test_no_text_returns_false(self, mock_set, mock_get, mock_has, app):
        """クリップボードにテキストがない場合は False を返す"""
        app.config.enabled = True

        result = app._on_paste_detected()

        assert result is False
        mock_has.assert_called_once()
        mock_get.assert_not_called()
        mock_set.assert_not_called()

    @patch("main.has_text", return_value=True)
    @patch("main.get_text", return_value="")
    @patch("main.set_text")
    def test_empty_text_returns_false(self, mock_set, mock_get, mock_has, app):
        """空文字列の場合は False を返す"""
        app.config.enabled = True

        result = app._on_paste_detected()

        assert result is False
        mock_has.assert_called_once()
        mock_get.assert_called_once()
        mock_set.assert_not_called()

    @patch("main.has_text", return_value=True)
    @patch("main.get_text", return_value="変換されないテキスト")
    @patch("main.set_text")
    def test_no_transformation_returns_false(self, mock_set, mock_get, mock_has, app):
        """変換が不要な場合は False を返す"""
        app.config.enabled = True

        result = app._on_paste_detected()

        assert result is False
        mock_has.assert_called_once()
        mock_get.assert_called_once()
        mock_set.assert_not_called()

    @patch("main.has_text", return_value=True)
    @patch("main.get_text", return_value="変換前テキスト")
    @patch("main.set_text", return_value=False)
    def test_set_text_fails_returns_false(self, mock_set, mock_get, mock_has, app):
        """set_text が失敗した場合は False を返す（元のテキストを復元する）"""
        app.config.enabled = True

        result = app._on_paste_detected()

        assert result is False
        mock_has.assert_called_once()
        mock_get.assert_called_once()
        # set_text は2回呼ばれる：1回目は変換後テキスト、2回目は復元用の元テキスト
        assert mock_set.call_count == 2
        mock_set.assert_any_call("変換後テキスト")
        mock_set.assert_any_call("変換前テキスト")
        app.hook.simulate_paste.assert_not_called()

    @patch("main.NOTIFICATION_AVAILABLE", True)
    @patch("main.Notification")
    @patch("main.has_text", return_value=True)
    @patch("main.get_text", return_value="変換前テキスト")
    @patch("main.set_text", return_value=True)
    def test_successful_transformation(self, mock_set, mock_get, mock_has, mock_notification_class, app):
        """正常に変換できた場合は True を返し、通知とペーストを実行"""
        app.config.enabled = True
        mock_notification = Mock()
        mock_notification_class.return_value = mock_notification

        result = app._on_paste_detected()

        assert result is True
        mock_has.assert_called_once()
        mock_get.assert_called_once()
        mock_set.assert_called_once_with("変換後テキスト")

        # 通知が表示された
        mock_notification_class.assert_called_once()
        mock_notification.set_audio.assert_called_once()
        mock_notification.show.assert_called_once()

        # ペーストがシミュレートされた
        app.hook.simulate_paste.assert_called_once()

    @patch("main.NOTIFICATION_AVAILABLE", False)
    @patch("main.has_text", return_value=True)
    @patch("main.get_text", return_value="変換前テキスト")
    @patch("main.set_text", return_value=True)
    def test_transformation_without_notification(self, mock_set, mock_get, mock_has, app):
        """通知が無効でも変換は成功する"""
        app.config.enabled = True

        result = app._on_paste_detected()

        assert result is True
        mock_set.assert_called_once_with("変換後テキスト")
        app.hook.simulate_paste.assert_called_once()

    @patch("main.NOTIFICATION_AVAILABLE", True)
    @patch("main.Notification")
    @patch("main.has_text", return_value=True)
    @patch("main.get_text", return_value="変換前テキスト")
    @patch("main.set_text", return_value=True)
    def test_notification_error_does_not_fail(self, mock_set, mock_get, mock_has, mock_notification_class, app):
        """通知でエラーが発生しても変換は成功する"""
        app.config.enabled = True
        mock_notification = Mock()
        mock_notification.show.side_effect = Exception("Test notification error")
        mock_notification_class.return_value = mock_notification

        result = app._on_paste_detected()

        # エラーが発生しても True を返す
        assert result is True
        mock_set.assert_called_once_with("変換後テキスト")
        app.hook.simulate_paste.assert_called_once()

    @patch("main.has_text", return_value=True)
    @patch("main.get_text", return_value="変換前の変換前テキスト")
    @patch("main.set_text", return_value=True)
    def test_multiple_occurrences(self, mock_set, mock_get, mock_has, app):
        """複数回出現する文字列も正しく変換される"""
        app.config.enabled = True

        result = app._on_paste_detected()

        assert result is True
        # "変換前" が2回出現する → "変換後" に2回変換される
        mock_set.assert_called_once_with("変換後の変換後テキスト")
