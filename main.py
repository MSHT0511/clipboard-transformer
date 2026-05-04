"""
メインアプリケーション

システムトレイに常駐し、Ctrl+V でクリップボード変換を実行する。
"""

import ctypes
import logging
import os
import sys
import winreg
import winsound
from pathlib import Path

import pystray
import win32api
import win32event
import winerror
from PIL import Image, ImageDraw
from pystray import MenuItem

from clipboard_util import get_text, has_text, set_text
from config import Config
from hook import KeyboardHook
from transformer import Transformer

# Windows通知用
try:
    from winotify import Notification, audio

    NOTIFICATION_AVAILABLE = True
except ImportError:
    NOTIFICATION_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("winotify not available, notifications will be disabled")


# ログファイルのパス
LOG_FILE_PATH = "clipboard-transformer.log"

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(LOG_FILE_PATH, encoding="utf-8"), logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger(__name__)


class ClipboardTransformerApp:
    """クリップボード変換アプリケーションのメインクラス"""

    def __init__(self):
        self.config = Config()
        self.transformer = Transformer()
        self.hook = KeyboardHook(on_paste_callback=self._on_paste_detected)
        self.icon = None

        # 設定からルールをロード
        self._reload_rules()

    def _reload_rules(self):
        """設定ファイルからルールを再読み込み"""
        try:
            self.transformer.load_rules_from_config(self.config.get_rules())
            logger.info(f"Loaded {len(self.transformer.rules)} transformation rules")
        except Exception as e:
            logger.error(f"Failed to load rules: {e}")

    def _on_paste_detected(self) -> bool:
        """
        Ctrl+V 検知時のコールバック

        Returns:
            bool: 変換を実行した場合 True（元の Ctrl+V をブロック）
        """
        # 機能が無効の場合はスキップ
        if not self.config.is_enabled():
            logger.debug("Transformation disabled, skipping")
            return False

        # クリップボードにテキストが無い場合はスキップ
        if not has_text():
            logger.debug("No text in clipboard, skipping")
            return False

        # クリップボードからテキストを取得
        original_text = get_text()
        if not original_text:
            logger.debug("Empty clipboard text, skipping")
            return False

        # 変換を実行
        transformed_text = self.transformer.transform(original_text)

        # 変換結果が元のテキストと同じ場合はスキップ
        if transformed_text == original_text:
            logger.debug("No transformation applied, skipping")
            return False

        # 変換後のテキストをクリップボードにセット
        if not set_text(transformed_text):
            logger.error("Failed to set transformed text to clipboard")
            return False

        logger.info("Text transformed and pasted")

        # Windows 通知を表示
        try:
            if NOTIFICATION_AVAILABLE:
                toast = Notification(
                    app_id="Clipboard Transformer", title="変換完了", msg="テキストが変換されました", duration="short"
                )
                toast.set_audio(self._get_audio_sound(), loop=False)
                toast.show()
                logger.debug("Notification sent")
        except Exception as e:
            logger.error(f"Failed to show notification: {e}")

        # Ctrl+V をシミュレート
        self.hook.simulate_paste()

        return True

    def _create_icon_image(self, enabled=True):
        """システムトレイアイコン用の画像を生成"""
        # シンプルな 64x64 のアイコンを作成
        width = 64
        height = 64
        image = Image.new("RGB", (width, height), color="white")
        draw = ImageDraw.Draw(image)

        # 背景色を状態に応じて変更（有効=緑、無効=赤）
        color = "green" if enabled else "red"
        draw.rectangle([0, 0, width, height], fill=color)

        # "CT" の文字を描画（Clipboard Transformer）
        draw.text((10, 20), "CT", fill="white")

        return image

    def _on_toggle(self, icon, item):
        """有効/無効の切り替え"""
        logger.info("Toggle action triggered (left click or menu)")
        self.config.enabled = not self.config.enabled
        self.hook.set_enabled(self.config.enabled)
        status = "enabled" if self.config.enabled else "disabled"
        logger.info(f"Transformation {status}")
        icon.notify(f"Clipboard Transformer {status}", "Status Changed")
        # アイコンの画像を更新
        icon.icon = self._create_icon_image(self.config.enabled)
        # アイコンのメニューを更新
        icon.update_menu()

    def _get_audio_sound(self):
        """設定された通知音の audio オブジェクトを返す"""
        sound_name = self.config.notification_sound
        return getattr(audio, sound_name, audio.Default)

    def _on_sound_selected(self, sound_name):
        """通知音が選択された時のハンドラを返す"""

        def handler(icon, item):
            self.config.notification_sound = sound_name
            self.config.save()
            logger.info(f"Notification sound changed to: {sound_name}")

            # 選択時に自動プレビュー（Silentを除く）
            if sound_name != "Silent":
                self._play_preview_sound(sound_name)

            icon.update_menu()

        return handler

    def _is_sound_checked(self, sound_name):
        """通知音が選択中かどうかを返す"""

        def checker(item):
            return self.config.notification_sound == sound_name

        return checker

    def _play_preview_sound(self, sound_name):
        """指定されたシステム通知音をプレビュー再生する（通知を表示しない）"""
        sound_mapping = {
            "Default": ".Default",
            "IM": "Notification.IM",
            "Mail": "Notification.Mail",
            "Reminder": "Notification.Reminder",
            "SMS": "Notification.SMS",
        }

        registry_path = sound_mapping.get(sound_name, ".Default")

        try:
            # レジストリからサウンドファイルのパスを取得
            key_path = f"AppEvents\\Schemes\\Apps\\.Default\\{registry_path}\\.Current"
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path)
            sound_file, _ = winreg.QueryValueEx(key, "")
            winreg.CloseKey(key)

            if sound_file:
                # 非同期で再生（SND_ASYNC: アプリケーションをブロックしない）
                winsound.PlaySound(sound_file, winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_NODEFAULT)
                logger.debug(f"Playing preview sound: {sound_file}")
            else:
                logger.warning(f"No sound file found for {sound_name}")
                winsound.MessageBeep(winsound.MB_OK)
        except FileNotFoundError:
            logger.warning(f"Sound registry key not found for {sound_name}")
            winsound.MessageBeep(winsound.MB_OK)
        except Exception as e:
            logger.error(f"Error playing sound {sound_name}: {e}")
            winsound.MessageBeep(winsound.MB_OK)

    def _on_open_log(self, icon, item):
        """ログファイルを開く"""
        log_path = Path(LOG_FILE_PATH).resolve()
        try:
            if log_path.exists():
                os.startfile(str(log_path))
                logger.info(f"Opening log file: {log_path}")
            else:
                logger.warning(f"Log file not found: {log_path}")
                icon.notify("Log file not found", "Clipboard Transformer")
        except Exception as e:
            logger.error(f"Failed to open log file: {e}")
            icon.notify(f"Failed to open log file: {e}", "Clipboard Transformer")

    def _on_reload(self, icon, item):
        """設定の再読み込み"""
        logger.info("Reloading configuration...")
        self.config.reload()
        self._reload_rules()
        self.hook.set_enabled(self.config.is_enabled())
        icon.notify("Configuration reloaded", "Clipboard Transformer")

    def _on_quit(self, icon, item):
        """アプリケーションの終了"""
        logger.info("Quitting application...")
        icon.stop()
        self.hook.stop()

    def _get_menu_items(self):
        """システムトレイのメニュー項目を生成"""
        # サウンドメニューの項目を生成（選択時に自動プレビュー）
        sound_items = [
            MenuItem(
                sound_name, self._on_sound_selected(sound_name), checked=self._is_sound_checked(sound_name), radio=True
            )
            for sound_name in Config.VALID_SOUNDS
        ]

        sound_menu = pystray.Menu(*sound_items)

        return (
            MenuItem(
                lambda text: f"{'Disable' if self.config.enabled else 'Enable'} Transformation",
                self._on_toggle,
                default=True,
            ),
            MenuItem("Notification Sound", sound_menu),
            MenuItem("Open Log File", self._on_open_log),
            MenuItem("Reload Config", self._on_reload),
            MenuItem("Quit", self._on_quit),
        )

    def run(self):
        """アプリケーションを起動"""
        logger.info("Starting Clipboard Transformer...")

        # 設定ファイルが無い場合はサンプルを作成
        if not Path("config.json").exists():
            logger.info("Config file not found, creating sample config...")
            self.config.save_default_config()
            self.config.reload()
            self._reload_rules()

        # キーボードフックを開始
        self.hook.start()

        # システムトレイアイコンを作成
        icon_image = self._create_icon_image(self.config.enabled)
        self.icon = pystray.Icon(
            "clipboard_transformer", icon_image, "Clipboard Transformer", menu=pystray.Menu(self._get_menu_items)
        )

        logger.info("Application started successfully")

        # アイコンを表示（これがメインループになる）
        self.icon.run()

        logger.info("Application stopped")


def main():
    """エントリポイント"""
    # ミューテックスを作成して重複起動を防ぐ
    mutex_name = "Global\\ClipboardTransformer_SingleInstance"
    mutex = None

    try:
        # ミューテックスを作成
        mutex = win32event.CreateMutex(None, False, mutex_name)
        last_error = win32api.GetLastError()

        # 既にミューテックスが存在する場合（既に起動している）
        if last_error == winerror.ERROR_ALREADY_EXISTS:
            logger.warning("Application is already running")
            # メッセージボックスを表示
            ctypes.windll.user32.MessageBoxW(
                0,
                "Clipboard Transformer は既に起動しています。\n\nシステムトレイのアイコンを確認してください。",
                "Clipboard Transformer",
                0x40,  # MB_ICONINFORMATION
            )
            sys.exit(1)

        logger.info("Single instance mutex created successfully")

        app = ClipboardTransformerApp()
        app.run()
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.exception(f"Fatal error: {e}")
        sys.exit(1)
    finally:
        # ミューテックスを解放
        if mutex:
            win32api.CloseHandle(mutex)


if __name__ == "__main__":
    main()
