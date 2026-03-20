"""
LangGraph チャットボットのグラフ定義

グラフ構造:
    START --> chat_node --> END

MessagesState を使ってメッセージ履歴を管理します。
add_messages reducer により、ノードが返す新しいメッセージは
リスト全体を上書きするのではなく、末尾に追記されます。
"""

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from langgraph.graph import StateGraph, MessagesState, START, END

from chatbot.config import MODEL_NAME, MAX_TOKENS, SYSTEM_PROMPT


def build_graph():
    """LangGraph の会話グラフを構築してコンパイルする。"""

    llm = ChatOpenAI(model=MODEL_NAME, max_tokens=MAX_TOKENS)

    def chat_node(state: MessagesState) -> dict:
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
        response = llm.invoke(messages)
        return {"messages": [response]}

    builder = StateGraph(MessagesState)
    builder.add_node("chat_node", chat_node)
    builder.add_edge(START, "chat_node")
    builder.add_edge("chat_node", END)

    return builder.compile()
