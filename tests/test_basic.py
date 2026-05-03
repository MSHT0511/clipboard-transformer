"""基本的な動作テスト"""

import pytest
from transformer import Transformer, LiteralRule, RegexRule


class TestLiteralRule:
    """LiteralRule のテスト"""
    
    def test_simple_replacement(self):
        """単純な文字列置換"""
        rule = LiteralRule("test", "foo", "bar")
        assert rule.apply("foo is foo") == "bar is bar"
    
    def test_no_match(self):
        """マッチしない場合は変換されない"""
        rule = LiteralRule("test", "foo", "bar")
        assert rule.apply("hello world") == "hello world"
    
    def test_disabled_rule(self):
        """無効化されたルールは適用されない"""
        rule = LiteralRule("test", "foo", "bar", enabled=False)
        assert rule.apply("foo") == "foo"
    
    def test_empty_string(self):
        """空文字列の処理"""
        rule = LiteralRule("test", "foo", "bar")
        assert rule.apply("") == ""


class TestRegexRule:
    """RegexRule のテスト"""
    
    def test_date_replacement(self):
        """日付パターンの置換"""
        rule = RegexRule("test", r"\d{4}-\d{2}-\d{2}", "DATE")
        assert rule.apply("Today is 2026-05-03") == "Today is DATE"
    
    def test_multiple_matches(self):
        """複数マッチの置換"""
        rule = RegexRule("test", r"\d+", "NUM")
        assert rule.apply("I have 3 apples and 5 oranges") == "I have NUM apples and NUM oranges"
    
    def test_backreference(self):
        """後方参照の使用"""
        rule = RegexRule("test", r"(\d{4})-(\d{2})-(\d{2})", r"\3/\2/\1")
        assert rule.apply("2026-05-03") == "03/05/2026"
    
    def test_invalid_pattern(self):
        """無効な正規表現パターンは適用されない"""
        rule = RegexRule("test", "[invalid(", "replacement")
        assert rule.compiled_pattern is None
        assert rule.apply("test text") == "test text"
    
    def test_disabled_regex_rule(self):
        """無効化された正規表現ルール"""
        rule = RegexRule("test", r"\d+", "NUM", enabled=False)
        assert rule.apply("123") == "123"


class TestTransformer:
    """Transformer のテスト"""
    
    def test_single_literal_rule(self):
        """単一のLiteralRuleの適用"""
        transformer = Transformer()
        transformer.add_rule(LiteralRule("test", "foo", "bar"))
        assert transformer.transform("foo is foo") == "bar is bar"
    
    def test_single_regex_rule(self):
        """単一のRegexRuleの適用"""
        transformer = Transformer()
        transformer.add_rule(RegexRule("test", r"\d{4}-\d{2}-\d{2}", "DATE"))
        assert transformer.transform("Today is 2026-05-03") == "Today is DATE"
    
    def test_multiple_rules_chain(self):
        """複数ルールの連鎖適用"""
        transformer = Transformer()
        transformer.add_rule(LiteralRule("rule1", "hello", "hi"))
        transformer.add_rule(LiteralRule("rule2", "world", "universe"))
        assert transformer.transform("hello world") == "hi universe"
    
    def test_rule_order_matters(self):
        """ルールの適用順序が結果に影響する"""
        transformer = Transformer()
        transformer.add_rule(LiteralRule("first", "abc", "xyz"))
        transformer.add_rule(LiteralRule("second", "xyz", "123"))
        # abc -> xyz -> 123 と連鎖する
        assert transformer.transform("abc") == "123"
    
    def test_mixed_enabled_disabled_rules(self):
        """有効/無効ルールの混在"""
        transformer = Transformer()
        transformer.add_rule(LiteralRule("enabled1", "foo", "bar", enabled=True))
        transformer.add_rule(LiteralRule("disabled", "bar", "baz", enabled=False))
        transformer.add_rule(LiteralRule("enabled2", "bar", "qux", enabled=True))
        # foo -> bar -> qux (disabled はスキップ)
        assert transformer.transform("foo") == "qux"
    
    def test_clear_rules(self):
        """ルールのクリア"""
        transformer = Transformer()
        transformer.add_rule(LiteralRule("test", "foo", "bar"))
        transformer.clear_rules()
        assert len(transformer.rules) == 0
        assert transformer.transform("foo") == "foo"
    
    def test_no_rules(self):
        """ルールが無い場合は変換されない"""
        transformer = Transformer()
        assert transformer.transform("test") == "test"
    
    def test_empty_text(self):
        """空文字列の変換"""
        transformer = Transformer()
        transformer.add_rule(LiteralRule("test", "foo", "bar"))
        assert transformer.transform("") == ""
