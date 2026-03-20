# LangGraph チャットボット

LangGraph と Claude (claude-sonnet-4-6) を使ったシンプルなチャットボットのサンプル実装です。

## 構成

```
.
├── main.py              # CLI エントリーポイント
├── chatbot/
│   ├── graph.py         # LangGraph グラフ定義（コア）
│   └── config.py        # モデル名・設定定数
├── requirements.txt
└── .env.example
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

## セットアップ

```bash
# 依存関係のインストール
pip install -r requirements.txt

# APIキーの設定
cp .env.example .env
# .env を編集して ANTHROPIC_API_KEY を設定
```

## 実行

```bash
python main.py
```

### 実行例

```
LangGraph チャットボット (claude-sonnet-4-6)
'quit' で終了、'history' で会話履歴を表示

あなた: LangGraphとは何ですか？
Claude: LangGraphはLangChain上に構築されたライブラリで、LLMを使った
        ステートフルなマルチアクターアプリケーションを構築するためのものです...

あなた: 一言でまとめると？
Claude: LLMワークフローをグラフとして定義し、状態管理を組み込んだライブラリです。

あなた: history
  [あなた] LangGraphとは何ですか？
  [Claude] LangGraphはLangChain上に...
  [あなた] 一言でまとめると？
  [Claude] LLMワークフローをグラフとして...

あなた: quit
さようなら！
```

## 次のステップ

- `MemorySaver` チェックポインターを追加して LangGraph にステート管理を任せる
- `add_conditional_edges` で複数ノード間の条件分岐を実装する
- `graph.stream()` でトークンごとのストリーミング出力に対応する
- ツール（Web検索、計算など）を追加して ReAct エージェントに発展させる
