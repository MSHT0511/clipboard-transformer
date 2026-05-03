"""
pytest設定ファイル

共通のフィクスチャやテスト設定を定義
"""

import pytest
import sys
from pathlib import Path

# プロジェクトのルートディレクトリをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
