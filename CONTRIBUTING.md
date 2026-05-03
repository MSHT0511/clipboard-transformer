# Contributing to Clipboard Transformer

まず、このプロジェクトへの貢献を検討していただき、ありがとうございます！

## 貢献方法

### バグ報告

バグを発見した場合は、以下の情報を含めてIssueを作成してください：

- **環境情報**: Windows バージョン、Python バージョン
- **再現手順**: バグを再現するための具体的な手順
- **期待される動作**: 本来どう動作すべきか
- **実際の動作**: 実際に何が起きたか
- **ログ**: `clipboard-transformer.log` の関連部分

### 機能提案

新機能の提案は大歓迎です。Issueに以下を記載してください：

- **機能の説明**: 何を実現したいか
- **ユースケース**: どんな場面で役立つか
- **実装案**: 可能であれば、実装のアイデア

### プルリクエスト

プルリクエストを送る際は以下の手順に従ってください：

#### 1. 開発環境のセットアップ

```bash
# リポジトリをフォーク・クローン
git clone https://github.com/yourusername/clipboard-transformer.git
cd clipboard-transformer

# 仮想環境を作成
python -m venv venv
source venv/Scripts/activate  # Windows

# 開発用依存関係をインストール
pip install -r requirements.txt
pip install pyinstaller
```

#### 2. ブランチの作成

```bash
git checkout -b feature/your-feature-name
# または
git checkout -b fix/your-bug-fix
```

#### 3. コーディング規約

- **PEP 8**: Pythonの標準コーディング規約に従う
- **型ヒント**: 可能な限り型アノテーションを使用
- **ドキュメント**: 関数・クラスにdocstringを記述
- **コメント**: 複雑なロジックには日本語または英語でコメント

#### 4. テストの実行

```bash
# すべてのテストを実行
pytest

# カバレッジレポート付き
pytest --cov=. --cov-report=html

# 特定のテストファイルのみ
pytest tests/test_basic.py
```

新機能には必ずテストを追加してください。

#### 5. コミット

```bash
git add .
git commit -m "Add: 新機能の説明"
# または
git commit -m "Fix: バグ修正の説明"
```

コミットメッセージの形式：
- `Add:` 新機能追加
- `Fix:` バグ修正
- `Update:` 既存機能の改善
- `Refactor:` リファクタリング
- `Docs:` ドキュメント更新
- `Test:` テスト追加・修正

#### 6. プルリクエストの作成

1. フォークしたリポジトリにプッシュ
2. GitHub上でプルリクエストを作成
3. 変更内容を明確に説明
4. 関連するIssueがあれば番号を記載（`Closes #123`）

### コードレビュー

- すべてのプルリクエストはレビューを受けます
- レビューのフィードバックには建設的に対応してください
- 必要に応じてコードを修正してください

## 開発ガイドライン

### ディレクトリ構成

```
clipboard-transformer/
├── main.py              # エントリーポイント
├── config.py            # 設定管理
├── transformer.py       # 変換エンジン
├── clipboard_util.py    # クリップボード操作
├── hook.py             # キーボードフック
├── config.json         # 設定ファイル
├── tests/              # テストコード
└── docs/               # ドキュメント
```

### テストの書き方

```python
def test_your_feature():
    """機能のテスト"""
    # Arrange（準備）
    input_data = "test input"
    
    # Act（実行）
    result = your_function(input_data)
    
    # Assert（検証）
    assert result == "expected output"
```

### デバッグ

```bash
# ログレベルをDEBUGに設定
# config.pyまたはmain.pyでlogging.DEBUGを使用
python main.py
```

## リリースプロセス

メンテナーのみ：

1. バージョン番号を更新（`pyproject.toml`, `CHANGELOG.md`）
2. CHANGELOGを更新
3. テストを実行して全てパス
4. タグを作成: `git tag v1.0.0`
5. GitHubでリリースを作成
6. EXEをビルドして添付

## コミュニティ

- 質問や議論はGitHub Discussionsで
- バグ報告・機能提案はIssuesで
- リアルタイムチャットが必要な場合は検討中

## ライセンス

貢献したコードは、プロジェクトのMITライセンスの下でリリースされます。

---

貢献をお待ちしています！
