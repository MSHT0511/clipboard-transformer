"""
修正内容のテスト用メモ
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

print("=== 修正内容 ===")
print()
print("【問題1】二重ペーストの修正")
print("  原因: keyboard.on_press_key() で suppress=False だったため")
print("  修正: keyboard.add_hotkey('ctrl+v', ..., suppress=True) に変更")
print("  結果: 元のCtrl+Vイベントが完全に抑制される")
print()
print("【問題2】Windows通知が表示されない")
print("  原因: pystray.notify() が別スレッドから正しく動作しない")
print("  修正: win10toast ライブラリを使用")
print("  結果: Windows標準の通知が確実に表示される")
print()
print("=== テスト方法 ===")
print()
print("1. アプリケーションを起動:")
print("   python main.py")
print()
print("2. 「旧文字列」をコピー")
print()
print("3. 任意の場所でCtrl+V")
print()
print("4. 期待結果:")
print("   - 「新文字列」が1回だけペーストされる（二重にならない）")
print("   - Windows通知が表示される")
print()

import main
print("✅ モジュールのインポート成功")

# 変換エンジンのテスト
from transformer import Transformer, LiteralRule
transformer = Transformer()
transformer.add_rule(LiteralRule("test", "旧文字列", "新文字列"))
result = transformer.transform("旧文字列")
assert result == "新文字列", f"Expected '新文字列' but got '{result}'"
print("✅ 変換ロジックは正常")
print()
print("次は実際にアプリを起動してテストしてください！")
