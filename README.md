# Clipboard Transformer

Windows クリップボード変換常駐ソフト

Ctrl+V 押下時にクリップボードのテキストを設定ファイル (config.json) のルールに従って自動変換してから貼り付けます。

## 機能

- **literal 置換**: 固定文字列の置換
- **regex 置換**: 正規表現パターンマッチによる置換
- **ルールの連鎖適用**: 複数のルールを上から順に適用
- **個別ON/OFF**: 各ルールを個別に有効/無効化
- **システムトレイ常駐**: タスクトレイから機能の切り替えや設定の再読み込みが可能

## 必要要件

- Windows 10 以降
- Python 3.10 以降
- 管理者権限（グローバルキーフックのため）

## インストール

1. リポジトリをクローンまたはダウンロード

```bash
git clone <repository-url>
cd clipboard-transformer
```

2. 必要なパッケージをインストール

```bash
pip install -r requirements.txt
```

## 使い方

### 起動

**管理者権限**でコマンドプロンプトまたは PowerShell を開き、以下を実行：

```bash
python main.py
```

システムトレイに緑色の "CT" アイコンが表示されます。

### システムトレイメニュー

アイコンを右クリックすると以下のメニューが表示されます：

- **Enable/Disable Transformation**: 変換機能の ON/OFF 切り替え
- **Reload Config**: 設定ファイルを再読み込み
- **Quit**: アプリケーションを終了

### 設定ファイル (config.json)

`config.json` で変換ルールを定義します：

```json
{
  "enabled": true,
  "rules": [
    {
      "name": "example-literal",
      "type": "literal",
      "from": "旧文字列",
      "to": "新文字列",
      "enabled": true
    },
    {
      "name": "remove-dates",
      "type": "regex",
      "pattern": "\\d{4}-\\d{2}-\\d{2}",
      "replacement": "DATE_REMOVED",
      "enabled": true
    }
  ]
}
```

#### ルールの種類

##### literal タイプ

固定文字列の置換を行います。

```json
{
  "name": "replace-foo-with-bar",
  "type": "literal",
  "from": "foo",
  "to": "bar",
  "enabled": true
}
```

##### regex タイプ

正規表現によるパターンマッチと置換を行います。

```json
{
  "name": "remove-phone-numbers",
  "type": "regex",
  "pattern": "\\d{3}-\\d{4}-\\d{4}",
  "replacement": "[PHONE]",
  "enabled": true
}
```

正規表現の後方参照も使用できます：

```json
{
  "name": "swap-date-format",
  "type": "regex",
  "pattern": "(\\d{4})-(\\d{2})-(\\d{2})",
  "replacement": "\\3/\\2/\\1",
  "enabled": true
}
```

#### 設定のポイント

- **ルールの順序**: ルールは配列の上から順に適用されます
- **enabled フラグ**: 各ルールを個別に有効/無効化できます
- **トップレベルの enabled**: 全体の機能を ON/OFF します
- **設定の再読み込み**: システムトレイメニューから再起動不要で設定を反映できます

## 動作の仕組み

1. Ctrl+V を検知
2. クリップボードからテキストを取得
3. config.json のルールを順番に適用
4. 変換後のテキストをクリップボードにセット
5. Ctrl+V をシミュレートしてペースト

※ テキスト以外（画像等）のクリップボード内容はそのままペーストされます

## トラブルシューティング

### キーフックが動作しない

- **管理者権限で実行**していることを確認してください
- 一部のアプリケーション（セキュリティソフト等）がキーフックをブロックしている可能性があります

### 変換が実行されない

1. システムトレイアイコンを右クリックして機能が有効か確認
2. `config.json` の `enabled` が `true` になっているか確認
3. ルールの `enabled` が `true` になっているか確認
4. ログファイル (`clipboard-transformer.log`) でエラーを確認

### 正規表現エラー

- `pattern` に不正な正規表現が含まれている場合、そのルールはスキップされます
- ログファイルでエラー内容を確認してください

## ログ

アプリケーションの動作ログは `clipboard-transformer.log` に記録されます。

## exe 化（オプション）

PyInstaller を使用して実行ファイルを作成できます：

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --icon=icon.ico main.py
```

生成された `dist/main.exe` を**管理者権限**で実行してください。

## ライセンス

MIT License

## 免責事項

**本ソフトウェアは個人開発のプロジェクトです。使用する際は自己責任でご利用ください。**

- このソフトウェアの使用により発生したいかなる損害についても、開発者は一切の責任を負いません
- クリップボードの内容を変換・操作するため、重要なデータを扱う際は十分に注意してください
- 本番環境や業務での使用前に、十分なテストを行うことを強く推奨します
- サポートや保証は提供されません

## 注意事項

- このソフトウェアはグローバルキーフックを使用するため、管理者権限が必要です
- キーボード入力を監視するため、セキュリティソフトが警告を出す場合があります
- クリップボードの内容を自動的に変換するため、予期しない動作が発生する可能性があります
- 使用前に必ず `config.json` の設定内容を確認し、テスト環境で動作を検証してください
