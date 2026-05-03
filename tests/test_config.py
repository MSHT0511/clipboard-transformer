"""設定ファイル読み込みのテスト"""

import pytest
import json
import tempfile
import os
from pathlib import Path
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
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
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
            "rules": [
                {
                    "name": "test-literal",
                    "type": "literal",
                    "from": "foo",
                    "to": "bar",
                    "enabled": True
                }
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
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
                {
                    "name": "test-regex",
                    "type": "regex",
                    "pattern": r"\d+",
                    "replacement": "NUM",
                    "enabled": True
                }
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
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
        config_data = {
            "enabled": True,
            "rules": [
                {"name": "invalid", "type": "unknown", "from": "a", "to": "b"}
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
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
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
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
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump(config_data, f)
            temp_file = f.name
        
        try:
            config = Config(temp_file)
            assert len(config.get_rules()) == 0
        finally:
            os.unlink(temp_file)
    
    def test_save_default_config(self):
        """デフォルト設定ファイルの作成"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_file = f.name
        
        os.unlink(temp_file)  # 一旦削除
        
        try:
            config = Config(temp_file)
            assert config.save_default_config() is True
            assert Path(temp_file).exists()
            
            # 保存されたファイルを読み込んで検証
            with open(temp_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            assert "enabled" in data
            assert "rules" in data
            assert isinstance(data["rules"], list)
        finally:
            if Path(temp_file).exists():
                os.unlink(temp_file)


class TestConfigTransformerIntegration:
    """Config と Transformer の統合テスト"""
    
    def test_load_rules_into_transformer(self):
        """設定ファイルからTransformerへのルール読み込み"""
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
