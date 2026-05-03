"""
統合テスト - クリップボード変換の動作確認
"""

import pytest
import time
import json
import tempfile
import os
from config import Config
from transformer import Transformer
from clipboard_util import get_text, set_text, has_text


class TestClipboardOperations:
    """クリップボード操作の基本テスト"""
    
    def test_set_and_get_text(self):
        """クリップボードへのテキスト設定と取得"""
        test_text = "テストテキスト"
        assert set_text(test_text) is True
        time.sleep(0.05)
        assert get_text() == test_text
    
    def test_has_text_with_text(self):
        """テキストがある場合のhas_text"""
        set_text("test")
        time.sleep(0.05)
        assert has_text() == True
    
    def test_set_empty_string(self):
        """空文字列の設定"""
        assert set_text("") is True
        time.sleep(0.05)
        assert get_text() == ""
    
    def test_unicode_text(self):
        """Unicode文字のクリップボード操作"""
        test_text = "日本語 🎉 𠮷野家"
        assert set_text(test_text) is True
        time.sleep(0.05)
        assert get_text() == test_text
    
    def test_long_text(self):
        """長いテキストのクリップボード操作"""
        test_text = "あ" * 10000
        assert set_text(test_text) is True
        time.sleep(0.05)
        retrieved = get_text()
        assert retrieved == test_text
        assert len(retrieved) == 10000
    
    def test_special_characters(self):
        """特殊文字を含むテキスト"""
        test_text = "Line1\nLine2\tTab\r\nCRLF"
        assert set_text(test_text) is True
        time.sleep(0.05)
        assert get_text() == test_text


class TestClipboardTransformation:
    """クリップボード変換の統合テスト"""
    
    @pytest.fixture
    def temp_config(self):
        """テスト用の一時設定ファイルを作成"""
        config_data = {
            "enabled": True,
            "rules": [
                {
                    "name": "literal-test",
                    "type": "literal",
                    "from": "旧文字列",
                    "to": "新文字列",
                    "enabled": True
                },
                {
                    "name": "regex-test",
                    "type": "regex",
                    "pattern": r"\d{4}-\d{2}-\d{2}",
                    "replacement": "DATE_REMOVED",
                    "enabled": True
                }
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump(config_data, f)
            temp_file = f.name
        
        yield temp_file
        
        if os.path.exists(temp_file):
            os.unlink(temp_file)
    
    def test_literal_replacement(self, temp_config):
        """リテラル置換の統合テスト"""
        config = Config(temp_config)
        transformer = Transformer()
        transformer.load_rules_from_config(config.get_rules())
        
        input_text = "これは旧文字列です"
        expected = "これは新文字列です"
        
        set_text(input_text)
        time.sleep(0.05)
        clipboard_text = get_text()
        result = transformer.transform(clipboard_text)
        
        assert result == expected
    
    def test_regex_replacement(self, temp_config):
        """正規表現置換の統合テスト"""
        config = Config(temp_config)
        transformer = Transformer()
        transformer.load_rules_from_config(config.get_rules())
        
        input_text = "今日は2026-05-03です"
        expected = "今日はDATE_REMOVEDです"
        
        set_text(input_text)
        time.sleep(0.05)
        clipboard_text = get_text()
        result = transformer.transform(clipboard_text)
        
        assert result == expected
    
    def test_both_rules(self, temp_config):
        """複数ルールの統合テスト"""
        config = Config(temp_config)
        transformer = Transformer()
        transformer.load_rules_from_config(config.get_rules())
        
        input_text = "旧文字列は2026-05-03に変更されます"
        expected = "新文字列はDATE_REMOVEDに変更されます"
        
        set_text(input_text)
        time.sleep(0.05)
        clipboard_text = get_text()
        result = transformer.transform(clipboard_text)
        
        assert result == expected
    
    def test_no_change(self, temp_config):
        """変換が不要な場合の統合テスト"""
        config = Config(temp_config)
        transformer = Transformer()
        transformer.load_rules_from_config(config.get_rules())
        
        input_text = "この文字列は変更されません"
        
        set_text(input_text)
        time.sleep(0.05)
        clipboard_text = get_text()
        result = transformer.transform(clipboard_text)
        
        assert result == input_text
    
    def test_clipboard_roundtrip(self, temp_config):
        """クリップボード経由の変換ラウンドトリップ"""
        config = Config(temp_config)
        transformer = Transformer()
        transformer.load_rules_from_config(config.get_rules())
        
        # 元のテキストをクリップボードに設定
        original = "旧文字列"
        set_text(original)
        time.sleep(0.05)
        
        # クリップボードから取得
        clipboard_text = get_text()
        assert clipboard_text == original
        
        # 変換
        transformed = transformer.transform(clipboard_text)
        assert transformed == "新文字列"
        
        # 変換後をクリップボードに設定
        set_text(transformed)
        time.sleep(0.05)
        
        # 再取得して確認
        final = get_text()
        assert final == "新文字列"
