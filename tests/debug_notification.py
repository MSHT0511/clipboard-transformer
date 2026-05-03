"""
通知機能の詳細デバッグ
"""

import sys
import time

print("=== 通知機能デバッグ ===\n")

# 1. win10toast のインポートテスト
print("1. win10toast インポートテスト...")
try:
    from win10toast import ToastNotifier
    print("   ✓ インポート成功")
except ImportError as e:
    print(f"   ✗ インポート失敗: {e}")
    sys.exit(1)

# 2. ToastNotifier インスタンス作成
print("\n2. ToastNotifier インスタンス作成...")
try:
    toaster = ToastNotifier()
    print("   ✓ インスタンス作成成功")
except Exception as e:
    print(f"   ✗ 失敗: {e}")
    sys.exit(1)

# 3. threaded=False で同期通知テスト
print("\n3. 同期通知テスト (threaded=False)...")
print("   通知を表示します（3秒間表示されます）...")
try:
    toaster.show_toast(
        "Test Notification",
        "これはテスト通知です (同期)",
        duration=3,
        threaded=False
    )
    print("   ✓ 同期通知完了")
except Exception as e:
    print(f"   ✗ 失敗: {e}")
    import traceback
    traceback.print_exc()

# 4. threaded=True で非同期通知テスト
print("\n4. 非同期通知テスト (threaded=True)...")
print("   通知を表示します...")
try:
    toaster.show_toast(
        "Test Notification",
        "これはテスト通知です (非同期)",
        duration=5,
        threaded=True
    )
    print("   ✓ 非同期通知送信完了")
    print("   5秒待機します...")
    time.sleep(6)
    print("   待機完了")
except Exception as e:
    print(f"   ✗ 失敗: {e}")
    import traceback
    traceback.print_exc()

# 5. Windowsバージョン確認
print("\n5. Windows環境情報...")
try:
    import platform
    print(f"   OS: {platform.system()} {platform.release()}")
    print(f"   Version: {platform.version()}")
except Exception as e:
    print(f"   情報取得失敗: {e}")

print("\n=== デバッグ完了 ===")
print("\n通知が表示されましたか？")
print("- 表示された → win10toast は正常に動作しています")
print("- 表示されない → Windows設定またはライブラリの問題")
