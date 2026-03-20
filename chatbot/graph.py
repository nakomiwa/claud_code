"""
LangGraph チャットボットのグラフ定義

グラフ構造:
    START --> chat_node --> END

MessagesState を使ってメッセージ履歴を管理します。
add_messages reducer により、ノードが返す新しいメッセージは
リスト全体を上書きするのではなく、末尾に追記されます。
"""

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage
from langgraph.graph import StateGraph, MessagesState, START, END

from chatbot.config import MODEL_NAME, MAX_TOKENS, SYSTEM_PROMPT


def build_graph():
    """LangGraph の会話グラフを構築してコンパイルする。"""

    # 1. LLM インスタンスを作成
    llm = ChatAnthropic(model=MODEL_NAME, max_tokens=MAX_TOKENS)

    # 2. ノード関数を定義
    #    LangGraph は現在の State を引数で渡し、
    #    戻り値を State にマージ（上書きではなく追記）する
    def chat_node(state: MessagesState) -> dict:
        # 毎回 SystemMessage を先頭に付けてコンテキストを維持
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
        response = llm.invoke(messages)
        # {"messages": [response]} を返すと add_messages reducer が
        # 既存のメッセージリストの末尾に response を追記する
        return {"messages": [response]}

    # 3. グラフを組み立て
    builder = StateGraph(MessagesState)
    builder.add_node("chat_node", chat_node)
    builder.add_edge(START, "chat_node")
    builder.add_edge("chat_node", END)

    # 4. コンパイルして実行可能なグラフを返す
    return builder.compile()
