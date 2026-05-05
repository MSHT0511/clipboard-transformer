"""
キーボードフック処理

keyboard ライブラリを使用して Ctrl+V を検知し、
クリップボードの変換を行ってからペーストする。
再帰防止フラグで自己シミュレート分をスキップする。
"""

import logging
import time
from collections.abc import Callable

import keyboard

logger = logging.getLogger(__name__)

# 定数
HOTKEY_CTRL_V = "ctrl+v"
KEY_PRESS_DELAY = 0.01  # キープレス後の待機時間（秒）
KEY_RELEASE_DELAY = 0.05  # キーリリース後の待機時間（秒）


class KeyboardHook:
    """Ctrl+V をフックして変換処理を実行するクラス"""

    def __init__(self, on_paste_callback: Callable[[], bool] | None = None):
        """
        Args:
            on_paste_callback: Ctrl+V 検知時に呼ばれるコールバック関数。
                               変換を実行して True を返すと、元の Ctrl+V をブロック。
                               False を返すと、元の Ctrl+V をそのまま実行。
        """
        self.on_paste_callback = on_paste_callback
        self.enabled = True
        self._prevent_recursion = False
        self._hook_active = False

    def start(self):
        """フックを開始"""
        if self._hook_active:
            logger.warning("Hook is already active")
            return

        try:
            # Ctrl+V のホットキーを登録（suppress=True で元のイベントを抑制）
            keyboard.add_hotkey(HOTKEY_CTRL_V, self._on_hotkey_triggered, suppress=True)
            self._hook_active = True
            logger.info("Keyboard hook started")

        except Exception as e:
            logger.error(f"Failed to start keyboard hook: {e}")

    def stop(self):
        """フックを停止"""
        if not self._hook_active:
            return

        try:
            keyboard.unhook_all()
            self._hook_active = False
            logger.info("Keyboard hook stopped")

        except Exception as e:
            logger.error(f"Failed to stop keyboard hook: {e}")

    def _on_hotkey_triggered(self):
        """Ctrl+V ホットキーが押された時のハンドラ"""
        # 再帰防止: 自分でシミュレートした Ctrl+V はスキップ
        if self._prevent_recursion:
            return

        # 機能が無効の場合はスキップ
        if not self.enabled:
            # 機能が無効の時は元のCtrl+Vを実行
            self.simulate_paste()
            return

        logger.debug("Ctrl+V detected")

        # コールバックを実行
        if self.on_paste_callback:
            try:
                # コールバックが False を返したら、元のCtrl+Vを実行
                if not self.on_paste_callback():
                    self.simulate_paste()

            except Exception as e:
                logger.error(f"Error in paste callback: {e}")

    def simulate_paste(self):
        """
        Ctrl+V をシミュレートする（再帰防止フラグ付き）
        """
        try:
            self._prevent_recursion = True

            # Ctrl+V を送信
            keyboard.press("ctrl")
            keyboard.press("v")
            time.sleep(KEY_PRESS_DELAY)
            keyboard.release("v")
            keyboard.release("ctrl")

            # 短い待機時間を置いてからフラグを解除
            time.sleep(KEY_RELEASE_DELAY)

        except Exception as e:
            logger.error(f"Failed to simulate paste: {e}")

        finally:
            self._prevent_recursion = False

    def set_enabled(self, enabled: bool):
        """フックの有効/無効を切り替え"""
        self.enabled = enabled
        logger.info(f"Keyboard hook {'enabled' if enabled else 'disabled'}")
