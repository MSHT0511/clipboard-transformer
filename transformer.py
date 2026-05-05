"""
変換ルールエンジン

literal タイプと regex タイプの変換ルールをサポートし、
ルールを上から順に適用してテキストを変換する。
"""

import logging
import re

logger = logging.getLogger(__name__)

# 定数
RULE_TYPE_LITERAL = "literal"
RULE_TYPE_REGEX = "regex"
FIELD_TYPE = "type"
FIELD_NAME = "name"
FIELD_ENABLED = "enabled"
FIELD_FROM = "from"
FIELD_TO = "to"
FIELD_PATTERN = "pattern"
FIELD_REPLACEMENT = "replacement"


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

    def _create_rule_from_config(self, rule_config: dict) -> TransformationRule | None:
        """
        設定辞書から単一のルールを作成する

        Args:
            rule_config: ルール設定の辞書

        Returns:
            TransformationRule | None: 作成されたルール、またはエラーの場合は None
        """
        try:
            rule_type = rule_config.get(FIELD_TYPE)
            name = rule_config.get(FIELD_NAME, "unnamed")
            enabled = rule_config.get(FIELD_ENABLED, True)

            if rule_type == RULE_TYPE_LITERAL:
                from_str = rule_config.get(FIELD_FROM, "")
                to_str = rule_config.get(FIELD_TO, "")
                logger.info(f"Loaded literal rule: {name}")
                return LiteralRule(name, from_str, to_str, enabled)

            elif rule_type == RULE_TYPE_REGEX:
                pattern = rule_config.get(FIELD_PATTERN, "")
                replacement = rule_config.get(FIELD_REPLACEMENT, "")
                logger.info(f"Loaded regex rule: {name}")
                return RegexRule(name, pattern, replacement, enabled)

            else:
                logger.warning(f"Unknown rule type '{rule_type}' for rule '{name}'")
                return None

        except Exception as e:
            logger.error(f"Error creating rule: {e}")
            return None

    def load_rules_from_config(self, rules_config: list):
        """設定リストからルールを読み込む"""
        self.clear_rules()

        for rule_config in rules_config:
            rule = self._create_rule_from_config(rule_config)
            if rule is not None:
                self.add_rule(rule)
