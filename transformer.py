"""
変換ルールエンジン

literal タイプと regex タイプの変換ルールをサポートし、
ルールを上から順に適用してテキストを変換する。
"""

import logging
import re

logger = logging.getLogger(__name__)


class TransformationRule:
    """変換ルールの基底クラス"""

    def __init__(self, name: str, enabled: bool = True):
        self.name = name
        self.enabled = enabled

    def apply(self, text: str) -> str:
        """ルールを適用してテキストを変換"""
        raise NotImplementedError


class LiteralRule(TransformationRule):
    """固定文字列の置換ルール"""

    def __init__(self, name: str, from_str: str, to_str: str, enabled: bool = True):
        super().__init__(name, enabled)
        self.from_str = from_str
        self.to_str = to_str

    def apply(self, text: str) -> str:
        if not self.enabled:
            return text
        return text.replace(self.from_str, self.to_str)


class RegexRule(TransformationRule):
    """正規表現による置換ルール"""

    def __init__(self, name: str, pattern: str, replacement: str, enabled: bool = True):
        super().__init__(name, enabled)
        self.pattern = pattern
        self.replacement = replacement
        try:
            self.compiled_pattern = re.compile(pattern)
        except re.error as e:
            logger.error(f"Invalid regex pattern in rule '{name}': {e}")
            self.compiled_pattern = None

    def apply(self, text: str) -> str:
        if not self.enabled or self.compiled_pattern is None:
            return text
        try:
            return self.compiled_pattern.sub(self.replacement, text)
        except Exception as e:
            logger.error(f"Error applying regex rule '{self.name}': {e}")
            return text


class Transformer:
    """変換ルールを管理し、テキストに適用する"""

    def __init__(self):
        self.rules = []

    def add_rule(self, rule: TransformationRule):
        """ルールを追加"""
        self.rules.append(rule)

    def clear_rules(self):
        """全ルールをクリア"""
        self.rules.clear()

    def transform(self, text: str) -> str:
        """全ルールを順番に適用してテキストを変換"""
        result = text
        for rule in self.rules:
            if rule.enabled:
                try:
                    old_result = result
                    result = rule.apply(result)
                    if old_result != result:
                        logger.debug(f"Rule '{rule.name}' applied")
                except Exception as e:
                    logger.error(f"Error applying rule '{rule.name}': {e}")
        return result

    def load_rules_from_config(self, rules_config: list):
        """設定リストからルールを読み込む"""
        self.clear_rules()

        for rule_config in rules_config:
            try:
                rule_type = rule_config.get("type")
                name = rule_config.get("name", "unnamed")
                enabled = rule_config.get("enabled", True)

                if rule_type == "literal":
                    from_str = rule_config.get("from", "")
                    to_str = rule_config.get("to", "")
                    rule = LiteralRule(name, from_str, to_str, enabled)
                    self.add_rule(rule)
                    logger.info(f"Loaded literal rule: {name}")

                elif rule_type == "regex":
                    pattern = rule_config.get("pattern", "")
                    replacement = rule_config.get("replacement", "")
                    rule = RegexRule(name, pattern, replacement, enabled)
                    self.add_rule(rule)
                    logger.info(f"Loaded regex rule: {name}")

                else:
                    logger.warning(f"Unknown rule type '{rule_type}' for rule '{name}'")

            except Exception as e:
                logger.error(f"Error loading rule: {e}")
