"""
constants.py のテスト

定数モジュールが正しくインポートでき、期待される値を持っていることを確認する
"""

from constants import (
    CLIPBOARD_RETRY_COUNT,
    CLIPBOARD_RETRY_DELAY,
    HOTKEY_CTRL_V,
    ICON_COLOR_DISABLED,
    ICON_COLOR_ENABLED,
    ICON_SIZE,
    ICON_TEXT,
    ICON_TEXT_COLOR,
    ICON_TEXT_POSITION,
    KEY_PRESS_DELAY,
    KEY_RELEASE_DELAY,
    LOG_FILE_BACKUP_COUNT,
    LOG_FILE_MAX_BYTES,
    LOG_FILE_PATH,
    MB_ICONINFORMATION,
    REGEX_TIMEOUT_SECONDS,
)


class TestConstants:
    """定数モジュールのテスト"""

    def test_clipboard_constants(self):
        """クリップボード関連定数が正しい値を持つ"""
        assert CLIPBOARD_RETRY_COUNT == 3
        assert CLIPBOARD_RETRY_DELAY == 0.05

    def test_keyboard_hook_constants(self):
        """キーボードフック関連定数が正しい値を持つ"""
        assert HOTKEY_CTRL_V == "ctrl+v"
        assert KEY_PRESS_DELAY == 0.01
        assert KEY_RELEASE_DELAY == 0.05

    def test_log_constants(self):
        """ログ関連定数が正しい値を持つ"""
        assert LOG_FILE_PATH == "clipboard-transformer.log"
        assert LOG_FILE_MAX_BYTES == 5 * 1024 * 1024  # 5MB
        assert LOG_FILE_BACKUP_COUNT == 3

    def test_icon_constants(self):
        """アイコン関連定数が正しい値を持つ"""
        assert ICON_SIZE == 64
        assert ICON_TEXT_POSITION == (10, 20)
        assert ICON_COLOR_ENABLED == "green"
        assert ICON_COLOR_DISABLED == "red"
        assert ICON_TEXT == "CT"
        assert ICON_TEXT_COLOR == "white"

    def test_windows_api_constants(self):
        """Windows API関連定数が正しい値を持つ"""
        assert MB_ICONINFORMATION == 0x40

    def test_regex_timeout_constant(self):
        """正規表現タイムアウト定数が正しい値を持つ"""
        assert REGEX_TIMEOUT_SECONDS == 2

    def test_all_constants_are_immutable_types(self):
        """すべての定数がイミュータブルな型である"""
        immutable_types = (int, float, str, tuple, bool)

        assert isinstance(CLIPBOARD_RETRY_COUNT, immutable_types)
        assert isinstance(CLIPBOARD_RETRY_DELAY, immutable_types)
        assert isinstance(HOTKEY_CTRL_V, immutable_types)
        assert isinstance(KEY_PRESS_DELAY, immutable_types)
        assert isinstance(KEY_RELEASE_DELAY, immutable_types)
        assert isinstance(LOG_FILE_PATH, immutable_types)
        assert isinstance(LOG_FILE_MAX_BYTES, immutable_types)
        assert isinstance(LOG_FILE_BACKUP_COUNT, immutable_types)
        assert isinstance(ICON_SIZE, immutable_types)
        assert isinstance(ICON_TEXT_POSITION, immutable_types)
        assert isinstance(ICON_COLOR_ENABLED, immutable_types)
        assert isinstance(ICON_COLOR_DISABLED, immutable_types)
        assert isinstance(ICON_TEXT, immutable_types)
        assert isinstance(ICON_TEXT_COLOR, immutable_types)
        assert isinstance(MB_ICONINFORMATION, immutable_types)
        assert isinstance(REGEX_TIMEOUT_SECONDS, immutable_types)
