# LangGraph チャットボット

LangGraph と Claude (claude-sonnet-4-6) を使ったシンプルなチャットボットのサンプル実装です。

## 構成

```
.
├── databricks_notebook.py   # Databricks Notebook 用（メイン）
├── main.py                  # ローカル CLI 用
├── chatbot/
│   ├── graph.py             # LangGraph グラフ定義（コア）
│   └── config.py            # モデル名・設定定数
├── requirements.txt         # ローカル実行用の依存関係
└── .env.example             # ローカル実行用 APIキーテンプレート
```

## LangGraph の主要概念

| 概念 | 説明 |
|---|---|
| `MessagesState` | メッセージリストを状態として管理。`add_messages` reducer により新メッセージは追記される |
| `StateGraph` | グラフビルダー。ノードとエッジを定義してからコンパイルする |
| `START` / `END` | グラフの入口・出口を示すセンチネルノード |
| `add_edge` | 静的（無条件）なノード間接続 |
| `.invoke()` | グラフを同期実行し、最終状態の dict を返す |

### グラフ構造

```
START --> chat_node --> END
```

---

## Databricks での実行（推奨）

### 1. Databricks Secret に API キーを登録

Databricks CLI から実行するか、UI の Secret Management で設定します。

```bash
# スコープの作成（初回のみ）
databricks secrets create-scope --scope YOUR_SECRET_SCOPE

# Anthropic API キーの登録
databricks secrets put --scope YOUR_SECRET_SCOPE --key anthropic-api-key
```

### 2. Notebook のインポート

`databricks_notebook.py` を Databricks Workspace にインポートします。

- Workspace → Import → `databricks_notebook.py` をアップロード
- または Repos を使って Git リポジトリをそのままクローン

### 3. スコープ名の設定

Notebook の設定セルの `DATABRICKS_SECRET_SCOPE` を実際のスコープ名に変更します。

```python
DATABRICKS_SECRET_SCOPE = "YOUR_SECRET_SCOPE"  # ← 変更
```

### 4. クラスターにアタッチして実行

クラスターをアタッチし、上から順にセルを実行します。
`%pip install` セルが依存関係を自動インストールします。

### 使い方（Notebook内）

```python
# メッセージを送る
response = chat("LangGraphとは何ですか？")
print(response)

# 会話履歴を表示
show_history()

# 履歴をリセット
reset_conversation()
```

---

## ローカルでの実行

```bash
pip install -r requirements.txt
cp .env.example .env
# .env を編集して ANTHROPIC_API_KEY を設定
python main.py
```

---

## 次のステップ

- `MemorySaver` チェックポインターを追加して LangGraph にステート管理を任せる
- `add_conditional_edges` で複数ノード間の条件分岐を実装する
- `graph.stream()` でトークンごとのストリーミング出力に対応する
- ツール（Web検索、計算など）を追加して ReAct エージェントに発展させる
