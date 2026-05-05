"""
設定ファイル (config.json) の読み込みとバリデーション
"""

import json
import logging
import os
import sys
from typing import Any

logger = logging.getLogger(__name__)

# 定数
RULE_TYPE_LITERAL = "literal"
RULE_TYPE_REGEX = "regex"
FIELD_NAME = "name"
FIELD_TYPE = "type"
FIELD_FROM = "from"
FIELD_TO = "to"
FIELD_PATTERN = "pattern"
FIELD_REPLACEMENT = "replacement"
FIELD_ENABLED = "enabled"


def get_base_dir() -> str:
    """PyInstaller バンドル時は _MEIPASS、通常時はスクリプトのディレクトリを返す"""
    if getattr(sys, "frozen", False):
        return sys._MEIPASS  # type: ignore[attr-defined]
    return os.path.dirname(os.path.abspath(__file__))


class Config:
    """設定ファイルの管理クラス"""

    DEFAULT_CONFIG = {"enabled": True, "notification_sound": "Default", "rules": []}

    VALID_SOUNDS = ["Default", "IM", "Mail", "Reminder", "SMS", "Silent"]

    def __init__(self, config_path: str | None = None):
        if config_path is None:
            config_path = os.path.join(get_base_dir(), "config.json")
        self.config_path = config_path
        self.enabled = True
        self.notification_sound = "Default"
        self.rules = []
        self._load()

    def _load(self):
        """設定ファイルを読み込む"""
        if not os.path.exists(self.config_path):
            logger.warning(f"Config file not found: {self.config_path}, using default config")
            self._use_default()
            return

        try:
            with open(self.config_path, encoding="utf-8") as f:
                data = json.load(f)

            if not isinstance(data, dict):
                logger.error("Config file is not a valid JSON object")
                self._use_default()
                return

            self.enabled = data.get("enabled", True)
            self.notification_sound = data.get("notification_sound", "Default")
            if self.notification_sound not in self.VALID_SOUNDS:
                logger.warning(f"Invalid notification_sound '{self.notification_sound}', using Default")
                self.notification_sound = "Default"
            self.rules = data.get("rules", [])

            if not isinstance(self.rules, list):
                logger.error("'rules' field must be an array")
                self.rules = []

            # ルールのバリデーション
            self._validate_rules()

            logger.info(f"Config loaded: {len(self.rules)} rules, enabled={self.enabled}")

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse config file: {e}")
            self._use_default()

        except Exception as e:
            logger.error(f"Error loading config: {e}")
            self._use_default()

    def _use_default(self):
        """デフォルト設定を使用"""
        self.enabled = self.DEFAULT_CONFIG["enabled"]
        self.notification_sound = self.DEFAULT_CONFIG["notification_sound"]
        self.rules = self.DEFAULT_CONFIG["rules"]

    def _is_valid_rule(self, rule: Any, index: int) -> bool:
        """
        単一のルールが妥当かどうかをチェックする

        Args:
            rule: チェック対象のルール
            index: ルールのインデックス（エラーメッセージ用）

        Returns:
            bool: ルールが妥当な場合 True
        """
        if not isinstance(rule, dict):
            logger.warning(f"Rule #{index} is not an object, skipping")
            return False

        rule_type = rule.get(FIELD_TYPE)
        if rule_type not in [RULE_TYPE_LITERAL, RULE_TYPE_REGEX]:
            logger.warning(f"Rule #{index} has invalid type '{rule_type}', skipping")
            return False

        name = rule.get(FIELD_NAME, f"rule-{index}")

        # literal タイプのバリデーション
        if rule_type == RULE_TYPE_LITERAL:
            if FIELD_FROM not in rule or FIELD_TO not in rule:
                logger.warning(f"Literal rule '{name}' missing 'from' or 'to', skipping")
                return False

        # regex タイプのバリデーション
        elif rule_type == RULE_TYPE_REGEX and (FIELD_PATTERN not in rule or FIELD_REPLACEMENT not in rule):
            logger.warning(f"Regex rule '{name}' missing 'pattern' or 'replacement', skipping")
            return False

        return True

    def _validate_rules(self):
        """ルールの妥当性をチェック"""
        valid_rules = []

        for i, rule in enumerate(self.rules):
            if self._is_valid_rule(rule, i):
                valid_rules.append(rule)

        self.rules = valid_rules

    def reload(self):
        """設定ファイルを再読み込み"""
        logger.info("Reloading configuration...")
        self._load()

    def is_enabled(self) -> bool:
        """機能が有効かどうかを返す"""
        return self.enabled

    def get_rules(self) -> list[dict[str, Any]]:
        """ルールリストを返す"""
        return self.rules

    def save_default_config(self):
        """デフォルトのサンプル設定ファイルを作成"""
        sample_config = {
            FIELD_ENABLED: True,
            "rules": [
                {
                    FIELD_NAME: "example-literal",
                    FIELD_TYPE: RULE_TYPE_LITERAL,
                    FIELD_FROM: "旧文字列",
                    FIELD_TO: "新文字列",
                    FIELD_ENABLED: True,
                },
                {
                    FIELD_NAME: "remove-dates",
                    FIELD_TYPE: RULE_TYPE_REGEX,
                    FIELD_PATTERN: "\\d{4}-\\d{2}-\\d{2}",
                    FIELD_REPLACEMENT: "DATE_REMOVED",
                    FIELD_ENABLED: True,
                },
            ],
        }

        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(sample_config, f, ensure_ascii=False, indent=2)
            logger.info(f"Default config saved to {self.config_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save default config: {e}")
            return False

    def save(self):
        """現在の設定をファイルに保存"""
        try:
            # 既存のファイルを読み込んで更新
            data = {}
            if os.path.exists(self.config_path):
                with open(self.config_path, encoding="utf-8") as f:
                    data = json.load(f)

            data["enabled"] = self.enabled
            data["notification_sound"] = self.notification_sound
            data["rules"] = self.rules

            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info("Config saved")
            return True
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
            return False
