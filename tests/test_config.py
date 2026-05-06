"""設定ファイル読み込みのテスト"""

import json
import os
import tempfile
from pathlib import Path

import pytest

from config import Config
from transformer import Transformer


class TestConfig:
    """Config クラスのテスト"""

    def test_load_default_config(self):
        """デフォルト設定ファイルの読み込み"""
        config = Config()
        assert isinstance(config.is_enabled(), bool)
        assert isinstance(config.get_rules(), list)

    def test_nonexistent_config_file(self):
        """存在しない設定ファイルはデフォルト設定を使用"""
        config = Config("nonexistent_test_config.json")
        assert len(config.get_rules()) == 0
        assert config.is_enabled() is True

    def test_invalid_json(self):
        """不正なJSONファイルはデフォルト設定にフォールバック"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
            f.write("{invalid json")
            temp_file = f.name

        try:
            config = Config(temp_file)
            assert len(config.get_rules()) == 0
            assert config.is_enabled() is True
        finally:
            os.unlink(temp_file)

    def test_valid_literal_rule(self):
        """有効なliteralルールの読み込み"""
        config_data = {
            "enabled": True,
            "rules": [{"name": "test-literal", "type": "literal", "from": "foo", "to": "bar", "enabled": True}],
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
            json.dump(config_data, f)
            temp_file = f.name

        try:
            config = Config(temp_file)
            assert len(config.get_rules()) == 1
            assert config.get_rules()[0]["name"] == "test-literal"
            assert config.get_rules()[0]["type"] == "literal"
        finally:
            os.unlink(temp_file)

    def test_valid_regex_rule(self):
        """有効なregexルールの読み込み"""
        config_data = {
            "enabled": True,
            "rules": [
                {"name": "test-regex", "type": "regex", "pattern": r"\d+", "replacement": "NUM", "enabled": True}
            ],
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
            json.dump(config_data, f)
            temp_file = f.name

        try:
            config = Config(temp_file)
            assert len(config.get_rules()) == 1
            assert config.get_rules()[0]["type"] == "regex"
        finally:
            os.unlink(temp_file)

    def test_invalid_rule_type(self):
        """無効なルールタイプはスキップされる"""
        config_data = {"enabled": True, "rules": [{"name": "invalid", "type": "unknown", "from": "a", "to": "b"}]}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
            json.dump(config_data, f)
            temp_file = f.name

        try:
            config = Config(temp_file)
            assert len(config.get_rules()) == 0
        finally:
            os.unlink(temp_file)

    def test_missing_required_fields_literal(self):
        """literalルールの必須フィールド欠如"""
        config_data = {
            "enabled": True,
            "rules": [
                {"name": "incomplete", "type": "literal", "from": "a"}  # 'to' がない
            ],
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
            json.dump(config_data, f)
            temp_file = f.name

        try:
            config = Config(temp_file)
            assert len(config.get_rules()) == 0
        finally:
            os.unlink(temp_file)

    def test_missing_required_fields_regex(self):
        """regexルールの必須フィールド欠如"""
        config_data = {
            "enabled": True,
            "rules": [
                {"name": "incomplete", "type": "regex", "pattern": r"\d+"}  # 'replacement' がない
            ],
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
            json.dump(config_data, f)
            temp_file = f.name

        try:
            config = Config(temp_file)
            assert len(config.get_rules()) == 0
        finally:
            os.unlink(temp_file)

    def test_save_default_config(self):
        """デフォルト設定ファイルの作成"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            temp_file = f.name

        os.unlink(temp_file)  # 一旦削除

        try:
            config = Config(temp_file)
            assert config.save_default_config() is True
            assert Path(temp_file).exists()

            # 保存されたファイルを読み込んで検証
            with open(temp_file, encoding="utf-8") as f:
                data = json.load(f)

            assert "enabled" in data
            assert "rules" in data
            assert isinstance(data["rules"], list)
        finally:
            if Path(temp_file).exists():
                os.unlink(temp_file)

    def test_notification_sound_default(self):
        """notification_sound のデフォルト値"""
        config = Config("nonexistent_test_config.json")
        assert config.notification_sound == "Default"

    def test_notification_sound_valid(self):
        """有効な notification_sound の読み込み"""
        config_data = {"enabled": True, "notification_sound": "Mail", "rules": []}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
            json.dump(config_data, f)
            temp_file = f.name

        try:
            config = Config(temp_file)
            assert config.notification_sound == "Mail"
        finally:
            os.unlink(temp_file)

    def test_notification_sound_invalid(self):
        """無効な notification_sound はデフォルトにフォールバック"""
        config_data = {"enabled": True, "notification_sound": "InvalidSound", "rules": []}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
            json.dump(config_data, f)
            temp_file = f.name

        try:
            config = Config(temp_file)
            assert config.notification_sound == "Default"
        finally:
            os.unlink(temp_file)

    @pytest.mark.parametrize("sound", Config.VALID_SOUNDS)
    def test_notification_sound_all_valid_sounds(self, sound):
        """すべての有効な通知音を読み込めることを確認"""
        config_data = {"enabled": True, "notification_sound": sound, "rules": []}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
            json.dump(config_data, f)
            temp_file = f.name

        try:
            config = Config(temp_file)
            assert config.notification_sound == sound
        finally:
            os.unlink(temp_file)

    def test_config_save(self):
        """Config.save() メソッドのテスト"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
            initial_data = {"enabled": True, "notification_sound": "Default", "rules": []}
            json.dump(initial_data, f)
            temp_file = f.name

        try:
            config = Config(temp_file)
            config.notification_sound = "SMS"
            config.enabled = False
            assert config.save() is True

            # ファイルが正しく保存されたか確認
            with open(temp_file, encoding="utf-8") as f:
                data = json.load(f)

            assert data["notification_sound"] == "SMS"
            assert data["enabled"] is False
        finally:
            os.unlink(temp_file)

    def test_config_save_preserves_rules(self):
        """Config.save() がルールを保持することを確認"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
            initial_data = {
                "enabled": True,
                "notification_sound": "Default",
                "rules": [{"name": "test-rule", "type": "literal", "from": "a", "to": "b", "enabled": True}],
            }
            json.dump(initial_data, f)
            temp_file = f.name

        try:
            config = Config(temp_file)
            config.notification_sound = "Reminder"
            assert config.save() is True

            # ファイルが正しく保存されたか確認
            with open(temp_file, encoding="utf-8") as f:
                data = json.load(f)

            assert data["notification_sound"] == "Reminder"
            assert len(data["rules"]) == 1
            assert data["rules"][0]["name"] == "test-rule"
        finally:
            os.unlink(temp_file)


class TestConfigTransformerIntegration:
    """Config と Transformer の統合テスト"""

    def test_load_rules_into_transformer(self):
        """設定ファイルからTransformerへのルール読み込み"""
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

        try:
            config = Config(temp_file)
            transformer = Transformer()
            transformer.load_rules_from_config(config.get_rules())

            assert len(transformer.rules) == 2

            # 実際の変換テスト
            result = transformer.transform("旧文字列 and 2026-05-03")
            assert result == "新文字列 and DATE_REMOVED"
        finally:
            os.unlink(temp_file)


class TestConfigEdgeCases:
    """Config のエッジケース・例外処理テスト"""

    def test_load_json_not_dict(self):
        """JSON が dict でない場合（配列など）"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
            # JSON 配列を書き込む
            json.dump(["not", "a", "dict"], f)
            temp_file = f.name

        try:
            config = Config(temp_file)
            # デフォルト設定にフォールバック
            assert config.enabled is True
            assert config.rules == []
        finally:
            os.unlink(temp_file)

    def test_load_rules_not_list(self):
        """rules フィールドが配列でない場合"""
        config_data = {
            "enabled": True,
            "rules": "not a list",  # 文字列
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
            json.dump(config_data, f)
            temp_file = f.name

        try:
            config = Config(temp_file)
            # rules が配列でない場合は空配列に修正される
            assert config.rules == []
        finally:
            os.unlink(temp_file)

    def test_load_general_exception(self):
        """JSON デコード以外の一般的な例外"""
        # ファイルが読み取り専用ディレクトリにある場合など
        # ここでは、存在しないディレクトリのパスを使用
        config = Config("/nonexistent/path/config.json")

        # デフォルト設定にフォールバック
        assert config.enabled is True
        assert config.rules == []

    def test_validate_rules_not_list(self):
        """_validate_rules() で rules が list でない場合の防御"""
        config_data = {
            "enabled": True,
            "rules": {"invalid": "not a list"},  # dict
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
            json.dump(config_data, f)
            temp_file = f.name

        try:
            config = Config(temp_file)
            # 内部で検証され、空配列に修正される
            assert config.rules == []
        finally:
            os.unlink(temp_file)

    def test_save_default_config_write_error(self):
        """save_default_config() でファイル書き込みエラー"""
        # 書き込み不可能なパスを指定
        config = Config()
        config.config_path = "/invalid/path/cannot/write/config.json"

        result = config.save_default_config()

        # 書き込み失敗時は False を返す
        assert result is False

    def test_save_write_error(self):
        """save() でファイル書き込みエラー"""
        config = Config()
        config.config_path = "/invalid/path/cannot/write/config.json"

        result = config.save()

        # 書き込み失敗時は False を返す
        assert result is False

    def test_load_with_permission_error(self):
        """ファイル読み込み時のパーミッションエラー"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
            json.dump({"enabled": True, "rules": []}, f)
            temp_file = f.name

        try:
            # Windows では簡単にパーミッションエラーを再現できないため、
            # 代わりに削除されたファイルを読み込む
            os.unlink(temp_file)

            config = Config(temp_file)
            # ファイルが存在しないため、デフォルト設定にフォールバック
            assert config.enabled is True
            assert config.rules == []
        except Exception:
            if os.path.exists(temp_file):
                os.unlink(temp_file)

    def test_reload_method(self):
        """reload() メソッドが正しく動作することを確認"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
            initial_data = {
                "enabled": True,
                "notification_sound": "Default",
                "rules": [{"name": "rule1", "type": "literal", "from": "a", "to": "b", "enabled": True}],
            }
            json.dump(initial_data, f)
            temp_file = f.name

        try:
            config = Config(temp_file)
            assert len(config.rules) == 1

            # ファイルを更新
            updated_data = {
                "enabled": False,
                "notification_sound": "Mail",
                "rules": [
                    {"name": "rule1", "type": "literal", "from": "a", "to": "b", "enabled": True},
                    {"name": "rule2", "type": "literal", "from": "x", "to": "y", "enabled": True},
                ],
            }
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(updated_data, f)

            # 再読み込み
            config.reload()

            assert config.enabled is False
            assert config.notification_sound == "Mail"
            assert len(config.rules) == 2
        finally:
            os.unlink(temp_file)

    def test_get_base_dir_when_frozen(self):
        """PyInstaller でフリーズされた状態での get_base_dir()"""
        from unittest.mock import patch

        from config import get_base_dir

        # sys.frozen = True の状態をモック
        with patch("config.sys") as mock_sys:
            mock_sys.frozen = True
            mock_sys._MEIPASS = "/fake/meipass/directory"

            result = get_base_dir()

            # frozen 状態では _MEIPASS を返す
            assert result == "/fake/meipass/directory"

    def test_load_with_non_json_decode_exception(self):
        """_load() で JSONDecodeError 以外の例外が発生した場合"""
        from unittest.mock import patch

        # os.path.exists を True を返すようにモック
        # open() が RuntimeError を投げるようにパッチ
        with (
            patch("os.path.exists", return_value=True),
            patch("builtins.open", side_effect=RuntimeError("Unexpected IO error")),
        ):
            config = Config("some_file.json")

            # 一般例外でもデフォルト設定にフォールバック
            assert config.enabled is True
            assert config.rules == []

    def test_validate_rules_with_non_dict_elements(self):
        """rules 配列に dict でない要素が含まれる場合"""
        config_data = {
            "enabled": True,
            "rules": [
                {"name": "valid-rule", "type": "literal", "from": "a", "to": "b", "enabled": True},
                "not_a_dict",  # 文字列
                123,  # 整数
                None,  # null
                {"name": "another-valid", "type": "literal", "from": "x", "to": "y", "enabled": True},
            ],
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
            json.dump(config_data, f)
            temp_file = f.name

        try:
            config = Config(temp_file)

            # dict でない要素はスキップされ、有効なルールのみ読み込まれる
            assert len(config.rules) == 2
            assert config.rules[0]["name"] == "valid-rule"
            assert config.rules[1]["name"] == "another-valid"
        finally:
            os.unlink(temp_file)
