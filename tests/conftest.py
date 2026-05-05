"""
pytest設定ファイル

共通のフィクスチャやテスト設定を定義
"""

import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

# プロジェクトのルートディレクトリをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def temp_config_file():
    """
    テスト用の空の一時設定ファイルを作成する

    Returns:
        str: 一時設定ファイルのパス
    """
    config_data = {"enabled": True, "notification_sound": "Default", "rules": []}

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
        json.dump(config_data, f)
        temp_file = f.name

    yield temp_file

    if os.path.exists(temp_file):
        os.unlink(temp_file)


@pytest.fixture
def temp_config_with_rules():
    """
    テスト用のルール付き一時設定ファイルを作成する

    Returns:
        str: 一時設定ファイルのパス
    """
    config_data = {
        "enabled": True,
        "notification_sound": "Default",
        "rules": [
            {"name": "test-literal", "type": "literal", "from": "OLD", "to": "NEW", "enabled": True},
            {"name": "test-regex", "type": "regex", "pattern": r"\d+", "replacement": "NUM", "enabled": True},
        ],
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
        json.dump(config_data, f)
        temp_file = f.name

    yield temp_file

    if os.path.exists(temp_file):
        os.unlink(temp_file)


@pytest.fixture
def sample_rules():
    """
    テスト用の標準ルールリストを返す

    Returns:
        list: ルール設定の辞書のリスト
    """
    return [
        {"name": "test-literal", "type": "literal", "from": "OLD", "to": "NEW", "enabled": True},
        {"name": "test-regex", "type": "regex", "pattern": r"\d+", "replacement": "NUM", "enabled": True},
    ]


@pytest.fixture
def mock_clipboard():
    """
    win32clipboard のモックを作成する

    Yields:
        Mock: win32clipboard のモックオブジェクト
    """
    with patch("clipboard_util.win32clipboard") as mock:
        yield mock
