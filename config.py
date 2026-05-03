"""
設定ファイル (config.json) の読み込みとバリデーション
"""

import json
import os
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class Config:
    """設定ファイルの管理クラス"""

    DEFAULT_CONFIG = {
        "enabled": True,
        "notification_sound": "Default",
        "rules": []
    }

    VALID_SOUNDS = ["Default", "IM", "Mail", "Reminder", "SMS", "Silent"]

    def __init__(self, config_path: str = "config.json"):
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
            with open(self.config_path, 'r', encoding='utf-8') as f:
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

    def _validate_rules(self):
        """ルールの妥当性をチェック"""
        valid_rules = []

        for i, rule in enumerate(self.rules):
            if not isinstance(rule, dict):
                logger.warning(f"Rule #{i} is not an object, skipping")
                continue

            rule_type = rule.get("type")
            if rule_type not in ["literal", "regex"]:
                logger.warning(f"Rule #{i} has invalid type '{rule_type}', skipping")
                continue

            name = rule.get("name", f"rule-{i}")

            # literal タイプのバリデーション
            if rule_type == "literal":
                if "from" not in rule or "to" not in rule:
                    logger.warning(f"Literal rule '{name}' missing 'from' or 'to', skipping")
                    continue

            # regex タイプのバリデーション
            elif rule_type == "regex":
                if "pattern" not in rule or "replacement" not in rule:
                    logger.warning(f"Regex rule '{name}' missing 'pattern' or 'replacement', skipping")
                    continue

            valid_rules.append(rule)

        self.rules = valid_rules

    def reload(self):
        """設定ファイルを再読み込み"""
        logger.info("Reloading configuration...")
        self._load()

    def is_enabled(self) -> bool:
        """機能が有効かどうかを返す"""
        return self.enabled

    def get_rules(self) -> List[Dict[str, Any]]:
        """ルールリストを返す"""
        return self.rules

    def save_default_config(self):
        """デフォルトのサンプル設定ファイルを作成"""
        sample_config = {
            "enabled": True,
            "rules": [
                {
                    "name": "example-literal",
                    "type": "literal",
                    "from": "旧文字列",
                    "to": "新文字列",
                    "enabled": True
                },
                {
                    "name": "remove-dates",
                    "type": "regex",
                    "pattern": "\\d{4}-\\d{2}-\\d{2}",
                    "replacement": "DATE_REMOVED",
                    "enabled": True
                }
            ]
        }

        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
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
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

            data["enabled"] = self.enabled
            data["notification_sound"] = self.notification_sound
            data["rules"] = self.rules

            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info("Config saved")
            return True
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
            return False
