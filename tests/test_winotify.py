"""
代替通知ライブラリ winotify のテスト
"""

print("=== winotify テスト ===\n")

print("1. winotify のインストール確認...")
try:
    from winotify import Notification
    print("   ✓ winotify がインストール済み")
    
    print("\n2. 通知テスト...")
    toast = Notification(
        app_id="Clipboard Transformer",
        title="テスト通知",
        msg="winotify による通知テストです",
        duration="short"
    )
    toast.show()
    print("   ✓ 通知を送信しました")
    print("\n通知が表示されましたか？")
    
except ImportError:
    print("   ✗ winotify がインストールされていません")
    print("\nインストール方法:")
    print("   pip install winotify")
except Exception as e:
    print(f"   ✗ エラー: {e}")
    import traceback
    traceback.print_exc()
