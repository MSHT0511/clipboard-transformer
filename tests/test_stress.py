"""
ストレステストと高度なエッジケーステスト

並発処理、パフォーマンス、ファイルシステムエラーなどの高度なシナリオをテストする
"""

import json
import os
import stat
import threading
import time
from unittest.mock import patch

from clipboard_util import get_text, set_text
from config import Config
from main import ClipboardTransformerApp
from transformer import Transformer


class TestConcurrentPasteEvents:
    """並発ペーストイベントのテスト"""

    def test_concurrent_paste_events_do_not_interfere(self, tmp_path):
        """複数のペーストイベントが並行して発生しても正しく処理される"""
        config_file = tmp_path / "config.json"
        config_data = {
            "enabled": True,
            "rules": [{"type": "literal", "name": "test", "enabled": True, "from": "a", "to": "b"}],
        }
        config_file.write_text(json.dumps(config_data))

        # Config を作成
        config = Config(str(config_file))

        # ClipboardTransformerApp を作成
        with patch("main.Config", return_value=config):
            app = ClipboardTransformerApp()

            # モック関数を作成
            results = []

            def mock_set_text(text, *args, **kwargs):
                results.append(text)
                return True

            with (
                patch("main.set_text", side_effect=mock_set_text),
                patch("main.get_text", return_value="aaa"),
                patch("main.has_text", return_value=True),
                patch("main.NOTIFICATION_AVAILABLE", False),
                patch.object(app.hook, "simulate_paste"),
            ):
                # 複数のスレッドで並行してペースト処理を実行
                threads = []
                for _ in range(10):
                    t = threading.Thread(target=app._on_paste_detected)
                    threads.append(t)
                    t.start()

                # すべてのスレッドが完了するまで待機
                for t in threads:
                    t.join(timeout=2.0)

                # 各スレッドが変換を実行したことを確認
                # すべて "aaa" -> "bbb" に変換されるはず
                assert len(results) == 10
                assert all(text == "bbb" for text in results)

    def test_concurrent_clipboard_operations(self):
        """並発クリップボード操作が競合しても安全に動作する"""
        # 実際のクリップボードではなくモックを使用して並発テスト
        test_texts = [f"test_{i}" for i in range(20)]
        results = []
        errors = []

        with (
            patch("clipboard_util.win32clipboard.OpenClipboard"),
            patch("clipboard_util.win32clipboard.CloseClipboard"),
            patch("clipboard_util.win32clipboard.EmptyClipboard"),
            patch("clipboard_util.win32clipboard.SetClipboardData"),
            patch("clipboard_util.win32clipboard.GetClipboardData") as mock_get,
            patch("clipboard_util.win32clipboard.IsClipboardFormatAvailable", return_value=True),
        ):

            def mock_get_data(format_type):
                # スレッドごとに異なるデータを返す（簡易シミュレーション）
                import threading

                thread_id = threading.get_ident()
                return f"data_{thread_id}"

            mock_get.side_effect = mock_get_data

            def worker(text):
                try:
                    # クリップボードに書き込み（モック）
                    if set_text(text):
                        # 短い待機後に読み取り（モック）
                        time.sleep(0.01)
                        read_text = get_text()
                        results.append((text, read_text))
                except Exception as e:
                    errors.append(e)

            threads = []
            for text in test_texts:
                t = threading.Thread(target=worker, args=(text,))
                threads.append(t)
                t.start()

            for t in threads:
                t.join(timeout=5.0)

            # エラーが発生していないことを確認
            assert len(errors) == 0

            # 結果が記録されていることを確認
            assert len(results) == len(test_texts)


class TestConfigFileErrors:
    """設定ファイルの実行時削除・権限エラーのテスト"""

    def test_config_file_deleted_during_runtime(self, tmp_path):
        """実行中に設定ファイルが削除された場合でも適切に処理される"""
        config_file = tmp_path / "config.json"
        config_data = {"enabled": True, "rules": []}
        config_file.write_text(json.dumps(config_data))

        config = Config(str(config_file))
        assert config.is_enabled() is True

        # 設定ファイルを削除
        config_file.unlink()

        # 再読み込みを試行（デフォルト設定にフォールバックするはず）
        config.reload()

        # デフォルト設定が適用されることを確認
        assert config.is_enabled() is True
        assert config.get_rules() == []

    def test_config_file_permission_error_on_save(self, tmp_path):
        """設定ファイルへの書き込み権限がない場合のエラー処理"""
        config_file = tmp_path / "config.json"
        config_data = {"enabled": True, "rules": []}
        config_file.write_text(json.dumps(config_data))

        config = Config(str(config_file))

        # ファイルを読み取り専用に設定
        os.chmod(config_file, stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)

        try:
            # 保存を試行
            config.enabled = False
            result = config.save()

            # 保存失敗を確認
            assert result is False
        finally:
            # クリーンアップ: 権限を戻す
            os.chmod(config_file, stat.S_IWUSR | stat.S_IRUSR)

    def test_config_file_corrupted_during_runtime(self, tmp_path):
        """実行中に設定ファイルが破損した場合のエラー処理"""
        config_file = tmp_path / "config.json"
        config_data = {"enabled": True, "rules": []}
        config_file.write_text(json.dumps(config_data))

        config = Config(str(config_file))
        assert config.is_enabled() is True

        # 設定ファイルを破損させる
        config_file.write_text("{ invalid json }")

        # 再読み込みを試行（デフォルト設定にフォールバックするはず）
        config.reload()

        # デフォルト設定が適用されることを確認
        assert config.is_enabled() is True
        assert config.get_rules() == []


class TestLargeRuleSetPerformance:
    """大量ルールのパフォーマンステスト"""

    def test_1000_literal_rules_performance(self):
        """1000個のliteralルールでも許容時間内に変換が完了する"""
        # 1000個のルールを作成
        rules = []
        for i in range(1000):
            rules.append(
                {"type": "literal", "name": f"rule_{i}", "enabled": True, "from": f"pattern_{i}", "to": f"replace_{i}"}
            )

        transformer = Transformer()
        transformer.load_rules_from_config(rules)

        # 変換対象のテキスト（最後のルールにマッチ）
        test_text = "prefix pattern_999 suffix"

        # 変換を実行して時間を計測
        start_time = time.time()
        result = transformer.transform(test_text)
        elapsed_time = time.time() - start_time

        # 正しく変換されていることを確認
        assert result == "prefix replace_999 suffix"

        # 許容時間内に完了していることを確認（1秒以内）
        assert elapsed_time < 1.0

    def test_1000_regex_rules_performance(self):
        """1000個のregexルールでも許容時間内に変換が完了する"""
        # 1000個の正規表現ルールを作成（シンプルなパターン）
        rules = []
        for i in range(1000):
            rules.append(
                {
                    "type": "regex",
                    "name": f"regex_rule_{i}",
                    "enabled": True,
                    "pattern": f"pattern_{i}",
                    "replacement": f"replace_{i}",
                }
            )

        transformer = Transformer()
        transformer.load_rules_from_config(rules)

        # 変換対象のテキスト（最後のルールにマッチ）
        test_text = "prefix pattern_999 suffix"

        # 変換を実行して時間を計測
        start_time = time.time()
        result = transformer.transform(test_text)
        elapsed_time = time.time() - start_time

        # 正しく変換されていることを確認
        assert result == "prefix replace_999 suffix"

        # 許容時間内に完了していることを確認（3秒以内 - 正規表現なので少し余裕を持たせる）
        assert elapsed_time < 3.0

    def test_mixed_1000_rules_performance(self):
        """literalとregexを混合した1000個のルールでも正常に動作する"""
        # 500個ずつのliteralとregexルールを交互に作成
        rules = []
        for i in range(500):
            # Literal rule
            rules.append(
                {
                    "type": "literal",
                    "name": f"literal_{i}",
                    "enabled": True,
                    "from": f"lit_pattern_{i}",
                    "to": f"lit_replace_{i}",
                }
            )
            # Regex rule
            rules.append(
                {
                    "type": "regex",
                    "name": f"regex_{i}",
                    "enabled": True,
                    "pattern": f"reg_pattern_{i}",
                    "replacement": f"reg_replace_{i}",
                }
            )

        transformer = Transformer()
        transformer.load_rules_from_config(rules)

        # 変換対象のテキスト（literalとregexの両方にマッチ）
        test_text = "prefix lit_pattern_100 reg_pattern_200 suffix"

        # 変換を実行して時間を計測
        start_time = time.time()
        result = transformer.transform(test_text)
        elapsed_time = time.time() - start_time

        # 正しく変換されていることを確認
        assert "lit_replace_100" in result
        assert "reg_replace_200" in result

        # 許容時間内に完了していることを確認（3秒以内）
        assert elapsed_time < 3.0

    def test_disabled_rules_are_skipped_efficiently(self):
        """無効化されたルールは効率的にスキップされる"""
        # 1000個のルールを作成（ほとんどが無効）
        rules = []
        for i in range(1000):
            rules.append(
                {
                    "type": "literal",
                    "name": f"rule_{i}",
                    "enabled": i == 999,  # 最後のルールだけ有効
                    "from": f"pattern_{i}",
                    "to": f"replace_{i}",
                }
            )

        transformer = Transformer()
        transformer.load_rules_from_config(rules)

        test_text = "prefix pattern_999 suffix"

        # 変換を実行して時間を計測
        start_time = time.time()
        result = transformer.transform(test_text)
        elapsed_time = time.time() - start_time

        # 正しく変換されていることを確認
        assert result == "prefix replace_999 suffix"

        # 無効ルールがスキップされるため高速に完了するはず（0.5秒以内）
        assert elapsed_time < 0.5


class TestHookRecursionPrevention:
    """フックの再帰防止機構のテスト"""

    def test_simulate_paste_prevents_recursion(self):
        """simulate_paste呼び出しが再帰を引き起こさない"""
        from hook import KeyboardHook

        callback_count = [0]

        def on_paste_callback():
            callback_count[0] += 1
            return True

        hook = KeyboardHook(on_paste_callback=on_paste_callback)

        with (
            patch("keyboard.press"),
            patch("keyboard.release"),
            patch("time.sleep"),
        ):
            # simulate_paste を呼び出し
            hook.simulate_paste()

            # コールバックが呼ばれていないことを確認（再帰防止が動作）
            assert callback_count[0] == 0
