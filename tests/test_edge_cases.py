"""
エッジケーステスト - 境界条件やエラーケースの確認
"""

from transformer import LiteralRule, RegexRule, Transformer


class TestEdgeCases:
    """エッジケースのテスト"""

    def test_empty_string(self):
        """空文字列の処理"""
        transformer = Transformer()
        transformer.add_rule(LiteralRule("test", "foo", "bar"))
        assert transformer.transform("") == ""

    def test_special_characters(self):
        """特殊文字（エスケープシーケンス）の処理"""
        transformer = Transformer()
        transformer.add_rule(LiteralRule("special", "\\n", "NEWLINE"))
        assert transformer.transform("Line1\\nLine2") == "Line1NEWLINELine2"

    def test_unicode_characters(self):
        """Unicode文字（サロゲートペア）の処理"""
        transformer = Transformer()
        transformer.add_rule(LiteralRule("unicode", "𠮷野家", "吉野家"))
        assert transformer.transform("𠮷野家に行きました") == "吉野家に行きました"

    def test_long_text(self):
        """長いテキストの処理"""
        transformer = Transformer()
        transformer.add_rule(LiteralRule("long", "a", "b"))
        long_text = "a" * 10000
        result = transformer.transform(long_text)
        assert result == "b" * 10000
        assert len(result) == 10000

    def test_regex_backreference(self):
        """正規表現の後方参照"""
        transformer = Transformer()
        transformer.add_rule(RegexRule("backref", r"(\d{4})-(\d{2})-(\d{2})", r"\3/\2/\1"))
        assert transformer.transform("Date: 2026-05-03") == "Date: 03/05/2026"

    def test_invalid_regex_pattern(self):
        """無効な正規表現パターンはスキップされる"""
        transformer = Transformer()
        RegexRule("invalid", "[invalid(", "replacement")
        # 無効なパターンは適用されない
        assert transformer.transform("test text") == "test text"

    def test_multiple_occurrences(self):
        """同じパターンが複数回出現する場合"""
        transformer = Transformer()
        transformer.add_rule(LiteralRule("test", "foo", "bar"))
        assert transformer.transform("foo foo foo") == "bar bar bar"

    def test_overlapping_patterns(self):
        """重複するパターンの処理"""
        transformer = Transformer()
        transformer.add_rule(LiteralRule("test", "abc", "xyz"))
        # "aabc" の "abc" 部分のみ置換される
        assert transformer.transform("aabc") == "axyz"

    def test_case_sensitive(self):
        """大文字小文字の区別"""
        transformer = Transformer()
        transformer.add_rule(LiteralRule("test", "foo", "bar"))
        assert transformer.transform("Foo FOO foo") == "Foo FOO bar"

    def test_whitespace_preservation(self):
        """空白文字の保持"""
        transformer = Transformer()
        transformer.add_rule(LiteralRule("test", "foo", "bar"))
        assert transformer.transform("  foo  ") == "  bar  "
        assert transformer.transform("foo\nfoo") == "bar\nbar"
        assert transformer.transform("foo\t\tfoo") == "bar\t\tbar"

    def test_no_transformation_needed(self):
        """変換が不要な場合"""
        transformer = Transformer()
        transformer.add_rule(LiteralRule("test", "foo", "bar"))
        text = "この文字列は変更されません"
        assert transformer.transform(text) == text

    def test_regex_special_chars_in_literal(self):
        """正規表現特殊文字を含むリテラル置換"""
        transformer = Transformer()
        transformer.add_rule(LiteralRule("test", "$100", "¥100"))
        assert transformer.transform("Price: $100") == "Price: ¥100"

    def test_replacement_creates_new_match(self):
        """置換結果が次のルールにマッチする場合（連鎖）"""
        transformer = Transformer()
        transformer.add_rule(LiteralRule("first", "a", "b"))
        transformer.add_rule(LiteralRule("second", "b", "c"))
        # a -> b -> c と連鎖
        assert transformer.transform("a") == "c"

    def test_circular_replacement_pattern(self):
        """循環参照的なパターン（無限ループにならない）"""
        transformer = Transformer()
        transformer.add_rule(LiteralRule("rule1", "a", "b"))
        transformer.add_rule(LiteralRule("rule2", "b", "a"))
        # a -> b -> a となるが、1回の変換で終わる
        assert transformer.transform("a") == "a"

    def test_empty_replacement(self):
        """空文字列への置換（削除）"""
        transformer = Transformer()
        transformer.add_rule(LiteralRule("delete", "foo", ""))
        assert transformer.transform("foo bar foo") == " bar "

    def test_regex_greedy_vs_nongreedy(self):
        """正規表現の貪欲マッチと非貪欲マッチ"""
        transformer = Transformer()
        # 貪欲マッチ
        transformer.add_rule(RegexRule("greedy", r"<.*>", "[TAG]"))
        assert transformer.transform("<a>text<b>") == "[TAG]"

        transformer.clear_rules()
        # 非貪欲マッチ
        transformer.add_rule(RegexRule("nongreedy", r"<.*?>", "[TAG]"))
        assert transformer.transform("<a>text<b>") == "[TAG]text[TAG]"
