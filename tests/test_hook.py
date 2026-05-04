"""
KeyboardHook クラスのテスト

keyboard ライブラリをモックして、フック処理のロジックをテストする。
"""

from unittest.mock import Mock, patch

from hook import KeyboardHook


class TestKeyboardHookInit:
    """KeyboardHook の初期化テスト"""

    def test_init_without_callback(self):
        """コールバックなしで初期化"""
        hook = KeyboardHook()
        assert hook.on_paste_callback is None
        assert hook.enabled is True
        assert hook._prevent_recursion is False
        assert hook._hook_active is False

    def test_init_with_callback(self):
        """コールバックありで初期化"""
        callback = Mock()
        hook = KeyboardHook(on_paste_callback=callback)
        assert hook.on_paste_callback is callback
        assert hook.enabled is True
        assert hook._prevent_recursion is False
        assert hook._hook_active is False


class TestKeyboardHookStartStop:
    """start() と stop() のテスト"""

    @patch("hook.keyboard")
    def test_start_hook(self, mock_keyboard):
        """フックを開始"""
        hook = KeyboardHook()
        hook.start()

        # keyboard.add_hotkey が呼ばれたか
        mock_keyboard.add_hotkey.assert_called_once_with("ctrl+v", hook._on_hotkey_triggered, suppress=True)
        assert hook._hook_active is True

    @patch("hook.keyboard")
    def test_start_hook_already_active(self, mock_keyboard):
        """既に開始済みのフックを再度開始"""
        hook = KeyboardHook()
        hook._hook_active = True

        hook.start()

        # add_hotkey は呼ばれない
        mock_keyboard.add_hotkey.assert_not_called()

    @patch("hook.keyboard")
    def test_start_hook_error(self, mock_keyboard):
        """フック開始時にエラーが発生"""
        mock_keyboard.add_hotkey.side_effect = Exception("Test error")
        hook = KeyboardHook()

        # エラーが発生してもクラッシュしない
        hook.start()
        assert hook._hook_active is False

    @patch("hook.keyboard")
    def test_stop_hook(self, mock_keyboard):
        """フックを停止"""
        hook = KeyboardHook()
        hook._hook_active = True

        hook.stop()

        # keyboard.unhook_all が呼ばれたか
        mock_keyboard.unhook_all.assert_called_once()
        assert hook._hook_active is False

    @patch("hook.keyboard")
    def test_stop_hook_not_active(self, mock_keyboard):
        """未開始のフックを停止"""
        hook = KeyboardHook()
        hook._hook_active = False

        hook.stop()

        # unhook_all は呼ばれない
        mock_keyboard.unhook_all.assert_not_called()

    @patch("hook.keyboard")
    def test_stop_hook_error(self, mock_keyboard):
        """フック停止時にエラーが発生"""
        mock_keyboard.unhook_all.side_effect = Exception("Test error")
        hook = KeyboardHook()
        hook._hook_active = True

        # エラーが発生してもクラッシュしない
        hook.stop()
        # エラーが発生した場合、_hook_activeは変更されない（現在の実装）
        assert hook._hook_active is True


class TestKeyboardHookHotkeyTriggered:
    """_on_hotkey_triggered() のテスト"""

    @patch("hook.keyboard")
    def test_hotkey_triggered_with_recursion_flag(self, mock_keyboard):
        """再帰防止フラグがTrueのときはスキップ"""
        callback = Mock()
        hook = KeyboardHook(on_paste_callback=callback)
        hook._prevent_recursion = True

        hook._on_hotkey_triggered()

        # コールバックは呼ばれない
        callback.assert_not_called()
        # keyboardも操作しない
        mock_keyboard.press.assert_not_called()

    @patch("hook.keyboard")
    @patch("hook.time.sleep")
    def test_hotkey_triggered_when_disabled(self, mock_sleep, mock_keyboard):
        """enabledがFalseのときは元のCtrl+Vをパススルー"""
        callback = Mock()
        hook = KeyboardHook(on_paste_callback=callback)
        hook.enabled = False

        hook._on_hotkey_triggered()

        # コールバックは呼ばれない
        callback.assert_not_called()

        # 元のCtrl+Vをシミュレート
        assert mock_keyboard.press.call_count == 2
        assert mock_keyboard.release.call_count == 2
        mock_keyboard.press.assert_any_call("ctrl")
        mock_keyboard.press.assert_any_call("v")
        mock_keyboard.release.assert_any_call("v")
        mock_keyboard.release.assert_any_call("ctrl")

    @patch("hook.keyboard")
    def test_hotkey_triggered_callback_returns_true(self, mock_keyboard):
        """コールバックがTrueを返す（変換が実行された）"""
        callback = Mock(return_value=True)
        hook = KeyboardHook(on_paste_callback=callback)

        hook._on_hotkey_triggered()

        # コールバックが呼ばれた
        callback.assert_called_once()

        # keyboardは操作しない（コールバックがTrueなので）
        mock_keyboard.press.assert_not_called()
        mock_keyboard.release.assert_not_called()

    @patch("hook.keyboard")
    @patch("hook.time.sleep")
    def test_hotkey_triggered_callback_returns_false(self, mock_sleep, mock_keyboard):
        """コールバックがFalseを返す（変換が実行されなかった）"""
        callback = Mock(return_value=False)
        hook = KeyboardHook(on_paste_callback=callback)

        hook._on_hotkey_triggered()

        # コールバックが呼ばれた
        callback.assert_called_once()

        # 元のCtrl+Vをシミュレート
        assert mock_keyboard.press.call_count == 2
        assert mock_keyboard.release.call_count == 2

    @patch("hook.keyboard")
    def test_hotkey_triggered_callback_raises_error(self, mock_keyboard):
        """コールバックでエラーが発生"""
        callback = Mock(side_effect=Exception("Test error"))
        hook = KeyboardHook(on_paste_callback=callback)

        # エラーが発生してもクラッシュしない
        hook._on_hotkey_triggered()

        callback.assert_called_once()

    def test_hotkey_triggered_no_callback(self):
        """コールバックがNoneの場合"""
        hook = KeyboardHook(on_paste_callback=None)

        # エラーが発生せず、何もしない
        hook._on_hotkey_triggered()


class TestKeyboardHookSimulatePaste:
    """simulate_paste() のテスト"""

    @patch("hook.keyboard")
    @patch("hook.time.sleep")
    def test_simulate_paste(self, mock_sleep, mock_keyboard):
        """ペーストをシミュレート"""
        hook = KeyboardHook()

        hook.simulate_paste()

        # Ctrl+Vのキー操作がシミュレートされた
        assert mock_keyboard.press.call_count == 2
        assert mock_keyboard.release.call_count == 2
        mock_keyboard.press.assert_any_call("ctrl")
        mock_keyboard.press.assert_any_call("v")
        mock_keyboard.release.assert_any_call("v")
        mock_keyboard.release.assert_any_call("ctrl")

        # 再帰防止フラグが最終的にFalseに戻る
        assert hook._prevent_recursion is False

    @patch("hook.keyboard")
    @patch("hook.time.sleep")
    def test_simulate_paste_sets_recursion_flag(self, mock_sleep, mock_keyboard):
        """simulate_paste() 実行中は再帰防止フラグがTrue"""
        hook = KeyboardHook()

        # keyboard.press が呼ばれたときにフラグをチェック
        def check_flag_on_press(key):
            if key == "v":
                assert hook._prevent_recursion is True

        mock_keyboard.press.side_effect = check_flag_on_press

        hook.simulate_paste()

        # 最終的にフラグはFalseに戻る
        assert hook._prevent_recursion is False

    @patch("hook.keyboard")
    @patch("hook.time.sleep")
    def test_simulate_paste_error_recovery(self, mock_sleep, mock_keyboard):
        """エラーが発生しても再帰防止フラグがリセットされる"""
        hook = KeyboardHook()
        mock_keyboard.press.side_effect = Exception("Test error")

        # エラーが発生してもクラッシュしない
        hook.simulate_paste()

        # フラグは必ずFalseに戻る（finallyブロック）
        assert hook._prevent_recursion is False


class TestKeyboardHookSetEnabled:
    """set_enabled() のテスト"""

    def test_set_enabled_true(self):
        """有効に設定"""
        hook = KeyboardHook()
        hook.enabled = False

        hook.set_enabled(True)

        assert hook.enabled is True

    def test_set_enabled_false(self):
        """無効に設定"""
        hook = KeyboardHook()
        hook.enabled = True

        hook.set_enabled(False)

        assert hook.enabled is False


class TestKeyboardHookIntegration:
    """統合的なシナリオテスト"""

    @patch("hook.keyboard")
    @patch("hook.time.sleep")
    def test_recursion_prevention_during_callback(self, mock_sleep, mock_keyboard):
        """コールバック内でシミュレートした場合、再帰が防がれる"""

        def callback_that_simulates():
            hook.simulate_paste()
            return True

        hook = KeyboardHook(on_paste_callback=callback_that_simulates)

        # 最初のトリガー
        hook._on_hotkey_triggered()

        # simulate_paste() が呼ばれ、その中でキーボード操作が行われた
        assert mock_keyboard.press.call_count >= 2

        # 再帰は防がれた（_prevent_recursionフラグが機能）
        assert hook._prevent_recursion is False

    @patch("hook.keyboard")
    def test_enable_disable_cycle(self, mock_keyboard):
        """有効化→無効化→有効化のサイクル"""
        callback = Mock(return_value=True)
        hook = KeyboardHook(on_paste_callback=callback)

        # 有効状態でトリガー
        hook.set_enabled(True)
        hook._on_hotkey_triggered()
        assert callback.call_count == 1

        # 無効化してトリガー
        hook.set_enabled(False)
        callback.reset_mock()
        mock_keyboard.reset_mock()
        hook._on_hotkey_triggered()
        assert callback.call_count == 0  # コールバックは呼ばれない
        assert mock_keyboard.press.call_count > 0  # パススルー

        # 再度有効化してトリガー
        hook.set_enabled(True)
        callback.reset_mock()
        mock_keyboard.reset_mock()
        hook._on_hotkey_triggered()
        assert callback.call_count == 1
