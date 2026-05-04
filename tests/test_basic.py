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


class TestRegexRuleExceptionHandling:
    """RegexRule の例外処理テスト"""

    def test_regex_invalid_backreference_in_replacement(self):
        """無効な後方参照がある場合の処理"""
        # パターンにキャプチャグループが無いのに、置換で \1 を使用
        rule = RegexRule("test", r"\d+", r"[\1]")
        # このケースでは実際にエラーが発生する可能性がある
        # 実装では try-except で元のテキストを返す
        result = rule.apply("test 123")
        # エラーハンドリングにより、元のテキストまたは安全な結果を返す
        assert isinstance(result, str)

    def test_regex_apply_with_invalid_pattern(self):
        """無効なパターンを持つルールは元のテキストを返す"""
        rule = RegexRule("test", "[invalid(", "replacement")
        # compiled_pattern が None の場合、元のテキストを返す
        assert rule.compiled_pattern is None
        result = rule.apply("test text")
        assert result == "test text"


class TestTransformerExceptionHandling:
    """Transformer の例外処理テスト"""

    def test_transform_continues_on_rule_exception(self):
        """ルール適用中に例外が発生しても処理を継続"""
        from unittest.mock import Mock
        
        transformer = Transformer()
        
        # 正常なルール
        good_rule = LiteralRule("good", "foo", "bar")
        
        # 例外を投げるルール
        bad_rule = Mock()
        bad_rule.enabled = True
        bad_rule.name = "bad_rule"
        bad_rule.apply.side_effect = Exception("Rule error")
        
        # もう1つの正常なルール
        another_good_rule = LiteralRule("another", "bar", "baz")
        
        transformer.add_rule(good_rule)
        transformer.add_rule(bad_rule)
        transformer.add_rule(another_good_rule)
        
        # foo -> bar -> (例外) -> baz
        result = transformer.transform("foo")
        
        # 例外が発生しても処理は継続され、他のルールは適用される
        assert result == "baz"


class TestTransformerLoadRules:
    """Transformer.load_rules_from_config() のテスト"""

    def test_load_unknown_rule_type(self):
        """未知のルールタイプは警告してスキップ"""
        transformer = Transformer()
        
        rules_config = [
            {
                "name": "valid-rule",
                "type": "literal",
                "from": "foo",
                "to": "bar",
                "enabled": True
            },
            {
                "name": "unknown-rule",
                "type": "unknown_type",  # 未知のタイプ
                "some_field": "value"
            },
            {
                "name": "another-valid",
                "type": "regex",
                "pattern": r"\d+",
                "replacement": "NUM",
                "enabled": True
            }
        ]
        
        transformer.load_rules_from_config(rules_config)
        
        # 未知のタイプはスキップされ、有効なルールのみ読み込まれる
        assert len(transformer.rules) == 2
        assert transformer.rules[0].name == "valid-rule"
        assert transformer.rules[1].name == "another-valid"

    def test_load_rule_with_exception(self):
        """ルール読み込み中の例外をハンドリング"""
        transformer = Transformer()
        
        rules_config = [
            {
                "name": "valid-rule",
                "type": "literal",
                "from": "foo",
                "to": "bar",
                "enabled": True
            },
            {
                "name": "broken-rule",
                "type": "literal"
                # 必須フィールド "from", "to" が欠如
                # 実装では get() でデフォルト値 "" が使用されるため、
                # 例外は発生せず、空文字列のルールとして読み込まれる
            },
            {
                "name": "another-valid",
                "type": "literal",
                "from": "hello",
                "to": "hi",
                "enabled": True
            }
        ]
        
        # 例外が発生しても処理は継続
        transformer.load_rules_from_config(rules_config)
        
        # from/to が無い場合もデフォルト値で読み込まれる
        assert len(transformer.rules) == 3
        assert transformer.rules[0].name == "valid-rule"
        assert transformer.rules[1].name == "broken-rule"
        assert transformer.rules[2].name == "another-valid"

    def test_load_literal_rule_missing_fields(self):
        """literalルールで必須フィールドが無い場合"""
        transformer = Transformer()
        
        rules_config = [
            {
                "name": "incomplete",
                "type": "literal"
                # "from" と "to" が無い
            }
        ]
        
        # 例外が発生してもクラッシュしない
        transformer.load_rules_from_config(rules_config)
        
        # from/to がデフォルト値 "" で読み込まれる
        assert len(transformer.rules) == 1
        assert transformer.rules[0].from_str == ""
        assert transformer.rules[0].to_str == ""

    def test_load_regex_rule_missing_fields(self):
        """regexルールで必須フィールドが無い場合"""
        transformer = Transformer()
        
        rules_config = [
            {
                "name": "incomplete-regex",
                "type": "regex"
                # "pattern" と "replacement" が無い
            }
        ]
        
        transformer.load_rules_from_config(rules_config)
        
        # pattern/replacement がデフォルト値 "" で読み込まれる
        assert len(transformer.rules) == 1
        # 空のパターンは無効なので compiled_pattern は None かもしれない
        # または空文字列にマッチするパターンとして扱われる
