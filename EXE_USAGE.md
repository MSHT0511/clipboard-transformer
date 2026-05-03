# Clipboard Transformer - EXE版 実行方法

## 📦 実行ファイル

`dist/ClipboardTransformer.exe` が作成されました（約27MB）

## 🚀 使い方

### 1. 初回セットアップ

1. `dist` フォルダから以下をコピー：
   - `ClipboardTransformer.exe`
   - `config.json`（ルートディレクトリから）

2. 任意のフォルダに配置（例：`C:\Program Files\ClipboardTransformer\`）

### 2. 実行

**重要: 管理者権限で実行してください**

- 方法1: `ClipboardTransformer.exe` を右クリック → **管理者として実行**
- 方法2: 管理者権限のコマンドプロンプトから実行

### 3. 動作確認

1. システムトレイに緑色の "CT" アイコンが表示される
2. テキスト「旧文字列」をコピー
3. 任意の場所で Ctrl+V
4. 「新文字列」がペーストされ、通知が表示される

### 4. 設定のカスタマイズ

`config.json` を編集して変換ルールをカスタマイズできます。

変更後：
- システムトレイアイコンを右クリック
- **Reload Config** をクリック

## ⚙️ 自動起動の設定（オプション）

Windows起動時に自動実行するには：

1. `Win + R` → `shell:startup` と入力
2. スタートアップフォルダが開く
3. `ClipboardTransformer.exe` のショートカットを作成して配置
4. ショートカットのプロパティ → **管理者として実行** にチェック

## ⚠️ トラブルシューティング

### セキュリティ警告が出る
- 初回実行時、Windows Defenderが警告を出す場合があります
- 「詳細情報」→「実行」で起動できます

### キーフックが動作しない
- **管理者権限**で実行していることを確認してください

### 通知が表示されない
- Windows設定 → システム → 通知 で通知が有効になっているか確認

### ログファイル
実行ファイルと同じフォルダに `clipboard-transformer.log` が作成されます

## 🔧 再ビルド方法

開発版から再度exeを作成する場合：

```bash
# 仮想環境をアクティベート
source venv/Scripts/activate  # Linux/Mac
# または
.\venv\Scripts\activate  # Windows

# PyInstallerでビルド
pyinstaller clipboard-transformer.spec --clean
```

## 📝 ファイル構成

```
配置先フォルダ/
├── ClipboardTransformer.exe    # 実行ファイル
├── config.json                 # 設定ファイル（必須）
└── clipboard-transformer.log   # ログファイル（自動生成）
```
