"""
通知機能付き変換テスト
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from winotify import Notification
from transformer import Transformer, LiteralRule
from clipboard_util import set_text, get_text
import time

print("=== 通知機能付き変換テスト ===\n")

# 1. 変換テスト
print("1. 変換ロジックのテスト...")
transformer = Transformer()
transformer.add_rule(LiteralRule("test", "旧文字列", "新文字列"))
result = transformer.transform("旧文字列")
print(f"   変換: '旧文字列' → '{result}'")
assert result == "新文字列"
print("   ✓ 変換成功")

# 2. クリップボードテスト
print("\n2. クリップボード操作のテスト...")
test_text = "テストテキスト"
set_text(test_text)
retrieved = get_text()
print(f"   設定: '{test_text}' → 取得: '{retrieved}'")
assert retrieved == test_text
print("   ✓ クリップボード操作成功")

# 3. 通知テスト
print("\n3. 通知表示のテスト...")
try:
    toast = Notification(
        app_id="Clipboard Transformer",
        title="変換完了",
        msg="テキストが変換されました",
        duration="short"
    )
    toast.show()
    print("   ✓ 通知を送信しました")
    print("\n   Windows通知が表示されましたか？")
except Exception as e:
    print(f"   ✗ 通知失敗: {e}")

print("\n=== テスト完了 ===")
print("\n次のステップ:")
print("  python main.py")
print("を実行して、実際に Ctrl+V で変換と通知をテストしてください")
