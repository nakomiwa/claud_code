# Databricks notebook source
# Workspace: https://adb-7405606053000173.13.azuredatabricks.net

# MAGIC %md
# MAGIC # LangGraph チャットボット on Databricks
# MAGIC
# MAGIC LangGraph と OpenAI (gpt-5-mini) を使ったチャットボットのデモです。
# MAGIC
# MAGIC ## 事前準備
# MAGIC Databricks Secret に OpenAI API キーを登録してください。
# MAGIC ```
# MAGIC databricks secrets create-scope --scope YOUR_SECRET_SCOPE
# MAGIC databricks secrets put --scope YOUR_SECRET_SCOPE --key openai-api-key
# MAGIC ```
# MAGIC 下の `DATABRICKS_SECRET_SCOPE` を実際のスコープ名に変更してください。

# COMMAND ----------

# MAGIC %pip install langgraph langchain-openai langchain-core
dbutils.library.restartPython()

# COMMAND ----------

import os
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, MessagesState, START, END

# COMMAND ----------

# MAGIC %md
# MAGIC ## 設定
# MAGIC `DATABRICKS_SECRET_SCOPE` を作成したスコープ名に変更してください。

# COMMAND ----------

# ---- 設定 ----
DATABRICKS_SECRET_SCOPE = "YOUR_SECRET_SCOPE"  # ← 変更してください
DATABRICKS_SECRET_KEY   = "openai-api-key"

MODEL_NAME    = "gpt-5-mini"
MAX_TOKENS    = 1024
SYSTEM_PROMPT = "あなたは親切なアシスタントです。簡潔でわかりやすい返答をしてください。"

# Databricks Secrets から OpenAI API キーを取得して環境変数に設定
os.environ["OPENAI_API_KEY"] = dbutils.secrets.get(
    scope=DATABRICKS_SECRET_SCOPE,
    key=DATABRICKS_SECRET_KEY
)
print("API キーを Databricks Secrets から取得しました。")

# COMMAND ----------

# MAGIC %md
# MAGIC ## LangGraph グラフの構築
# MAGIC
# MAGIC グラフ構造: `START → chat_node → END`
# MAGIC
# MAGIC `MessagesState` の `add_messages` reducer により、
# MAGIC ノードが返す新しいメッセージは履歴に**追記**されます（上書きではありません）。

# COMMAND ----------

def build_graph():
    """LangGraph の会話グラフを構築してコンパイルする。"""

    llm = ChatOpenAI(model=MODEL_NAME, max_tokens=MAX_TOKENS)

    def chat_node(state: MessagesState) -> dict:
        # 毎回 SystemMessage を先頭に付けてコンテキストを維持
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
        response = llm.invoke(messages)
        return {"messages": [response]}

    builder = StateGraph(MessagesState)
    builder.add_node("chat_node", chat_node)
    builder.add_edge(START, "chat_node")
    builder.add_edge("chat_node", END)

    return builder.compile()


graph = build_graph()
print("グラフを構築しました。")

# COMMAND ----------

# MAGIC %md
# MAGIC ## チャット関数
# MAGIC
# MAGIC `chat()` を呼び出すたびに会話履歴が蓄積されます。
# MAGIC `reset_conversation()` で履歴をリセットできます。

# COMMAND ----------

conversation = []

def chat(user_message: str) -> str:
    """
    ユーザーメッセージを送り、GPT-4o の返答を返す。
    会話履歴は自動的に蓄積される。
    """
    global conversation
    conversation.append(HumanMessage(content=user_message))
    result = graph.invoke({"messages": conversation})
    conversation = result["messages"]
    return result["messages"][-1].content

def reset_conversation():
    """会話履歴をリセットする。"""
    global conversation
    conversation = []
    print("会話履歴をリセットしました。")

def show_history():
    """現在の会話履歴を表示する。"""
    if not conversation:
        print("(まだメッセージはありません)")
        return
    for msg in conversation:
        role = "あなた" if isinstance(msg, HumanMessage) else "GPT-4o"
        print(f"[{role}] {msg.content}\n")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 実行例
# MAGIC
# MAGIC 以下のセルを編集して自由に試してください。

# COMMAND ----------

# 1回目の質問
response = chat("LangGraphとは何ですか？")
print(f"GPT-4o: {response}")

# COMMAND ----------

# 2回目（前の会話を踏まえた質問）
response = chat("一言でまとめると？")
print(f"GPT-4o: {response}")

# COMMAND ----------

# 会話履歴の確認
show_history()

# COMMAND ----------

# 会話履歴のリセット（新しいトピックを始める場合）
reset_conversation()
