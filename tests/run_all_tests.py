"""
全テストの実行とサマリー
"""

import subprocess
import sys
from pathlib import Path

def run_test_file(filename, description):
    """テストファイルを実行して結果を返す"""
    print(f"\n{'='*70}")
    print(f"Running: {description}")
    print('='*70)
    
    # testsディレクトリからの相対パス
    test_path = Path(__file__).parent / filename
    
    result = subprocess.run(
        [sys.executable, str(test_path)],
        capture_output=False,
        text=True
    )
    
    return result.returncode == 0

def main():
    """全テストを実行"""
    print("╔" + "═"*68 + "╗")
    print("║" + " "*20 + "CLIPBOARD TRANSFORMER TEST SUITE" + " "*16 + "║")
    print("╚" + "═"*68 + "╝")
    
    tests = [
        ("test_basic.py", "Basic Transformation Tests"),
        ("test_config.py", "Configuration Loading Tests"),
        ("test_integration.py", "Integration Tests"),
        ("test_edge_cases.py", "Edge Cases & Validation Tests"),
    ]
    
    results = {}
    
    for test_file, description in tests:
        success = run_test_file(test_file, description)
        results[description] = success
    
    # 最終サマリー
    print("\n\n" + "╔" + "═"*68 + "╗")
    print("║" + " "*25 + "FINAL TEST SUMMARY" + " "*25 + "║")
    print("╠" + "═"*68 + "╣")
    
    all_passed = True
    for description, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"║  {status}  {description:<55} ║")
        if not success:
            all_passed = False
    
    print("╠" + "═"*68 + "╣")
    
    if all_passed:
        print("║" + " "*12 + "🎉 ALL TESTS PASSED SUCCESSFULLY! 🎉" + " "*14 + "║")
        print("║" + " "*68 + "║")
        print("║  Ready for production use!                                         ║")
    else:
        print("║" + " "*17 + "❌ SOME TESTS FAILED ❌" + " "*21 + "║")
        print("║" + " "*68 + "║")
        print("║  Please review the failures above.                                 ║")
    
    print("╚" + "═"*68 + "╝")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
