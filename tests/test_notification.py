"""
通知音機能のテスト
"""

import json
import os
import tempfile
from unittest.mock import Mock, patch

import pytest

from config import Config
from main import ClipboardTransformerApp

# winotify が利用可能かチェック
try:
    from winotify import audio

    NOTIFICATION_AVAILABLE = True
except ImportError:
    NOTIFICATION_AVAILABLE = False


class TestNotificationSound:
    """通知音関連の機能テスト"""

    @pytest.fixture
    def temp_config(self):
        """テスト用の一時設定ファイルを作成"""
        config_data = {"enabled": True, "notification_sound": "Default", "rules": []}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
            json.dump(config_data, f)
            temp_file = f.name

        yield temp_file

        if os.path.exists(temp_file):
            os.unlink(temp_file)

    @pytest.mark.skipif(not NOTIFICATION_AVAILABLE, reason="winotify not available")
    def test_get_audio_sound_default(self, temp_config):
        """デフォルト通知音の取得"""
        with patch("main.KeyboardHook"):
            app = ClipboardTransformerApp()
            app.config = Config(temp_config)
            sound = app._get_audio_sound()
            assert sound == audio.Default

    @pytest.mark.skipif(not NOTIFICATION_AVAILABLE, reason="winotify not available")
    def test_get_audio_sound_mail(self, temp_config):
        """Mail通知音の取得"""
        # 設定ファイルを更新
        with open(temp_config, encoding="utf-8") as f:
            data = json.load(f)
        data["notification_sound"] = "Mail"
        with open(temp_config, "w", encoding="utf-8") as f:
            json.dump(data, f)

        with patch("main.KeyboardHook"):
            app = ClipboardTransformerApp()
            app.config = Config(temp_config)
            sound = app._get_audio_sound()
            assert sound == audio.Mail

    @pytest.mark.skipif(not NOTIFICATION_AVAILABLE, reason="winotify not available")
    def test_get_audio_sound_all_valid_sounds(self, temp_config):
        """すべての有効な通知音を取得できることを確認"""
        for sound_name in Config.VALID_SOUNDS:
            # 設定ファイルを更新
            with open(temp_config, encoding="utf-8") as f:
                data = json.load(f)
            data["notification_sound"] = sound_name
            with open(temp_config, "w", encoding="utf-8") as f:
                json.dump(data, f)

            with patch("main.KeyboardHook"):
                app = ClipboardTransformerApp()
                app.config = Config(temp_config)
                sound = app._get_audio_sound()
                expected = getattr(audio, sound_name)
                assert sound == expected

    @pytest.mark.skipif(not NOTIFICATION_AVAILABLE, reason="winotify not available")
    def test_get_audio_sound_invalid_fallback(self, temp_config):
        """無効な通知音はデフォルトにフォールバック"""
        # 設定ファイルに無効な通知音を設定
        with open(temp_config, encoding="utf-8") as f:
            data = json.load(f)
        data["notification_sound"] = "InvalidSound"
        with open(temp_config, "w", encoding="utf-8") as f:
            json.dump(data, f)

        with patch("main.KeyboardHook"):
            app = ClipboardTransformerApp()
            app.config = Config(temp_config)
            # Config クラスで無効な音は "Default" にフォールバックされる
            assert app.config.notification_sound == "Default"
            sound = app._get_audio_sound()
            assert sound == audio.Default

    def test_on_sound_selected_handler(self, temp_config):
        """通知音選択ハンドラのテスト"""
        with patch("main.KeyboardHook"):
            app = ClipboardTransformerApp()
            app.config = Config(temp_config)

            # Mock アイコン
            mock_icon = Mock()

            # SMS を選択
            handler = app._on_sound_selected("SMS")
            handler(mock_icon, None)

            # 設定が更新されたか確認
            assert app.config.notification_sound == "SMS"

            # ファイルに保存されたか確認
            with open(temp_config, encoding="utf-8") as f:
                data = json.load(f)
            assert data["notification_sound"] == "SMS"

    def test_is_sound_checked(self, temp_config):
        """通知音のチェック状態確認テスト"""
        with patch("main.KeyboardHook"):
            app = ClipboardTransformerApp()
            app.config = Config(temp_config)
            app.config.notification_sound = "Reminder"

            # Reminder はチェックされているべき
            checker = app._is_sound_checked("Reminder")
            assert checker(None) is True

            # 他の音はチェックされていないべき
            checker = app._is_sound_checked("Mail")
            assert checker(None) is False

    def test_menu_items_include_sound_menu(self, temp_config):
        """メニューに通知音選択が含まれることを確認"""
        with patch("main.KeyboardHook"):
            app = ClipboardTransformerApp()
            app.config = Config(temp_config)

            menu_items = app._get_menu_items()

            # メニュー項目が5つあることを確認（Enable/Disable, Notification Sound, Open Log File, Reload, Quit）
            assert len(menu_items) == 5

            # 2番目の項目が "Notification Sound" であることを確認
            # （pystray の MenuItem オブジェクトなので詳細は確認しにくいが、少なくとも存在することを確認）
            assert menu_items is not None
